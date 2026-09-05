from __future__ import annotations

import argparse
import json
from pathlib import Path
import struct
from types import SimpleNamespace
import sys
import tempfile
import unittest
from unittest import mock


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import trellis_client as client  # noqa: E402
from providers import get_provider  # noqa: E402
from providers.common import ProviderRun, capability_snapshot  # noqa: E402


FIXTURES = Path(__file__).parent / "fixtures"


def provider_args(image: Path) -> SimpleNamespace:
    return SimpleNamespace(
        selected_seed=7,
        image=image,
        multi_image=[],
        ss_guidance_strength=7.5,
        ss_sampling_steps=12,
        slat_guidance_strength=3.0,
        slat_sampling_steps=12,
        multiimage_algo="stochastic",
        mesh_simplify=0.95,
        texture_size=1024,
        extract_gaussian=False,
        stderr=sys.stderr,
        resolution="1024",
        ss_guidance_rescale=0.7,
        ss_rescale_t=5.0,
        shape_slat_guidance_strength=7.5,
        shape_slat_guidance_rescale=0.5,
        shape_slat_sampling_steps=12,
        shape_slat_rescale_t=3.0,
        tex_slat_guidance_strength=1.0,
        tex_slat_guidance_rescale=0.0,
        tex_slat_sampling_steps=12,
        tex_slat_rescale_t=3.0,
        decimation_target=300_000,
        free_only=True,
        quota_wait=True,
        pbr_required=False,
        audit_out=None,
    )


def write_glb(path: Path, document: dict[str, object]) -> None:
    payload = json.dumps(document, separators=(",", ":")).encode("utf-8")
    payload += b" " * ((4 - (len(payload) % 4)) % 4)
    path.write_bytes(
        struct.pack("<4sII", b"glTF", 2, 12 + 8 + len(payload))
        + struct.pack("<II", len(payload), client.GLB_JSON_CHUNK)
        + payload
    )


