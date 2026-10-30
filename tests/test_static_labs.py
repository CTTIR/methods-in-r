import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("static_labs", Path(__file__).parents[1] / "scripts/static_labs.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class StaticLabConversion(unittest.TestCase):
    def test_preserves_first_statement_and_blank_lines(self):
        source = "```{r}\nx <- data.frame(a=1)\nprint(x)\n```\n"
        expected = "```r\nx <- data.frame(a=1)\nprint(x)\n```\n"
        self.assertEqual(module.transform(source), expected)
        self.assertEqual(module.transform(expected), expected)
        self.assertEqual(module.transform("```{r}\n\nx <- 1\n```"), "```r\n\nx <- 1\n```")

    def test_options_and_other_engines_preserve_code(self):
        self.assertEqual(module.transform("```{python, echo=FALSE}\nx = 1\n```"), "```python\nx = 1\n```")

if __name__ == "__main__": unittest.main()
