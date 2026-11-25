"""Indexed attended-review state. Published JSON is an archive, never active state."""

from collections.abc import MutableMapping
from contextlib import contextmanager, nullcontext
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import stat
import tempfile


DATABASE = "session.sqlite3"
HOSTED_DB_VERSION = 3
MATERIAL = ("media", "audio", "now", "reference")
HISTORY = ("decision_history", "feedback_history", "superseded")
SUMMARY = ("id", "title", "revision", "fingerprint", "phase", "protected",
           "decision", "feedback", "playback_errors")
SCHEMA = """
CREATE TABLE IF NOT EXISTS metadata (singleton INTEGER PRIMARY KEY CHECK (singleton=1), payload TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS commits (sequence INTEGER PRIMARY KEY, header TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS material (digest TEXT PRIMARY KEY, payload TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS cards (
    id TEXT PRIMARY KEY, position INTEGER NOT NULL UNIQUE, sequence INTEGER NOT NULL,
    body TEXT NOT NULL, media TEXT REFERENCES material(digest), media_keys TEXT NOT NULL,
    summary TEXT NOT NULL, page TEXT NOT NULL, ready INTEGER NOT NULL, answered INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS versions (
    id TEXT NOT NULL, sequence INTEGER NOT NULL, body TEXT NOT NULL,
    media TEXT REFERENCES material(digest), summary TEXT NOT NULL, page TEXT NOT NULL,
    ready INTEGER NOT NULL, answered INTEGER NOT NULL,
    PRIMARY KEY (id, sequence)
);
CREATE INDEX IF NOT EXISTS changes_by_sequence ON versions (sequence, id);
CREATE TABLE IF NOT EXISTS history (
    position INTEGER PRIMARY KEY, sequence INTEGER NOT NULL,
    body TEXT NOT NULL, media TEXT REFERENCES material(digest)
);
CREATE TABLE IF NOT EXISTS events (sequence INTEGER PRIMARY KEY, kind TEXT NOT NULL, body TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS events_by_kind ON events (kind, sequence);
CREATE TABLE IF NOT EXISTS exports (sequence INTEGER PRIMARY KEY, header TEXT NOT NULL, receipt TEXT);
CREATE INDEX IF NOT EXISTS pending_exports ON exports (sequence) WHERE receipt IS NULL;
"""


class ArchiveConflict(ValueError):
    pass


