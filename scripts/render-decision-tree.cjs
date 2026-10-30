// Optional authoring tool. The checked-in SVG needs no browser at build time.
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('playwright');
(async () => {
  if (!process.argv[2]) throw new Error('Pass the path to Quarto share/formats/html/mermaid/mermaid.min.js');
  const root = path.resolve(__dirname, '..');
  const browser = await chromium.launch();
  try {
    const page = await browser.newPage();
    await page.setContent('<!doctype html><html><body></body></html>');
    await page.addScriptTag({path: path.resolve(process.argv[2])});
    const source = fs.readFileSync(path.join(root,'images/decision-tree.mmd'),'utf8');
    const svg = await page.evaluate(async source => {
      mermaid.initialize({startOnLoad:false,securityLevel:'strict',htmlLabels:false,flowchart:{htmlLabels:false}});
      const result = (await mermaid.render('method-decision-tree',source)).svg;
      return result.replace('<style>', '<style>svg{background:white}.interdep text{fill:#fff!important}');
    },source);
    if (!svg.includes('<svg')) throw new Error('No SVG rendered');
    fs.writeFileSync(path.join(root,'images/decision-tree.svg'),svg);
    console.log('Rendered the maintained decision-tree source to SVG');
  } finally { await browser.close(); }
})().catch(error => { console.error(error);process.exitCode=1; });
