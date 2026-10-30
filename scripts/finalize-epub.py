#!/usr/bin/env python3
"""Resolve bookdown's post-split references and bundle readable citation files."""
import argparse
from collections import defaultdict
import hashlib
import html
from pathlib import Path
import posixpath
import re
import tempfile
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree as ET
import zipfile

OPF = 'http://www.idpf.org/2007/opf'
XHTML = 'http://www.w3.org/1999/xhtml'


def finalize(path, source_root):
    path, source_root = Path(path), Path(source_root).resolve()
    with zipfile.ZipFile(path) as archive:
        if archive.testzip() is not None or archive.read('mimetype') != b'application/epub+zip':
            raise ValueError('Invalid EPUB archive')
        infos = archive.infolist()
        members = {info.filename: archive.read(info) for info in infos}
        comment = archive.comment
    ids, by_id = {}, defaultdict(list)
    for name, data in members.items():
        if name.endswith('.xhtml'):
            ids[name] = {e.attrib['id'] for e in ET.fromstring(data).iter() if 'id' in e.attrib}
            for anchor in ids[name]:
                by_id[anchor].append(name)
    container = ET.fromstring(members['META-INF/container.xml'])
    opf_name = next(e.attrib['full-path'] for e in container.iter() if e.tag.endswith('rootfile'))
    opf = ET.fromstring(members[opf_name])
    manifest = opf.find(f'{{{OPF}}}manifest')
    if manifest is None:
        raise ValueError('Missing EPUB manifest')
    hashes = defaultdict(list)
    for name, data in members.items():
        hashes[hashlib.sha256(data).hexdigest()].append(name)
    added, changes = {}, []
    text_assets = {}

    def rewrite(match, name):
        ref = html.unescape(match.group(1))
        url = urlsplit(ref)
        if url.scheme or url.netloc:
            return match.group(0)
        dest = posixpath.normpath(posixpath.join(posixpath.dirname(name), unquote(url.path))) if url.path else name
        fragment = unquote(url.fragment)
        if dest in members and (not fragment or dest not in ids or fragment in ids[dest]):
            return match.group(0)
        if fragment and len(by_id[fragment]) == 1:
            target = by_id[fragment][0]
        elif not fragment and dest not in members:
            asset = (source_root / unquote(url.path)).resolve()
            if not asset.is_relative_to(source_root) or not asset.is_file():
                # _common.R copies citation files beside the rendered EPUB.
                distribution = path.parent.resolve()
                asset = (distribution / unquote(url.path)).resolve()
                if not asset.is_relative_to(distribution) or not asset.is_file():
                    raise ValueError(f'{name}: missing attachment {ref}')
            data = asset.read_bytes()
            candidates = hashes[hashlib.sha256(data).hexdigest()]
            if len(candidates) == 1:
                target = candidates[0]
            elif asset.suffix.lower() in ('.bib', '.ris'):
                # A readable XHTML attachment is portable across EPUB readers;
                # the original citation text is preserved verbatim inside <pre>.
                key = hashlib.sha256(data).hexdigest()
                target = text_assets.get(key)
                if target is None:
                    target = posixpath.join(posixpath.dirname(opf_name),'attachments',asset.name+'.xhtml')
                    label = html.escape(asset.name)
                    added[target] = (f'<?xml version="1.0" encoding="utf-8"?>\n'
                        f'<html xmlns="{XHTML}" lang="en"><head><title>{label}</title></head>'
                        f'<body><h1>{label}</h1><pre>{html.escape(data.decode("utf-8"))}</pre></body></html>').encode()
                    ET.SubElement(manifest,f'{{{OPF}}}item',{
                        'id':'citation-'+key[:12],
                        'href':posixpath.relpath(target,posixpath.dirname(opf_name)),
                        'media-type':'application/xhtml+xml'})
                    text_assets[key] = target
            else:
                raise ValueError(f'{name}: attachment is not packaged uniquely: {ref}')
        else:
            raise ValueError(f'{name}: unresolved or ambiguous anchor {ref}')
        new_ref = posixpath.relpath(target,posixpath.dirname(name))
        if url.fragment:
            new_ref += '#'+url.fragment
        changes.append((name,ref,new_ref))
        return 'href="'+html.escape(new_ref,quote=True)+'"'

    for name in ids:
        text = members[name].decode('utf-8')
        members[name] = re.sub(r'href="([^"]*)"',lambda m:rewrite(m,name),text).encode()
    if added:
        ET.register_namespace('',OPF)
        ET.register_namespace('dc','http://purl.org/dc/elements/1.1/')
        members[opf_name] = ET.tostring(opf,encoding='utf-8',xml_declaration=True)
    complete = {**members, **added}
    for name, data in complete.items():
        if not name.endswith(('.xhtml','.opf','.ncx')):
            continue
        for element in ET.fromstring(data).iter():
            for attribute in ('href','src'):
                ref = element.attrib.get(attribute)
                if ref is None:
                    continue
                url = urlsplit(ref)
                if url.scheme or url.netloc:
                    continue
                dest = posixpath.normpath(posixpath.join(posixpath.dirname(name),unquote(url.path))) if url.path else name
                if dest not in complete:
                    raise ValueError(f'{name}: final resource is missing: {ref}')
                if url.fragment and dest in ids and unquote(url.fragment) not in ids[dest]:
                    raise ValueError(f'{name}: final anchor is missing: {ref}')
    with tempfile.NamedTemporaryFile(dir=path.parent,suffix='.epub',delete=False) as stream:
        temporary = Path(stream.name)
    try:
        with zipfile.ZipFile(temporary,'w') as archive:
            archive.comment = comment
            for info in infos:
                archive.writestr(info,members[info.filename])
            for name,data in added.items():
                archive.writestr(name,data,compress_type=zipfile.ZIP_DEFLATED)
        with zipfile.ZipFile(temporary) as archive:
            if archive.testzip() is not None:
                raise ValueError('Final EPUB failed its CRC check')
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)
    return changes


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('epub',nargs='?',type=Path,default=Path('docs/methods-in-r.epub'))
    parser.add_argument('--source-root',type=Path,default=Path(__file__).resolve().parents[1])
    args=parser.parse_args()
    print(f'Finalized {len(finalize(args.epub,args.source_root))} EPUB links')
