import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile
from xml.etree import ElementTree as ET

spec=importlib.util.spec_from_file_location('epub',Path(__file__).resolve().parents[1]/'scripts/finalize-epub.py')
epub=importlib.util.module_from_spec(spec);spec.loader.exec_module(epub)

class EpubLinks(unittest.TestCase):
    def make(self, root, ref='#target'):
        p=root/'book.epub'
        with zipfile.ZipFile(p,'w') as z:
            z.writestr('mimetype','application/epub+zip')
            z.writestr('META-INF/container.xml','<container><rootfiles><rootfile full-path="EPUB/book.opf"/></rootfiles></container>')
            z.writestr('EPUB/book.opf','<package xmlns="http://www.idpf.org/2007/opf"><manifest/></package>')
            z.writestr('EPUB/a.xhtml',f'<html><body><a href="{ref}">Go</a><a href="cite.bib">Citation</a></body></html>')
            z.writestr('EPUB/b.xhtml','<html><body><h1 id="target">Target</h1></body></html>')
        (root/'cite.bib').write_text('@book{x, title={A & B}}\n')
        return p

    def test_split_link_and_citation_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);p=self.make(root)
            self.assertEqual(len(epub.finalize(p,root)),2)
            with zipfile.ZipFile(p) as z:
                self.assertIn('href="b.xhtml#target"',z.read('EPUB/a.xhtml').decode())
                attachment=ET.fromstring(z.read('EPUB/attachments/cite.bib.xhtml'))
                self.assertEqual(attachment.find('.//{http://www.w3.org/1999/xhtml}pre').text,(root/'cite.bib').read_text())
                self.assertIsNone(z.testzip())
            before=p.read_bytes();self.assertEqual(epub.finalize(p,root),[])
            self.assertEqual(before,p.read_bytes())

    def test_missing_anchor_preserves_original(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);p=self.make(root,'#absent');before=p.read_bytes()
            with self.assertRaises(ValueError):epub.finalize(p,root)
            self.assertEqual(before,p.read_bytes())
