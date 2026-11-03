"""The mini-tool must build from a standalone GitHub checkout."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]

class MiniBuildTests(unittest.TestCase):
    def test_standalone_checkout_and_deterministic_root_zip(self):
        with tempfile.TemporaryDirectory() as directory:
            checkout = Path(directory) / 'checkout'
            for folder in ('tools', 'src', 'minitool'):
                (checkout / folder).mkdir(parents=True)
            shutil.copy(ROOT / 'tools/build_minitool.py', checkout / 'tools/build_minitool.py')
            for name in ('mobile-polish.css', 'quick-start.js'):
                shutil.copy(ROOT / 'src' / name, checkout / 'src' / name)
            (checkout / 'minitool/index.html').write_text('/* SHARED_MOBILE_START */old/* SHARED_MOBILE_END */', encoding='utf-8')
            (checkout / 'minitool/app.js').write_text('/* SHARED_QUICK_START */old/* SHARED_QUICK_END */', encoding='utf-8')
            command = [sys.executable, str(checkout / 'tools/build_minitool.py')]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            package = checkout / 'output/Hamilton_World_Atlas_XHS_MiniTool_v1.1-polished.zip'
            first = package.read_bytes()
            with zipfile.ZipFile(package) as archive:
                self.assertEqual(archive.namelist(), ['index.html', 'app.js'])
                for name, shared in [('index.html', 'mobile-polish.css'), ('app.js', 'quick-start.js')]:
                    self.assertIn((checkout / 'src' / shared).read_bytes().strip(), archive.read(name))
            second = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(first, package.read_bytes())

if __name__ == '__main__':
    unittest.main()