def pack(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def summary(item):
    record = {key: item.get(key) for key in SUMMARY}
    for key in ("superseded", "error"):
        if item.get(key):
            record[key] = item[key]
    return record


class Cards(MutableMapping):
    """Read candidates on demand and persist changed records at the commit cursor."""

    def __init__(self, db):
        self.db = db
        self.items = {}
        self.original = {}
        self.replaced = set()

    def __getitem__(self, key):
        if key not in self.items:
            row = self.db.execute("SELECT body, media, media_keys FROM cards WHERE id=?", (key,)).fetchone()
            if row is None:
                raise KeyError(key)
            self.original[key] = row
            self.items[key] = json.loads(row[0])
        return self.items[key]

    def __setitem__(self, key, value):
        self.items[key] = value
        self.replaced.add(key)

    def __delitem__(self, key):
        raise TypeError("published candidate identities are retained")

    def __iter__(self):
        yield from (row[0] for row in self.db.execute("SELECT id FROM cards ORDER BY position"))
        yield from (key for key in self.items if key not in self.original)

    def __len__(self):
        return self.db.execute("SELECT count(*) FROM cards").fetchone()[0] + len(self.items.keys() - self.original.keys())

    def write(self, sequence):
        for key, item in self.items.items():
            original = self.original.get(key, (None, None, "[]"))
            _, media, media_keys = original if key not in self.replaced else (None, None, "[]")
            material = {field: item[field] for field in MATERIAL if field in item}
            if material:
                payload = pack(material)
                media = hashlib.sha256(payload.encode()).hexdigest()
                media_keys = pack(list(material))
                self.db.execute("INSERT OR IGNORE INTO material VALUES (?,?)", (media, payload))
            active = {field: value for field, value in item.items() if field not in MATERIAL}
            body = pack(active)
            if (body, media, media_keys) == original:
                continue
            projected = pack(summary(item))
            page = {field: value for field, value in active.items() if field not in HISTORY}
            if media is not None:
                page.update(media_lazy=True, material_omitted=json.loads(media_keys))
            ready = int(item["phase"] == "ready" and bool(item.get("protected")) and not item.get("decision"))
            answered = int(bool(item.get("decision")))
            view = pack(page)
            self.db.execute("""
                INSERT INTO cards VALUES (?,coalesce((SELECT max(position)+1 FROM cards),0),?,?,?,?,?,?,?,?)
                ON CONFLICT(id) DO UPDATE SET sequence=excluded.sequence, body=excluded.body,
                    media=excluded.media, media_keys=excluded.media_keys, summary=excluded.summary,
                    page=excluded.page, ready=excluded.ready, answered=excluded.answered
            """, (key, sequence, body, media, media_keys, projected, view, ready, answered))
            self.db.execute("INSERT INTO versions VALUES (?,?,?,?,?,?,?,?)",
                            (key, sequence, body, media, projected, view, ready, answered))


class SQLiteStore:
    def __init__(self, path, checkout, error):
        self.path = Path(path)
        self.checkout = str(checkout)
        self.error = error

    @contextmanager
    def connection(self, *, writer=False, create=False, path=None, timeout=8):
        path = self.path if path is None else path
        if create:
            path.parent.mkdir(parents=True, exist_ok=True)
            fd = os.open(path, os.O_CREAT | os.O_RDWR, 0o600)
            os.close(fd)
        if not path.is_file():
            raise self.error("No attended session; run init with a manifest")
        db = None
        try:
            db = sqlite3.connect(path.absolute().as_uri() + "?mode=rw", uri=True, timeout=timeout, isolation_level=None)
            db.execute("PRAGMA foreign_keys=ON")
            db.execute("PRAGMA synchronous=FULL")
            db.execute("BEGIN IMMEDIATE" if writer else "BEGIN")
            yield db
            db.commit()
        except sqlite3.Error as exc:
            raise self.error(f"Attended review database unavailable: {exc}") from exc
        finally:
            if db is not None:
                db.close()

    def header(self, db, *, missing=False):
        version = db.execute("PRAGMA user_version").fetchone()[0]
        if version not in (1, 2, HOSTED_DB_VERSION):
            raise self.error("Unsupported attended review database version")
        row = db.execute("SELECT payload FROM metadata WHERE singleton=1").fetchone()
        if row is None:
            if missing:
                return None
            raise self.error("No attended session; run init with a manifest")
        header = json.loads(row[0])
        if header["checkout"] != self.checkout:
            raise self.error("session state belongs to another source checkout")
        if version == HOSTED_DB_VERSION:
            if header.get("hosted") is not True or header.get("hosted_directory") != self.hosted_directory():
                raise self.error("Hosted session belongs to its original state directory")
        elif header.get("hosted_bound"):
            raise self.error("Published hosted session has no recorded state directory; preserve it and create a new hosted session")
        return header

    def hosted_directory(self):
        if self.path.is_symlink():
            raise self.error("Hosted session database must be a regular file in its original state directory")
        return str(self.path.parent.resolve())

    def write_header(self, db, header):
        db.execute("INSERT OR REPLACE INTO metadata VALUES (1,?)", (pack(header),))

    @contextmanager
    def edit(self, seed=None):
        with self.connection(writer=True, create=seed is not None) as db:
            with self.editing(db, seed) as state:
                yield state

    @contextmanager
    def editing(self, db, seed=None):
        if seed is not None:
            version = db.execute("PRAGMA user_version").fetchone()[0]
            if version == 0:
                for ddl in SCHEMA.split(";"):
                    if ddl.strip():
                        db.execute(ddl)
                # Older helpers must refuse an active hosted database. The
                # JSON archive retains the existing reader schema.
                version = HOSTED_DB_VERSION if seed.get("hosted") else 1
                db.execute(f"PRAGMA user_version={version}")
        header = self.header(db, missing=seed is not None)
        if header is None:
            header = seed
            self.write_header(db, header)
            self.write_commit(db, header)
        before = dict(header)
        cards = Cards(db)
        events, history = [], []
        state = {**header, "candidates": cards, "events": events, "history": history}
        yield state
        for item in history:
            body, media, _ = cards.original[item["id"]]
            db.execute("INSERT INTO history(sequence, body, media) VALUES (?,?,?)",
                       (state["sequence"], body, media))
        cards.write(state["sequence"])
        for event in events:
            self.write_event(db, event)
        header = {k: v for k, v in state.items() if k not in ("candidates", "events", "history")}
        if before != header:
            self.write_header(db, header)
        if events:
            self.write_commit(db, header)

    @staticmethod
    def write_event(db, event):
        db.execute("INSERT INTO events VALUES (?,?,?)", (event["sequence"], event["kind"], pack(event)))

    @staticmethod
    def write_commit(db, header):
        snapshot = {**header, "host": None}
        db.execute("INSERT INTO commits VALUES (?,?)", (header["sequence"], pack(snapshot)))

    def visible_header(self, db, current):
        pending = db.execute("SELECT min(sequence) FROM exports WHERE receipt IS NULL").fetchone()[0]
        if pending is None:
            return current
        before, = db.execute("SELECT header FROM commits WHERE sequence<? ORDER BY sequence DESC LIMIT 1",
                             (pending,)).fetchone()
        return {**json.loads(before), "host": current["host"]}

    @staticmethod
    def working_cards(db, selected):
        if selected:
            rows = (db.execute("SELECT body FROM cards WHERE id=?", (cid,)).fetchone()
                    for cid in dict.fromkeys(selected))
            return [json.loads(row[0]) for row in rows if row is not None]
        return [json.loads(body) for body, in db.execute("SELECT body FROM cards ORDER BY position")]

    def status(self, full=False, after=None, page=False):
        with self.connection() as db:
            current = self.header(db)
            header = self.visible_header(db, current)
            if page and after == header["sequence"]:
                return header, [], []
            rows = self.card_rows(db, header["sequence"], current["sequence"],
                                  "body, media" if full else "summary")
            cards = [self.card(db, *row) if full else json.loads(row[0]) for row in rows]
            events = self.events(db, after, header["sequence"]) if after is not None and not page else []
            return header, cards, events

    @staticmethod
    def card_rows(db, sequence, current, projection):
        # The projection is a private query constant, never input.
        if sequence == current:
            return db.execute(f"SELECT {projection} FROM cards ORDER BY position")
        columns = ", ".join("v." + name for name in projection.split(", "))
        return db.execute(f"""
            SELECT {columns} FROM cards c JOIN versions v ON v.id=c.id
            AND v.sequence=(SELECT max(sequence) FROM versions WHERE id=c.id AND sequence<=?)
            ORDER BY c.position
        """, (sequence,))

    def changes(self, after, limit):
        with self.connection() as db:
            current = self.header(db)
            head = self.visible_header(db, current)
            if after > head["sequence"]:
                raise self.error("Cursor is ahead of the visible review")
            commits = db.execute("SELECT sequence, header FROM commits WHERE sequence>? AND sequence<=? ORDER BY sequence LIMIT ?",
                                 (after, head["sequence"], limit)).fetchall()
            if not commits:
                return head, [], False
            cursor, header = commits[-1]
            rows = db.execute("""
                SELECT page FROM versions v JOIN (
                    SELECT id, max(sequence) AS sequence FROM versions WHERE sequence>? AND sequence<=? GROUP BY id
                ) changed ON v.id=changed.id AND v.sequence=changed.sequence ORDER BY v.id
            """, (after, cursor))
            cards = [json.loads(page) for page, in rows]
            return json.loads(header), cards, cursor < head["sequence"]

    def page(self, after):
        with self.connection() as db:
            current = self.header(db)
            header = self.visible_header(db, current)
            cards = [] if after == header["sequence"] else [
                json.loads(page) for page, in self.card_rows(db, header["sequence"], current["sequence"], "page")
            ]
            return header, cards

    def selected_material(self, cid, fingerprint):
        with self.connection() as db:
            head = self.visible_header(db, self.header(db))["sequence"]
            row = db.execute("SELECT body, media FROM versions WHERE id=? AND sequence<=? ORDER BY sequence DESC LIMIT 1",
                             (cid, head)).fetchone()
            if row is None or json.loads(row[0])["fingerprint"] != fingerprint:
                raise self.error("Candidate not found or changed")
            return self.read_material(db, row[1])

    def card(self, db, body, media):
        return {**json.loads(body), **self.read_material(db, media)}

    def read_material(self, db, digest):
        if digest is None:
            return {}
        row = db.execute("SELECT payload FROM material WHERE digest=?", (digest,)).fetchone()
        if row is None or hashlib.sha256(row[0].encode()).hexdigest() != digest:
            raise self.error("Candidate material unavailable")
        return json.loads(row[0])

    def events(self, db, after, through, kinds=()):
        sql = """
            SELECT e.body, x.receipt FROM events e LEFT JOIN exports x ON x.sequence=e.sequence
            WHERE e.sequence>? AND e.sequence<=?
        """
        if kinds:
            sql += " AND e.kind IN (" + ",".join("?" for _ in kinds) + ")"
        return [self.archive_event(body, receipt) for body, receipt in
                db.execute(sql + " ORDER BY e.sequence", (after, through, *kinds))]

    @staticmethod
    def archive_event(body, receipt):
        event = json.loads(body)
        if receipt:
            event.update(json.loads(receipt))
        return event

    def wait_snapshot(self, after, kinds):
        with self.connection() as db:
            header = self.visible_header(db, self.header(db))
            events = self.events(db, after, header["sequence"], kinds) if after is not None else []
            return header, events

    def publication(self):
        with self.connection() as db:
            current = self.header(db)
            header = self.visible_header(db, current)
            if header["sequence"] == current["sequence"]:
                total, ready, answered = db.execute(
                    "SELECT count(*),coalesce(sum(ready),0),coalesce(sum(answered),0) FROM cards").fetchone()
            else:
                rows = self.card_rows(db, header["sequence"], current["sequence"], "ready, answered")
                total = ready = answered = 0
                for is_ready, is_answered in rows:
                    total += 1
                    ready += is_ready
                    answered += is_answered
            return header, {"waiting": total - ready - answered, "ready": ready, "answered": answered, "total": total}

    def enqueue_export(self, at):
        with self.connection(writer=True) as db:
            header = self.header(db)
            if header.get("hosted"):
                raise self.error("Use hosted-poll to receive the hosted Hand Back")
            pending = db.execute("SELECT sequence FROM exports WHERE receipt IS NULL").fetchone()
            if pending:
                return pending[0]
            sequence = header["sequence"]
            if db.execute("SELECT 1 FROM exports WHERE sequence=?", (sequence,)).fetchone():
                return sequence
            sequence += 1
            header.update(sequence=sequence, handed_back=at)
            self.write_header(db, header)
            self.write_commit(db, header)
            self.write_event(db, {"sequence": sequence, "time": at, "kind": "handed-back"})
            self.queue_archive(db, header)
            return sequence

    @staticmethod
    def archive_header(header):
        return {**{k: v for k, v in header.items() if k not in ("hosted", "hosted_bound", "hosted_directory")},
                "host": None}

    def queue_archive(self, db, header):
        archive = self.archive_header(header)
        db.execute("INSERT INTO exports VALUES (?,?,NULL)", (archive["sequence"], pack(archive)))

    def verify_staged_archive(self, db, path, header):
        """Compare a pre-existing archive before committing a recovered delivery."""
        with self.render_archive(path, self.archive_header(header), db=db) as (expected, _):
            verify_archive(expected, path)

    def pending_export(self):
        with self.connection() as db:
            self.header(db)
            return db.execute("SELECT min(sequence) FROM exports WHERE receipt IS NULL").fetchone()[0]

    def publish_export(self, sequence, path):
        # This transaction owns only the export lock file. The OS drops its
        # locks on process death. Reading/writing the review remains independent.
        with self.connection(writer=True, create=True, path=path.parent / ".export-lock.sqlite3", timeout=30):
            with self.connection() as db:
                current = self.header(db)
                raw, saved = db.execute("SELECT header, receipt FROM exports WHERE sequence=?", (sequence,)).fetchone()
                exclusive = bool(current.get("hosted"))
                if saved is not None and not exclusive:
                    return {"handed_back": json.loads(raw)["handed_back"], **json.loads(saved)}
                if db.execute("SELECT 1 FROM exports WHERE sequence>? AND receipt IS NOT NULL", (sequence,)).fetchone():
                    raise self.error("A newer Hand Back archive is already published")
                if json.loads(raw)["id"] != current["id"]:
                    raise self.error("Hand Back archive belongs to another session")
            header = json.loads(raw)
            receipt = self.write_archive(path, header, exclusive=True) if exclusive else self.write_archive(path, header)
            with self.connection(writer=True) as db:
                db.execute("UPDATE exports SET receipt=? WHERE sequence=?", (pack(receipt), sequence))
            return {"handed_back": json.loads(raw)["handed_back"], **receipt}

    def archive_cards(self, sequence, transaction=None):
        position = -1
        while True:
            with (self.connection() if transaction is None else nullcontext(transaction)) as db:
                row = db.execute("""
                    SELECT c.position, c.id, v.body, v.media FROM cards c JOIN versions v ON v.id=c.id
                    AND v.sequence=(SELECT max(sequence) FROM versions WHERE id=c.id AND sequence<=?)
                    WHERE c.position>? ORDER BY c.position LIMIT 1
                """, (sequence, position)).fetchone()
                if row is None:
                    return
                position, cid, body, media = row
                card = self.card(db, body, media)
            yield cid, card

    def archive_history(self, sequence, transaction=None):
        position = 0
        while True:
            with (self.connection() if transaction is None else nullcontext(transaction)) as db:
                row = db.execute("SELECT position, body, media FROM history WHERE position>? AND sequence<=? ORDER BY position LIMIT 1",
                                 (position, sequence)).fetchone()
                if row is None:
                    return
                position, body, media = row
                card = self.card(db, body, media)
            yield card

    def archive_events(self, sequence, receipt, transaction=None):
        for number in range(1, sequence + 1):
            with (self.connection() if transaction is None else nullcontext(transaction)) as db:
                body, saved = db.execute("""
                    SELECT e.body, x.receipt FROM events e LEFT JOIN exports x ON x.sequence=e.sequence
                    WHERE e.sequence=?
                """, (number,)).fetchone()
            yield self.archive_event(body, pack(receipt) if number == sequence else saved)

    def write_archive(self, path, header, *, exclusive=False):
        with self.render_archive(path, header) as (name, receipt):
            if exclusive:
                install_archive(name, path)
            else:
                replace_durably(name, path)
            return receipt

    @contextmanager
    def render_archive(self, path, header, *, db=None):
        receipt = {"decided": [], "pending": [], "feedback_pending": []}
        sequence = header["sequence"]

        def candidates(stream):
            stream.write("{")
            for index, (cid, card) in enumerate(self.archive_cards(sequence, db)):
                if card.get("decision"):
                    receipt["decided"].append(cid)
                else:
                    receipt["pending"].append(cid)
                    if card.get("feedback"):
                        receipt["feedback_pending"].append(cid)
                stream.write(",\n" if index else "\n")
                stream.write("    " + pack(cid) + ": " + pack(card))
            stream.write("\n  }")
            for ids in receipt.values():
                ids.sort()

        def array(stream, values):
            stream.write("[")
            for index, value in enumerate(values):
                stream.write(",\n" if index else "\n")
                stream.write("    " + pack(value))
            stream.write("\n  ]")

        fd, name = tempfile.mkstemp(prefix=".review-archive-", dir=path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
                stream.write(json.dumps(header, ensure_ascii=False, indent=2).removesuffix("\n}") + ',\n  "candidates": ')
                candidates(stream)
                stream.write(',\n  "history": ')
                array(stream, self.archive_history(sequence, db))
                stream.write(',\n  "events": ')
                array(stream, self.archive_events(sequence, receipt, db))
                stream.write("\n}\n")
                stream.flush()
                os.fsync(stream.fileno())
            yield name, receipt
        finally:
            Path(name).unlink(missing_ok=True)


def replace_durably(source, target):
    if os.name == "nt":
        windows_move(source, target, replace=True)
        return
    os.replace(source, target)
    sync_parent(target)


def install_archive(source, target):
    """Publish once, or verify the exact output after an interrupted receipt."""
    try:
        if os.name == "nt":
            windows_move(source, target, replace=False)
            return
        os.link(source, target)
    except FileExistsError:
        verify_archive(source, target)
    if os.name != "nt":
        sync_parent(target)


def verify_archive(source, target):
    conflict = ArchiveConflict("Existing Hand Back archive conflicts with the hosted delivery")
    if not stat.S_ISREG(target.lstat().st_mode):
        raise conflict
    fd = os.open(target, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
                 | getattr(os, "O_BINARY", 0))
    with os.fdopen(fd, "rb") as existing, open(source, "rb") as expected:
        if not stat.S_ISREG(os.fstat(fd).st_mode) or hashlib.file_digest(existing, "sha256").digest() != hashlib.file_digest(expected, "sha256").digest():
            raise conflict
        if os.name != "nt":
            os.fsync(fd)


def windows_move(source, target, *, replace):
    import ctypes
    from ctypes import wintypes

    move = ctypes.WinDLL("kernel32", use_last_error=True).MoveFileExW
    move.argtypes = (wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD)
    move.restype = wintypes.BOOL
    flags = 0x8 | int(replace)  # WRITE_THROUGH and optional REPLACE_EXISTING.
    if not move(source, str(target), flags):
        raise ctypes.WinError(ctypes.get_last_error())


def sync_parent(target):
    fd = os.open(target.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)
