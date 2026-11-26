"""Hosted publication and Hand Back for a native SQLite session."""

import base64
from datetime import datetime, timedelta, timezone
import hashlib
import http.client
import json
import os
import re
import socket
import ssl
import stat
import struct
from urllib.parse import urlsplit
import zlib

from review_store import ArchiveConflict, UNBOUND_HOSTED

IDENTIFIER = re.compile(r"[a-z0-9][a-z0-9_-]{0,63}")
ITEM_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,95}")
LOGIN = re.compile(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+")
REVIEW_ID = re.compile(r"[a-f0-9]{32}")
DIGEST = re.compile(r"[a-f0-9]{64}")
PRIVATE_TEXT = re.compile(r'(?i)#token(?:=|%3d)|(?:^|[\s("=\x27])(?:file:|~[/\\]|[A-Z]:[/\\]|\\\\|/[\w.~-])')
MAX_MANIFEST = 2 * 1024 * 1024
MAX_ASSET = 8 * 1024 * 1024
MAX_PACKAGE = 128 * 1024 * 1024
MAX_SNAPSHOT = 24 * 1024 * 1024
TOKEN_ENV = "ATTENDED_REVIEW_HOSTED_TOKEN"
FIXTURE_CONNECT = "ATTENDED_REVIEW_HOSTED_FIXTURE_CONNECT"
PROJECT_CONFIG = ".mask/skill-config/attended-review/project.json"
PROJECT_SCHEMA = "attended-review.project.v1"
PROJECT_CONFIG_LIMIT = 64 * 1024
ROUTE_FIELDS = ("origin", "project", "owner", "installation")
PACKAGE_TABLE = """
CREATE TABLE hosted_package (
    singleton INTEGER PRIMARY KEY CHECK (singleton=1),
    origin TEXT NOT NULL, manifest BLOB NOT NULL, revision TEXT NOT NULL,
    review TEXT, committed INTEGER NOT NULL DEFAULT 0,
    delivery TEXT, digest TEXT, export_sequence INTEGER, acknowledged INTEGER NOT NULL DEFAULT 0
)
"""
MEDIA_TABLE = "CREATE TABLE hosted_assets (digest TEXT PRIMARY KEY, content BLOB NOT NULL)"


class HostedError(ValueError):
    pass


class NeedsAttention(HostedError):
    pass


def matches(pattern, value):
    return isinstance(value, str) and pattern.fullmatch(value) is not None


def sha256(value):
    return hashlib.sha256(value).hexdigest()


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def document(raw):
    def unique(pairs):
        result = dict(pairs)
        if len(pairs) != len(result):
            raise ValueError
        return result

    def invalid_constant(_):
        raise ValueError

    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=unique, parse_constant=invalid_constant)
    except (ValueError, RecursionError):
        raise HostedError("Invalid hosted JSON response") from None


def fields(value, required):
    return isinstance(value, dict) and value.keys() == required


def valid_owner(value):
    return matches(LOGIN, value) and len(value) <= 254


def hosted_defaults(root, origin_validator):
    """Read project defaults from the selected checkout. An absent file selects legacy."""
    config = root / PROJECT_CONFIG
    try:
        path = config.resolve()
        if not path.is_relative_to(root):
            raise HostedError("Attended review project config must resolve inside the checkout")
        if not stat.S_ISREG(path.stat().st_mode):
            raise HostedError("Attended review project config must be a regular file")
        with path.open("rb") as stream:
            raw = stream.read(PROJECT_CONFIG_LIMIT + 1)
    except FileNotFoundError:
        if config.is_symlink():
            raise HostedError("Attended review project config link has no target") from None
        return {}
    except (OSError, RuntimeError):
        raise HostedError("Cannot read attended review project config") from None

    if len(raw) > PROJECT_CONFIG_LIMIT:
        raise HostedError("Attended review project config exceeds 64 KiB")
    try:
        settings = document(raw)
    except HostedError:
        raise HostedError("Attended review project config must be valid JSON with unique keys") from None

    if isinstance(settings, dict) and settings.get("schema") == PROJECT_SCHEMA:
        if fields(settings, {"schema", "mode"}) and settings["mode"] == "legacy":
            return {}
        if fields(settings, {"schema", "mode", "hosted"}) and settings["mode"] == "hosted":
            return hosted_route(settings["hosted"], origin_validator)
    raise HostedError("Invalid attended review project config schema or mode")


