import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from PIL import Image, ImageDraw


SCRIPT = Path(__file__).absolute().parents[1] / 'scripts/validate_sprite_sheet.py'


class SpriteValidatorTests(unittest.TestCase):
    def run_validator(self, sheet, *extra):
        result = subprocess.run([
            sys.executable, '-B', str(SCRIPT), '--sheet', str(sheet),
            '--cell-width', '16', '--cell-height', '16', '--columns', '2',
            '--rows', '1', '--animations', 'idle:2', '--json', *extra,
        ], cwd=sheet.parent, capture_output=True, text=True)
        json.loads(result.stdout)
        self.assertEqual(result.stderr, '')
        return result.returncode

    def test_dimensions_gutters_and_optional_body_checks(self):
        with tempfile.TemporaryDirectory(prefix='sprite-validator-') as directory:
            sheet = Path(directory) / 'sprite.png'
            image = Image.new('RGBA', (32, 16))
            draw = ImageDraw.Draw(image)
            draw.rectangle((4, 4, 11, 11), fill=(255, 0, 0, 255))
            draw.rectangle((20, 4, 27, 11), fill=(255, 0, 0, 255))
            image.save(sheet)
            self.assertEqual(self.run_validator(sheet, '--no-body-check'), 0)
            self.assertEqual(self.run_validator(sheet), 1)
            image.putpixel((0, 4), (255, 0, 0, 255))
            image.save(sheet)
            self.assertEqual(self.run_validator(sheet, '--no-body-check'), 1)
            image.resize((31, 16)).save(sheet)
            self.assertEqual(self.run_validator(sheet, '--no-body-check'), 1)


if __name__ == '__main__':
    unittest.main()