class TrellisClientTests(unittest.TestCase):
    def test_provider_registry_owns_exact_live_identities(self) -> None:
        trellis1 = get_provider("trellis1").BINDING
        trellis2 = get_provider("trellis2").BINDING
        self.assertEqual(trellis1.space_id, "trellis-community/TRELLIS")
        self.assertEqual(trellis2.space_id, "microsoft/TRELLIS.2")
        self.assertEqual(trellis1.generation_endpoint, "/generate_and_extract_glb")
        self.assertEqual(trellis2.generation_endpoint, "/image_to_3d")
        self.assertTrue(trellis1.supports_multi_image)
        self.assertFalse(trellis2.supports_multi_image)

    def test_capability_snapshot_hashes_the_complete_schema(self) -> None:
        schema = json.loads((FIXTURES / "trellis2-api.json").read_text(encoding="utf-8"))
        snapshot = capability_snapshot(
            get_provider("trellis2").BINDING,
            schema,
            "2026-07-12T00:00:00Z",
        )
        repeated = capability_snapshot(
            get_provider("trellis2").BINDING,
            schema,
            "2026-07-12T00:00:00Z",
        )
        self.assertTrue(snapshot["available"])
        self.assertEqual(snapshot["snapshot_digest"], repeated["snapshot_digest"])
        self.assertRegex(snapshot["api_schema_digest"], r"^sha256:[0-9a-f]{64}$")
        self.assertIn("roughness", snapshot["capabilities"]["pbr_channels"])

    def test_legacy_v1_command_defaults_to_trellis1(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / "reference.png"
            image.write_bytes(b"png")
            parser = client.build_parser()
            argv = ["--image", str(image)]
            args = parser.parse_args(argv)
            client.apply_work_order(parser, args, argv)
            args.provider = client.selected_provider_name(args.provider)
            client.apply_provider_defaults(args)
            client.validate_args(parser, args)
            self.assertEqual(args.provider, "trellis1")
            self.assertEqual(args.texture_size, 1024)
            self.assertEqual(args.multiimage_algo, "stochastic")

    def test_trellis1_adapter_preserves_single_image_endpoint_order(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / "reference.png"
            image.write_bytes(b"png")
            calls: list[str] = []

            def predict(_client: object, endpoint: str, *values: object) -> object:
                calls.append(endpoint)
                if endpoint == "/preprocess_image":
                    return {"path": str(image)}
                if endpoint == "/generate_and_extract_glb":
                    return {"path": str(Path(directory) / "model.glb")}
                return None

            run = get_provider("trellis1").generate(
                object(),
                lambda path: {"path": path},
                provider_args(image),
                predict,
            )
            self.assertEqual(
                calls,
                ["/start_session", "/lambda", "/preprocess_image", "/generate_and_extract_glb"],
            )
            self.assertEqual(run.settings["texture_size"], 1024)

    def test_trellis2_adapter_uses_generation_then_glb_extraction(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / "reference.png"
            image.write_bytes(b"png")
            calls: list[str] = []

            def predict(_client: object, endpoint: str, *values: object) -> object:
                calls.append(endpoint)
                if endpoint == "/preprocess_image":
                    return {"path": str(image)}
                return {"path": str(Path(directory) / ("model.glb" if endpoint == "/extract_glb" else "preview.glb"))}

            args = provider_args(image)
            args.texture_size = 2048
            run = get_provider("trellis2").generate(
                object(),
                lambda path: {"path": path},
                args,
                predict,
            )
            self.assertEqual(
                calls,
                ["/start_session", "/lambda", "/preprocess_image", "/image_to_3d", "/extract_glb"],
            )
            self.assertEqual(run.settings["decimation_target"], 300_000)

    def test_pbr_required_auto_selection_never_downgrades_to_v1(self) -> None:
        self.assertEqual(client.selected_provider_name("auto", pbr_required=True), "trellis2")
        self.assertEqual(client.selected_provider_name(None, pbr_required=True), "trellis2")
        self.assertEqual(client.selected_provider_name("trellis1", pbr_required=True), "trellis1")

        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / "reference.png"
            image.write_bytes(b"png")
            parser = client.build_parser()
            argv = ["--provider", "trellis1", "--pbr-required", "--image", str(image)]
            args = parser.parse_args(argv)
            client.apply_work_order(parser, args, argv)
            args.provider = client.selected_provider_name(args.provider, args.pbr_required)
            client.apply_provider_defaults(args)
            with self.assertRaises(SystemExit):
                client.validate_args(parser, args)

    def test_glb_audit_requires_textured_base_color_and_metallic_roughness(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            complete = root / "complete.glb"
            incomplete = root / "incomplete.glb"
            write_glb(
                complete,
                {
                    "asset": {"version": "2.0"},
                    "materials": [
                        {
                            "name": "pbr",
                            "pbrMetallicRoughness": {
                                "baseColorTexture": {"index": 0},
                                "metallicRoughnessTexture": {"index": 1},
                            },
                        }
                    ],
                    "textures": [{}, {}],
                    "images": [{}, {}],
                },
            )
            write_glb(
                incomplete,
                {
                    "asset": {"version": "2.0"},
                    "materials": [
                        {
                            "name": "base-only",
                            "pbrMetallicRoughness": {"baseColorTexture": {"index": 0}},
                        }
                    ],
                    "textures": [{}],
                    "images": [{}],
                },
            )
            accepted = client.audit_glb(complete)
            rejected = client.audit_glb(incomplete)
            self.assertTrue(accepted["pbr_required_complete"])
            self.assertFalse(rejected["pbr_required_complete"])
            self.assertEqual(rejected["materials"][0]["missing_required_channels"], ["metallic", "roughness"])

    def test_work_order_rejects_secret_material(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "work-order.json"
            path.write_text(
                json.dumps(
                    {
                        "schema_name": "example_workflow.provider_work_order",
                        "schema_version": 1,
                        "request_id": "example_workflow:/generation-request/example-scene/test/0001",
                        "source_intent_id": "example_workflow:/source-intent/example-scene/test",
                        "provider_id": "skill:trellis1",
                        "inputs": [],
                        "parameters": {"token": "not-a-secret"},
                        "free_only": True,
                        "quota_wait": True,
                        "staging_directory": "staging/test-0001",
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaises(SystemExit):
                client.load_work_order(path)

    def test_attempt_receipt_contains_only_redacted_provider_identity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            image = root / "reference.png"
            model = root / "model.glb"
            image.write_bytes(b"image")
            model.write_bytes(b"model")
            args = argparse.Namespace(
                request_id="example_workflow:/generation-request/example-scene/test/0001",
                attempt_id="example_workflow:/generation-attempt/example-scene/test/0001",
                provider="trellis1",
                work_order_data={},
                image=image,
                multi_image=[],
            )
            receipt = client.build_attempt_receipt(
                args,
                "skill:trellis1",
                "sha256:" + ("2" * 64),
                [{"path": str(model)}],
            )
            encoded = json.dumps(receipt)
            self.assertEqual(receipt["status"], "captured")
            self.assertEqual(receipt["provider_job_id_redacted"], "job:<redacted>")
            self.assertNotIn("hf_", encoded)
            self.assertNotIn("Authorization", encoded)

    def test_generation_manifest_records_provider_and_live_schema_digest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            image = root / "reference.png"
            provider_model = root / "provider-model.glb"
            output = root / "output"
            output.mkdir()
            image.write_bytes(b"image")
            provider_model.write_bytes(b"model")
            args = provider_args(image)
            args.provider = "trellis1"
            args.capabilities_out = root / "capabilities.json"
            args.token = None
            args.output_dir = output
            args.randomize_seed = False
            args.seed = 7
            args.request_id = "example_workflow:/generation-request/example-scene/test/0001"
            args.attempt_id = "example_workflow:/generation-attempt/example-scene/test/0001"
            args.work_order_data = {}
            args.attempt_receipt = root / "attempt-receipt.json"
            capabilities = {
                "available": True,
                "missing_required_endpoints": [],
                "snapshot_digest": "sha256:" + ("2" * 64),
                "api_schema_digest": "sha256:" + ("3" * 64),
                "capabilities": {
                    "free_only": True,
                    "pbr_channels": ["base_color"],
                },
            }
            provider = get_provider("trellis1")

            with (
                mock.patch.object(client, "probe_provider", return_value=capabilities),
                mock.patch.object(
                    client,
                    "require_gradio_client",
                    return_value=(lambda _space: object(), lambda path: path),
                ),
                mock.patch.object(client, "get_configured_token", return_value=None),
                mock.patch.object(
                    provider,
                    "generate",
                    return_value=ProviderRun(settings={"seed": 7}, raw_result={"path": str(provider_model)}),
                ),
            ):
                manifest = client.run_generation(args)

            persisted = json.loads((output / "trellis-run.json").read_text(encoding="utf-8"))
            receipt = json.loads(args.attempt_receipt.read_text(encoding="utf-8"))
            self.assertEqual(manifest["provider"], "trellis1")
            self.assertEqual(persisted["api_schema_digest"], "sha256:" + ("3" * 64))
            self.assertEqual(receipt["capability_snapshot_digest"], "sha256:" + ("2" * 64))
            self.assertEqual(receipt["provider_job_id_redacted"], "job:<redacted>")

    def test_quota_wait_receipt_survives_and_resume_uses_a_new_attempt(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            image = root / "reference.png"
            image.write_bytes(b"image")
            capabilities = {
                "available": True,
                "missing_required_endpoints": [],
                "snapshot_digest": "sha256:" + ("2" * 64),
                "api_schema_digest": "sha256:" + ("3" * 64),
                "capabilities": {"free_only": True, "pbr_channels": ["base_color"]},
            }
            provider = get_provider("trellis1")
            request_id = "example_workflow:/generation-request/example-scene/quota/0001"

            waiting_args = provider_args(image)
            waiting_args.provider = "trellis1"
            waiting_args.capabilities_out = root / "capabilities.json"
            waiting_args.token = None
            waiting_args.output_dir = root / "waiting-output"
            waiting_args.output_dir.mkdir()
            waiting_args.randomize_seed = False
            waiting_args.seed = 7
            waiting_args.request_id = request_id
            waiting_args.attempt_id = "example_workflow:/generation-attempt/example-scene/quota/0001"
            waiting_args.work_order_data = {}
            waiting_args.attempt_receipt = root / "attempt-0001.json"

            with (
                mock.patch.object(client, "probe_provider", return_value=capabilities),
                mock.patch.object(
                    client,
                    "require_gradio_client",
                    return_value=(lambda _space: object(), lambda path: path),
                ),
                mock.patch.object(client, "get_configured_token", return_value=None),
                mock.patch.object(provider, "generate", side_effect=RuntimeError("exceeded your ZeroGPU quota")),
            ):
                with self.assertRaises(client.ProviderAttemptError):
                    client.run_generation(waiting_args)

            waiting_bytes = waiting_args.attempt_receipt.read_bytes()
            waiting = json.loads(waiting_bytes)
            self.assertEqual(waiting["status"], "waiting_for_quota")

            provider_model = root / "provider-model.glb"
            provider_model.write_bytes(b"model")
            resumed_args = provider_args(image)
            resumed_args.provider = "trellis1"
            resumed_args.capabilities_out = root / "capabilities-resume.json"
            resumed_args.token = None
            resumed_args.output_dir = root / "resumed-output"
            resumed_args.output_dir.mkdir()
            resumed_args.randomize_seed = False
            resumed_args.seed = 7
            resumed_args.request_id = request_id
            resumed_args.attempt_id = "example_workflow:/generation-attempt/example-scene/quota/0002"
            resumed_args.work_order_data = {}
            resumed_args.attempt_receipt = root / "attempt-0002.json"
            with (
                mock.patch.object(client, "probe_provider", return_value=capabilities),
                mock.patch.object(
                    client,
                    "require_gradio_client",
                    return_value=(lambda _space: object(), lambda path: path),
                ),
                mock.patch.object(client, "get_configured_token", return_value=None),
                mock.patch.object(
                    provider,
                    "generate",
                    return_value=ProviderRun(settings={"seed": 7}, raw_result={"path": str(provider_model)}),
                ),
            ):
                client.run_generation(resumed_args)

            resumed = json.loads(resumed_args.attempt_receipt.read_text(encoding="utf-8"))
            self.assertEqual(resumed["status"], "captured")
            self.assertEqual(resumed["request_id"], waiting["request_id"])
            self.assertNotEqual(resumed["attempt_id"], waiting["attempt_id"])
            self.assertEqual(waiting_args.attempt_receipt.read_bytes(), waiting_bytes)

    def test_pbr_required_output_gate_writes_terminal_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            image = root / "reference.png"
            image.write_bytes(b"image")
            provider_model = root / "provider-model.glb"
            write_glb(
                provider_model,
                {
                    "asset": {"version": "2.0"},
                    "materials": [
                        {
                            "pbrMetallicRoughness": {"baseColorTexture": {"index": 0}},
                        }
                    ],
                    "textures": [{}],
                    "images": [{}],
                },
            )
            capabilities = {
                "available": True,
                "missing_required_endpoints": [],
                "snapshot_digest": "sha256:" + ("2" * 64),
                "api_schema_digest": "sha256:" + ("3" * 64),
                "capabilities": {
                    "free_only": True,
                    "pbr_channels": ["base_color", "roughness", "metallic", "opacity"],
                },
            }
            provider = get_provider("trellis2")
            args = provider_args(image)
            args.provider = "trellis2"
            args.pbr_required = True
            args.capabilities_out = root / "capabilities.json"
            args.token = None
            args.output_dir = root / "output"
            args.output_dir.mkdir()
            args.randomize_seed = False
            args.seed = 7
            args.request_id = "example_workflow:/generation-request/example-scene/pbr/0001"
            args.attempt_id = "example_workflow:/generation-attempt/example-scene/pbr/0001"
            args.work_order_data = {}
            args.attempt_receipt = root / "attempt.json"

            with (
                mock.patch.object(client, "probe_provider", return_value=capabilities),
                mock.patch.object(
                    client,
                    "require_gradio_client",
                    return_value=(lambda _space: object(), lambda path: path),
                ),
                mock.patch.object(client, "get_configured_token", return_value=None),
                mock.patch.object(
                    provider,
                    "generate",
                    return_value=ProviderRun(settings={"seed": 7}, raw_result={"path": str(provider_model)}),
                ),
            ):
                with self.assertRaises(client.ProviderAttemptError) as raised:
                    client.run_generation(args)

            receipt = json.loads(args.attempt_receipt.read_text(encoding="utf-8"))
            audit = json.loads((args.output_dir / "pbr-audit.json").read_text(encoding="utf-8"))
            self.assertEqual(raised.exception.status, "terminal_failure")
            self.assertEqual(receipt["status"], "terminal_failure")
            self.assertFalse(audit["pbr_required_complete"])


if __name__ == "__main__":
    unittest.main()