def hosted_route(route, origin_validator):
    required = {"origin", "project", "owner"}
    if (not isinstance(route, dict) or not required <= route.keys() <= set(ROUTE_FIELDS)
            or not matches(IDENTIFIER, route["project"]) or not valid_owner(route["owner"])
            or ("installation" in route and not matches(IDENTIFIER, route["installation"]))):
        raise HostedError("Invalid hosted project config routing fields")
    try:
        return {**route, "origin": origin_validator(route["origin"])}
    except ValueError:
        raise HostedError("Hosted project config origin must be a Tailscale Serve HTTPS producer origin") from None


def describe_project(root, origin_validator):
    if not root.is_dir():
        raise HostedError("checkout root must exist")
    route = hosted_defaults(root, origin_validator)
    return {"mode": "hosted" if route else "legacy", "hosted": route or None,
            "path": str(root / PROJECT_CONFIG)}


def publication_route(root, args, origin_validator):
    explicit = {field: value for field, value in vars(args).items() if field in ROUTE_FIELDS and value is not None}
    if "origin" in explicit:
        explicit["origin"] = origin_validator(explicit["origin"])
    if len(explicit) == len(ROUTE_FIELDS):
        route = explicit
    else:
        defaults = hosted_defaults(root, origin_validator)
        if any(field in defaults and defaults[field] != value for field, value in explicit.items()):
            raise HostedError("Partial routing flags must match the project config; supply all four routing flags to override it")
        route = {**defaults, **explicit}
    if (route.keys() != set(ROUTE_FIELDS) or not matches(IDENTIFIER, route["project"])
            or not matches(IDENTIFIER, route["installation"]) or not valid_owner(route["owner"])):
        raise HostedError("First publication needs --origin, --project, --installation and --owner or project defaults")
    return route


def display_text(value, limit, *, empty=False):
    if (not isinstance(value, str) or len(value) > limit or (not empty and not value.strip())
            or PRIVATE_TEXT.search(value)
            or any((ord(c) < 32 and c not in "\n\t") or 0xD800 <= ord(c) <= 0xDFFF for c in value)):
        raise HostedError("Hosted display text is invalid or contains a private path or capability")
    return value


def valid_png(data):
    """Accept only static PNG scanlines and the hub's non-text ancillary chunks."""
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        return False
    channels = {0: 1, 2: 3, 4: 2, 6: 4}
    ancillary = {(b"sRGB", 1), (b"gAMA", 4), (b"pHYs", 9), (b"cHRM", 32)}
    position = 8
    stream = None
    pixels = bytearray()
    while position + 12 <= len(data):
        size, kind = struct.unpack_from(">I4s", data, position)
        end = position + 8 + size
        if end + 4 > len(data):
            return False
        chunk = memoryview(data)[position + 8:end]
        if zlib.crc32(chunk, zlib.crc32(kind)) != struct.unpack_from(">I", data, end)[0]:
            return False
        if position == 8:
            if kind != b"IHDR" or size != 13:
                return False
            width, height, depth, color, compression, filtering, interlace = struct.unpack(">IIBBBBB", chunk)
            if not (1 <= width <= 4096 and 1 <= height <= 4096 and depth == 8 and
                    color in channels and (compression, filtering, interlace) == (0, 0, 0)):
                return False
            row = 1 + width * channels[color]
            limit = row * height
            if limit > 16 * 1024 * 1024:
                return False
        elif kind == b"IDAT":
            stream = stream or zlib.decompressobj()
            try:
                pixels.extend(stream.decompress(chunk, limit + 1 - len(pixels)))
            except zlib.error:
                return False
            if len(pixels) > limit or stream.unused_data or stream.unconsumed_tail:
                return False
        elif kind == b"IEND":
            return (size == 0 and end + 4 == len(data) and stream is not None and stream.eof
                    and len(pixels) == limit and all(pixel <= 4 for pixel in pixels[::row]))
        elif stream is not None or (kind, size) not in ancillary:
            return False
        position = end + 4
    return False


