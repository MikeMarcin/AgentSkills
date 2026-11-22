from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from PIL import Image

from test_trellis_client import client, write_glb


class RobloxExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def run_cli(self, *args):
        with mock.patch("sys.argv", ["trellis_client", *map(str, args)]), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            return client.main()

    def test_per_primitive_budget_indexed_and_unindexed(self):
        glb, report = self.root / "export.glb", self.root / "report.json"
        document = {
            "asset": {"version": "2.0"},
            "meshes": [{"name": "Shell", "primitives": [
                {"attributes": {"POSITION": 0}, "indices": 1},
                {"attributes": {"POSITION": 2}},
                {"attributes": {"POSITION": 0}, "mode": 5},
                {"attributes": {"POSITION": 0}, "mode": 6},
            ]}],
            "accessors": [
                {"count": 4, "type": "VEC3", "componentType": 5126},
                {"count": 60_000, "type": "SCALAR", "componentType": 5123},
                {"count": 36_000, "type": "VEC3", "componentType": 5126},
            ],
        }
        write_glb(glb, document)
        command = ["--audit-glb", glb, "--audit-out", report, "--target", "roblox"]
        self.assertEqual(self.run_cli(*command), 0)
        audit = json.loads(report.read_text())
        geometry = audit["roblox_geometry"]
        self.assertEqual(audit["sha256"], client.sha256_file(glb))
        self.assertEqual([p["triangles"] for p in geometry["parts"]], [20_000, 12_000, 2, 2])
        self.assertTrue(geometry["within_budget"])
        self.assertEqual(self.run_cli(*command, "--max-triangles-per-part", 12_000), 1)
        self.assertEqual(self.run_cli(*command, "--pbr-required"), 1)
        document["accessors"][1]["count"] = 60_003
        write_glb(glb, document)
        self.assertEqual(self.run_cli(*command), 1)
        self.assertIn("20001", json.loads(report.read_text())["roblox_geometry"]["errors"][0])
        self.assertEqual(self.run_cli("--audit-glb", glb, "--audit-out", report), 0)
        self.assertNotIn("roblox_geometry", json.loads(report.read_text()))
        for extra in (["--max-triangles-per-part", "20001"], ["--probe"]):
            with self.assertRaises(SystemExit):
                self.run_cli(*command, *extra)

    def test_unmeasurable_geometry_fails_with_primitive_location(self):
        glb, report = self.root / "incomplete.glb", self.root / "report.json"
        prim = {"attributes": {"POSITION": 0}}
        write_glb(glb, {"accessors": [{"type": "VEC3", "count": 4, "componentType": 5126}],
                        "meshes": [{"primitives": [prim, {**prim, "indices": -1}, {**prim, "mode": 1}, {}]}]})
        self.assertEqual(self.run_cli("--audit-glb", glb, "--target", "roblox", "--audit-out", report), 1)
        geo = json.loads(report.read_text())["roblox_geometry"]
        self.assertFalse(geo["within_budget"])
        self.assertEqual([s.split(":")[0] for s in geo["errors"]], [f"mesh 0, primitive {i}" for i in range(4)])
        write_glb(glb, {"meshes": []})
        self.assertEqual(self.run_cli("--audit-glb", glb, "--target", "roblox", "--audit-out", report), 1)

    def test_alpha_crop_and_opaque_preparation(self):
        source = self.root / "sheet.png"
        sheet = Image.new("RGBA", (16, 8), (255, 0, 0, 0))
        sheet.paste((110, 110, 110, 245), (2, 1, 7, 7))
        sheet.paste((80, 80, 80, 110), (4, 3, 6, 5))
        sheet.paste((0, 0, 255, 255), (10, 2, 14, 6))
        sheet.save(source)
        command = ["--prepare-image", source, "--prepare-output-dir", self.root, "--crop-box", "0,0,8,8",
                   "--canvas-size", 8, "--padding", 0, "--alpha-blur", 0]
        self.assertEqual(self.run_cli(*command), 0)
        manifest = json.loads((self.root / "sheet_prepare-run.json").read_text())
        self.assertEqual(manifest["preparation"]["alpha_method"], "source")
        self.assertEqual(manifest["source_sha256"], client.sha256_file(source))
        with Image.open(self.root / "sheet_alpha.png") as actual:
            self.assertEqual(actual.getchannel("A").tobytes(), sheet.crop((0, 0, 8, 8)).getchannel("A").tobytes())
        with Image.open(self.root / "sheet_crop.png") as rgb:
            self.assertEqual(rgb.getpixel((0, 0)), (128, 128, 128))
        self.assertEqual(self.run_cli(*command, "--alpha-mode", "neutral-border"), 0)
        self.assertEqual(json.loads((self.root / "sheet_prepare-run.json").read_text())["preparation"]["alpha_method"], "neutral_border")

        opaque = Image.new("RGB", (16, 8), (128, 128, 128))
        opaque.paste((180, 30, 15), (2, 2, 6, 6))
        opaque.save(source)
        self.assertEqual(self.run_cli(*command), 0)
        with Image.open(self.root / "sheet_alpha.png") as keyed:
            self.assertEqual(keyed.getpixel((0, 0))[-1], 0)
            self.assertEqual(keyed.getpixel((4, 4))[-1], 255)
