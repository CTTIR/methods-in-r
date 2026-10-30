import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class NavigationTests(unittest.TestCase):
    def test_titles_and_cross_references_survive_conversion(self):
        names = re.findall(r"^  - '([^']+\.Rmd)'", (ROOT/'_bookdown.yml').read_text(), re.M)
        texts = [(ROOT/name).read_text() for name in names]
        labels = re.findall(r'\{#([^ }]+)', '\n'.join(texts))
        self.assertEqual(len(labels), len(set(labels)), 'duplicate explicit anchors')
        unnumbered = re.findall(r'\{#([^ }]+) \.unnumbered\}', '\n'.join(texts))
        for name, text in zip(names, texts):
            for label in unnumbered:
                self.assertNotIn('\\@ref('+label+')', text, name)
            if '<div class="hero">' in text:
                self.assertLess(text.index('\n# '), text.index('<div class="hero">'), name)
            self.assertNotRegex(text, r'^### .*## ', name)
            self.assertNotRegex(text, r'\]\([^\n)]*\.Rmd(?:#[^)]*)?\)', name)
            self.assertNotRegex(text, r'\]\(\\@ref')
            self.assertNotRegex(text, r'\{-\} \{#')
            for label in re.findall(r'\]\(#([^ )]+)\)', text):
                self.assertIn(label, labels, name)
        for entry in json.loads((ROOT/'_data/manifest.json').read_text())['entries']:
            path = ROOT / Path(entry['target']).with_suffix('.Rmd')
            self.assertTrue(path.read_text().startswith('## '+entry['title']+' {#'), str(path))

if __name__ == '__main__':
    unittest.main()
