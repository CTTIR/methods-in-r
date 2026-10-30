import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile

spec=importlib.util.spec_from_file_location('downloads',Path(__file__).parents[1]/'scripts/build-download-manifest.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class DownloadTests(unittest.TestCase):
    def test_only_present_recognizable_formats_are_listed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            self.assertEqual(module.collect(root),[])
            (root/'methods-in-r.pdf').write_bytes(b'HTML error response')
            with zipfile.ZipFile(root/'methods-in-r.epub','w') as z:z.writestr('other.txt','ordinary zip')
            self.assertEqual(module.collect(root),[])
            (root/'methods-in-r.pdf').write_bytes(b'%PDF-1.7\n')
            with zipfile.ZipFile(root/'methods-in-r.epub','w') as z:
                z.writestr('mimetype','application/epub+zip')
                z.writestr('META-INF/container.xml','<container/>')
            self.assertEqual(module.collect(root),['methods-in-r.pdf','methods-in-r.epub'])
