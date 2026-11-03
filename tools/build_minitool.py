"""Build tracked mini sources; optionally sync the explicitly selected local app."""
from pathlib import Path
import argparse
import zipfile

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--sync-sibling', action='store_true', help='Mirror tracked sources into ../小红书版/MiniTool and put the ZIP next to it')
args=parser.parse_args()
MINI=ROOT/'minitool'

def managed_block(text, start, end, content):
    if text.count(start)!=1 or text.count(end)!=1:
        raise SystemExit('Expected one managed block: '+start)
    before, rest=text.split(start,1)
    _, after=rest.split(end,1)
    return before+start+'\n'+content.rstrip()+'\n'+end+after

html=(MINI/'index.html').read_text(encoding='utf-8')
script=(MINI/'app.js').read_text(encoding='utf-8')
html=managed_block(html,'/* SHARED_MOBILE_START */','/* SHARED_MOBILE_END */',(ROOT/'src/mobile-polish.css').read_text(encoding='utf-8'))
script=managed_block(script,'/* SHARED_QUICK_START */','/* SHARED_QUICK_END */',(ROOT/'src/quick-start.js').read_text(encoding='utf-8'))
(MINI/'index.html').write_bytes(html.encode('utf-8'))
(MINI/'app.js').write_bytes(script.encode('utf-8'))
destination=ROOT/'output'
if args.sync_sibling:
    sibling=ROOT.parent/'小红书版'/'MiniTool'
    if not sibling.is_dir():
        raise SystemExit('Local MiniTool folder is missing; refusing to create an unrelated app folder')
    for name in ('index.html','app.js'):
        (sibling/name).write_bytes((MINI/name).read_bytes())
    destination=sibling.parent
destination.mkdir(exist_ok=True)
package=destination/'Hamilton_World_Atlas_XHS_MiniTool_v1.1-compliant.zip'
with zipfile.ZipFile(package,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
    for name in ('index.html','app.js'):
        info=zipfile.ZipInfo(name,date_time=(2026,11,4,0,0,0))
        info.compress_type=zipfile.ZIP_DEFLATED
        archive.writestr(info,(MINI/name).read_bytes())
print('Built mini-tool ZIP:',package)