def valid_wav(data):
    if len(data) < 46 or data[:4] != b"RIFF" or data[8:20] != b"WAVEfmt \x10\x00\x00\x00" or data[36:40] != b"data":
        return False
    length, = struct.unpack_from("<I", data, 4)
    encoding, channels, rate, byte_rate, align, bits = struct.unpack_from("<HHIIHH", data, 20)
    size, = struct.unpack_from("<I", data, 40)
    return (length == len(data) - 8 and encoding == 1 and channels in (1, 2)
            and 8000 <= rate <= 96000 and bits in (8, 16, 24, 32)
            and align == channels * (bits // 8) and byte_rate == rate * align
            and size > 0 and size % align == 0 and 44 + size + size % 2 == len(data))


def package_media(item, assets):
    reference = item.get("reference")
    media = [*item.get("media", []), *item.get("now", []), *(reference if isinstance(reference, list) else [])]
    if item.get("audio"):
        media.append({"url": item["audio"]["url"], "label": "Audio excerpt"})
    if len(media) > 8:
        raise HostedError("A hosted item supports at most eight media references")
    validators = {"data:image/png;base64": ("image/png", valid_png), "data:audio/wav;base64": ("audio/wav", valid_wav)}
    result = []
    for medium in media:
        prefix, _, data = medium["url"].partition(",")
        if prefix not in validators or len(data) > (MAX_ASSET + 2) // 3 * 4:
            raise HostedError("Hosted media must be bounded inline PNG or PCM WAV")
        mime, validate = validators[prefix]
        try:
            content = base64.b64decode(data, validate=True)
        except ValueError:
            raise HostedError("Invalid base64 in hosted media") from None
        if len(content) > MAX_ASSET or not validate(content):
            raise HostedError("Invalid hosted PNG or WAV, or the asset contains metadata")
        digest = sha256(content)
        assets[digest] = (mime, content)
        label = medium.get("label") or ("Image" if mime == "image/png" else "Audio")
        if medium.get("option"):
            label = f"{medium['option']} — {label}"
        result.append({"sha256": digest, "label": display_text(label, 120)})
    return result


def package_links(item):
    links = item.get("links", [])
    if len(links) > 8:
        raise HostedError("A hosted item supports at most eight links")
    for link in links:
        display_text(link["label"], 120)
        raw = link["url"]
        if not raw.isascii() or len(raw) > 2048 or re.search(r"[\x00-\x20\x7f\\#?]", raw):
            raise HostedError("Hosted links must use HTTPS without credentials, queries or fragments")
        try:
            url = urlsplit(raw)
            valid = url.scheme == "https" and url.hostname and url.username is None and url.port != 0
        except ValueError:
            valid = False
        if not valid:
            raise HostedError("Hosted links must use HTTPS without credentials, queries or fragments")
    return links


def package_item(item, args, assets):
    criteria, options = item["criteria"], item.get("options")
    if not 1 <= len(criteria) <= 12 or (options is not None and not 2 <= len(options) <= 16):
        raise HostedError("Hosted items need 1–12 criteria and selection items need 2–16 options")
    result = {"id": item["id"], "fingerprint": item["fingerprint"], "title": display_text(item["title"], 200),
              "type": "verdict" if options is None else "selection",
              "criteria": [display_text(text, 500) for text in criteria]}
    if options is not None:
        result["options"] = [display_text(text, 120) for text in options]
    audio = item.get("audio", {})
    text = "\n\n".join([item[key] for key in ("content", "why", "document", "note") if item.get(key)]
                       + [audio[key] for key in ("purpose", "scope", "context", "listen_for", "reject_if", "variant") if audio.get(key)])
    if text:
        result["text"] = display_text(text, 8000)
    if args.include_media:
        media = package_media(item, assets)
        if media:
            result["media"] = media
    if args.include_links:
        links = package_links(item)
        if links:
            result["links"] = links
    return result


def prepared_item(session, db, ident, canonical, fingerprint=None):
    row = db.execute("SELECT body, media FROM cards WHERE id=?", (ident,)).fetchone()
    if row is not None:
        item = session.store.card(db, *row)
        if (item["phase"] == "ready" and item.get("protected") and not item.get("decision")
                and item["fingerprint"] == canonical(item)
                and (fingerprint is None or item["fingerprint"] == fingerprint)):
            return item
    raise NeedsAttention("A hosted item is missing, changed, unprotected or already decided")


def binding(db):
    row = db.execute("""SELECT origin, manifest, revision, review, committed, delivery, digest,
                      export_sequence FROM hosted_package WHERE singleton=1""").fetchone()
    origin, raw, revision, review, committed, delivery, digest, sequence = row
    if sha256(raw) != revision:
        raise HostedError("Stored hosted manifest digest is inconsistent")
    manifest = json.loads(raw)
    return {"origin": origin, "raw": raw, "manifest": manifest, "revision": revision, "review": review,
            "committed": bool(committed), "delivery": delivery, "digest": digest, "sequence": sequence}


def require_hosted(header):
    if not header.get("hosted"):
        raise HostedError("Hosted commands require a new SQLite session initialized in hosted mode")
    if "hosted_directory" not in header:
        raise HostedError(UNBOUND_HOSTED)


def load_binding(session):
    with session.store.connection() as db:
        header = session.store.header(db)
        require_hosted(header)
        if not header.get("hosted_bound"):
            raise HostedError("Create the package with hosted-publish first")
        return binding(db)


def create_package(session, args, origin_validator, canonical, token):
    selection = args.candidate
    with session.store.connection(writer=True) as db:
        header = session.store.header(db)
        require_hosted(header)
        if header.get("hosted_bound"):
            raise HostedError("Hosted package already exists; repeat hosted-publish without selection or enrollment flags")
        if not args.title or not selection:
            raise HostedError("First publication needs an explicit --title and --candidate selection")
        if len(selection) > 1000 or len(set(selection)) != len(selection) or not all(ITEM_ID.fullmatch(cid) for cid in selection):
            raise HostedError("Hosted publication needs 1–1000 distinct protocol item IDs")
        route = publication_route(session.root, args, origin_validator)
        title = display_text(args.title, 200)
        assets = {}
        items = []
        for cid in selection:
            item = prepared_item(session, db, cid, canonical)
            items.append(package_item(item, args, assets))
            if len(assets) > 1000 or sum(len(data) for _, data in assets.values()) > MAX_PACKAGE:
                raise HostedError("Hosted package exceeds its total media bound")
        media = [{"sha256": digest, "type": mime, "bytes": len(content)} for digest, (mime, content) in assets.items()]
        manifest = {"schema": "attended-review.hosted-package.v1", "mode": "hosted", "owner": route["owner"],
                    "title": title, "items": items, "media": media,
                    "origin": {"project": route["project"], "installation": route["installation"], "session": header["id"]}}
        raw = encode(manifest)
        if token.encode("ascii") in raw:
            raise HostedError("Hosted package contains the producer credential")
        if len(raw) > MAX_MANIFEST or len(raw) + sum(asset["bytes"] for asset in media) > MAX_PACKAGE:
            raise HostedError("Hosted manifest or package exceeds its byte limit")
        db.execute(PACKAGE_TABLE)
        db.execute(MEDIA_TABLE)
        db.execute("INSERT INTO hosted_package (singleton, origin, manifest, revision) VALUES (1, ?, ?, ?)",
                   (route["origin"], raw, sha256(raw)))
        db.executemany("INSERT INTO hosted_assets VALUES (?, ?)", ((digest, pair[1]) for digest, pair in assets.items()))
        session.store.write_header(db, {**header, "hosted_bound": True})
        return binding(db)


class Transport:
    """Direct HTTPS to the saved authority. Errors expose only a status or cause category."""

    def __init__(self, current, token, origin_validator):
        self.origin = urlsplit(origin_validator(current["origin"]))
        self.token = token
        self.revision = current["revision"]
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.context.load_default_certs()
        self.path = "/api/producer/projects/{project}/installations/{installation}/reviews/{session}".format(
            **current["manifest"]["origin"])
        self.fixture_port = None
        fixture = os.environ.get(FIXTURE_CONNECT)
        if fixture is not None:
            match = re.fullmatch(r"127\.0\.0\.1:([0-9]{1,5})", fixture)
            if not match or not 1 <= int(match[1]) <= 65535:
                raise HostedError("Hosted fixture connector requires a loopback port")
            self.fixture_port = int(match[1])

    def connect(self, address, timeout, source_address):
        if self.fixture_port is not None:
            address = ("127.0.0.1", self.fixture_port)
        return socket.create_connection(address, timeout, source_address)

    def request(self, method, suffix, expected, body=None, mime=None, limit=4096):
        connection = http.client.HTTPSConnection(self.origin.hostname, self.origin.port, context=self.context, timeout=10)
        connection._create_connection = self.connect
        try:
            headers = {"Authorization": "Bearer " + self.token, "X-Hosted-Revision": self.revision}
            if body is not None:
                headers["Content-Length"] = str(len(body))
            if mime is not None:
                headers["Content-Type"] = mime
            connection.request(method, self.path + suffix, body=body, headers=headers)
            with connection.getresponse() as response:
                if response.status not in expected:
                    if 300 <= response.status < 400:
                        raise HostedError(f"Hosted redirect refused (HTTP {response.status})")
                    raise HostedError(f"Hosted hub returned HTTP {response.status}")
                if response.status == 204:
                    return None
                raw = response.read(limit + 1)
                if len(raw) > limit:
                    raise HostedError("Hosted response exceeds its byte limit")
                return document(raw)
        except ssl.SSLCertVerificationError:
            raise HostedError("Hosted certificate verification failed") from None
        except (OSError, http.client.HTTPException):
            raise HostedError("Hosted HTTPS request failed; retry from the saved session") from None
        finally:
            connection.close()


def save_publication(session, receipt, revision, allowed_state):
    if (not fields(receipt, {"review", "revision", "state"}) or not matches(REVIEW_ID, receipt["review"])
            or receipt["revision"] != revision or not isinstance(receipt["state"], str)
            or receipt["state"] not in allowed_state):
        raise HostedError("Hosted publication receipt does not match the saved revision")
    with session.store.connection(writer=True) as db:
        require_hosted(session.store.header(db))
        current = binding(db)
        if current["review"] not in (None, receipt["review"]) or current["revision"] != revision:
            raise HostedError("Hosted publication receipt conflicts with the saved binding")
        db.execute("UPDATE hosted_package SET review=?, committed=? WHERE singleton=1",
                   (receipt["review"], current["committed"] or receipt["state"] == "committed"))


def publish(session, current, transport):
    if current["committed"]:
        return {"state": "committed", "review": current["review"], "revision": current["revision"]}
    revision = current["revision"]
    receipt = transport.request("PUT", "", {200}, current["raw"], "application/json")
    save_publication(session, receipt, revision, {"staged", "committed"})
    if receipt["state"] == "staged":
        for asset in current["manifest"]["media"]:
            digest = asset["sha256"]
            with session.store.connection() as db:
                row = db.execute("SELECT content FROM hosted_assets WHERE digest=?", (digest,)).fetchone()
            if row is None or len(row[0]) != asset["bytes"] or sha256(row[0]) != digest:
                raise HostedError("Stored hosted media is missing or changed")
            transport.request("PUT", "/media/" + digest, {204}, row[0], asset["type"])
        receipt = transport.request("POST", "/commit", {200}, b"")
        save_publication(session, receipt, revision, {"committed"})
    return receipt


def timestamp(value):
    try:
        if type(value) is int and value >= 0:
            return (datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(milliseconds=value)).isoformat()
    except OverflowError:
        pass
    raise HostedError("Invalid hosted decision or Hand Back timestamp")


def validate_snapshot(envelope, current):
    problem = HostedError("Hosted Hand Back snapshot does not match its digest, schema or saved binding")
    if not fields(envelope, {"digest", "snapshot"}) or not matches(DIGEST, envelope["digest"]):
        raise problem
    snapshot = envelope["snapshot"]
    if not isinstance(snapshot, dict):
        raise problem
    required = {"schema", "delivery", "target", "handed_back_at", "items"}
    schema = snapshot.get("schema")
    collaborators = set()
    if schema in ("attended-review.hosted-handback.v2", "attended-review.hosted-handback.v3"):
        required.add("handed_back_by")
        if not matches(LOGIN, snapshot.get("handed_back_by")) or len(snapshot["handed_back_by"]) > 254:
            raise problem
    elif schema != "attended-review.hosted-handback.v1":
        raise problem
    if schema == "attended-review.hosted-handback.v3":
        required.add("contributors")
        names = snapshot.get("contributors")
        if not isinstance(names, list) or not names or len(names) > 1000 or any(
                not matches(LOGIN, name) or len(name) > 254 for name in names):
            raise problem
        if names != sorted(set(names)):
            raise problem
        collaborators = set(names)
    if not fields(snapshot, required):
        raise problem
    target = {**current["manifest"]["origin"], "review": current["review"], "revision": current["revision"]}
    try:
        digest_ok = sha256(encode(snapshot)) == envelope["digest"]
    except (ValueError, RecursionError):
        digest_ok = False
    if (snapshot["target"] != target
            or not matches(REVIEW_ID, snapshot["delivery"]) or not digest_ok):
        raise problem
    timestamp(snapshot["handed_back_at"])
    published = current["manifest"]["items"]
    items = snapshot["items"]
    if not isinstance(items, list) or len(items) != len(published):
        raise problem
    actors = {current["manifest"]["owner"], snapshot.get("handed_back_by", current["manifest"]["owner"])}
    if collaborators & actors:
        raise problem
    used = set()
    for item, original in zip(items, published):
        if (not fields(item, {"id", "fingerprint", "version", "decision"})
                or any(item[key] != original[key] for key in ("id", "fingerprint"))
                or type(item["version"]) is not int or item["version"] < 0):
            raise problem
        decision = item["decision"]
        if decision is not None:
            validate_decision(decision, original, actors | collaborators, item["version"])
            used.add(decision["actor"])
    if used - actors != collaborators:
        raise problem
    return snapshot


def validate_decision(decision, original, actors, version):
    problem = HostedError("Invalid final decision in hosted Hand Back")
    if not isinstance(decision, dict) or not version:
        raise problem
    outcome = decision.get("outcome")
    expected = {"actor", "at", "note", "outcome"}
    if outcome == "select":
        expected.add("selected")
        selected = decision.get("selected")
        options = original.get("options", [])
        if (not isinstance(selected, list) or not selected or any(value not in options for value in selected)
                or len(set(selected)) != len(selected)):
            raise problem
    elif not (outcome == "reject" or outcome == "accept" and original["type"] == "verdict"):
        raise problem
    if not fields(decision, expected) or not isinstance(decision["actor"], str) or decision["actor"] not in actors:
        raise problem
    timestamp(decision["at"])
    display_text(decision["note"], 2000, empty=True)


def stage_delivery(session, current, snapshot, digest, canonical):
    delivery = snapshot["delivery"]
    at = timestamp(snapshot["handed_back_at"])
    with session.store.connection(writer=True) as db:
        require_hosted(session.store.header(db))
        latest = binding(db)
        if latest["delivery"]:
            if (latest["delivery"], latest["digest"]) != (delivery, digest):
                raise NeedsAttention("A different hosted delivery is already recorded for this session")
            return latest["sequence"]
        if (latest["review"], latest["revision"]) != (current["review"], current["revision"]):
            raise NeedsAttention("Hosted publication binding changed")
        with session.store.editing(db) as state:
            require_hosted(state)
            if state.get("handed_back") or state["id"] != snapshot["target"]["session"]:
                raise NeedsAttention("Local Hand Back state conflicts with the hosted delivery")
            session.upgrade(state)
            for record in snapshot["items"]:
                prepared_item(session, db, record["id"], canonical, record["fingerprint"])
                if record["decision"] is None:
                    continue
                item = state["candidates"][record["id"]]
                decision = record["decision"]
                clean = {key: decision[key] for key in ("outcome", "note", "selected") if key in decision}
                clean.update(candidate=item["id"], fingerprint=record["fingerprint"], decision_id=f"hosted:{delivery}:{item['id']}",
                             attachments=(item.get("feedback") or {}).get("attachments", []))
                session.save_decision(state, item, clean, at=timestamp(decision["at"]), actor=decision["actor"])
            state["handed_back"] = at
            attribution = {"actor": snapshot["handed_back_by"]} if "handed_back_by" in snapshot else {}
            session.event(state, "handed-back", at=at, **attribution)
            sequence = state["sequence"]
        header = session.store.header(db)
        if os.path.lexists(session.path):
            # The database may have been restored to before this delivery.
            # Compare the exact projected archive while changes can roll back.
            session.store.verify_staged_archive(db, session.path, header)
        session.store.queue_archive(db, header)
        db.execute("UPDATE hosted_package SET delivery=?, digest=?, export_sequence=? WHERE singleton=1",
                   (delivery, digest, sequence))
        return sequence


def poll(session, current, transport, canonical):
    if not current["committed"]:
        raise HostedError("Complete hosted-publish before polling for Hand Back")
    path = "/handback/" + current["review"]
    if current["delivery"]:
        receipt = {"delivery": current["delivery"], "digest": current["digest"]}
        sequence = current["sequence"]
    else:
        envelope = transport.request("GET", path, {200, 204}, limit=MAX_SNAPSHOT)
        if envelope is None:
            latest = load_binding(session)
            if not latest["delivery"]:
                return {"state": "waiting"}
            return poll(session, latest, transport, canonical)
        snapshot = validate_snapshot(envelope, current)
        receipt = {"delivery": snapshot["delivery"], "digest": envelope["digest"]}
        try:
            sequence = stage_delivery(session, current, snapshot, envelope["digest"], canonical)
        except (NeedsAttention, ArchiveConflict):
            transport.request("PUT", path + "/attention", {204}, encode(receipt), "application/json")
            raise
    try:
        session.export(sequence)
    except ArchiveConflict as error:
        transport.request("PUT", path + "/attention", {204}, encode(receipt), "application/json")
        raise NeedsAttention(str(error)) from None
    # A restored hub can have forgotten an ACK. Confirm this exact delivery
    # against the current hub after the local archive is durable.
    transport.request("PUT", path + "/ack", {204}, encode(receipt), "application/json")
    with session.store.connection(writer=True) as db:
        require_hosted(session.store.header(db))
        db.execute("UPDATE hosted_package SET acknowledged=1 WHERE singleton=1 AND delivery=? AND digest=?",
                   (receipt["delivery"], receipt["digest"]))
    return {"state": "delivered", "delivery": receipt["delivery"], "sequence": sequence}


def add_commands(sub):
    parser = sub.add_parser("hosted-publish", help="Freeze selected prepared material and publish it to the hosted hub")
    parser.add_argument("--origin", help="Producer Tailscale Serve HTTPS origin")
    parser.add_argument("--project", help="Enrolled project slug")
    parser.add_argument("--installation", help="Enrolled installation slug")
    parser.add_argument("--owner", help="Review owner login on the collaboration origin")
    parser.add_argument("--title", help="Title to display in the hosted review")
    parser.add_argument("--candidate", action="append", help="Prepared candidate ID to publish, repeatable in review order")
    parser.add_argument("--include-media", action="store_true", help="Include the selected candidates' supported inline media")
    parser.add_argument("--include-links", action="store_true", help="Include the selected candidates' safe HTTPS links")
    sub.add_parser("hosted-poll", help="Receive and durably apply a frozen hosted Hand Back")


def run(session, args, origin_validator, canonical):
    if not session.indexed:
        raise HostedError("Hosted commands require a new SQLite session initialized in hosted mode")
    token = os.environ.get(TOKEN_ENV, "")
    if not re.fullmatch(r"[A-Za-z0-9_-]{43}", token):
        raise HostedError(f"Set {TOKEN_ENV} to the enrolled producer credential")
    publishing = args.command == "hosted-publish"
    if publishing and (any(value is not None for value in (args.origin, args.project, args.installation, args.owner,
                                                           args.title, args.candidate))
                       or args.include_media or args.include_links):
        current = create_package(session, args, origin_validator, canonical, token)
    else:
        current = load_binding(session)
    transport = Transport(current, token, origin_validator)
    return publish(session, current, transport) if publishing else poll(session, current, transport, canonical)
