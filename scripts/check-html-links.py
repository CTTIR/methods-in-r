from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit,unquote
import argparse,json
p=argparse.ArgumentParser();p.add_argument('root');p.add_argument('output');a=p.parse_args();root=Path(a.root).resolve()
class Page(HTMLParser):
 def __init__(self,text):super().__init__();self.refs=[];self.ids=set();self.feed(text)
 def handle_starttag(self,tag,attrs):
  attrs=dict(attrs)
  if 'id' in attrs:self.ids.add(attrs['id'])
  for key in ['href'] if tag in ['a','link'] else ['src'] if tag in ['img','script','iframe'] else []:
   if key in attrs:self.refs.append((tag,attrs[key]))
pages={f:Page(f.read_text(errors='replace')) for f in root.rglob('*.html')};bad=[];n=0
for file,page in pages.items():
 for tag,ref in page.refs:
  u=urlsplit(ref)
  if u.scheme or u.netloc or not ref:continue
  path=unquote(u.path);dest=(root/path.lstrip('/') if path.startswith('/') else file.parent/path).resolve() if path else file
  if dest.is_dir():dest=dest/'index.html'
  n+=1
  if not dest.exists():bad.append([str(file.relative_to(root)),ref,'missing file'])
  elif tag=='a' and u.fragment and dest in pages and unquote(u.fragment) not in pages[dest].ids:bad.append([str(file.relative_to(root)),ref,'missing anchor'])
result={'html_pages':len(pages),'local_references':n,'broken':bad};Path(a.output).write_text(json.dumps(result,indent=2));print('HTML pages',len(pages),'local references',n,'broken',len(bad));print(json.dumps(bad[:15],indent=2))
raise SystemExit(bool(bad))
