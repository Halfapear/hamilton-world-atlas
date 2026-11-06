"""v1.2 cross-client integration and narrow viewport checks."""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
import hashlib
import json
import os
import sys
from datetime import datetime
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'output/playwright/v1.2' / (os.environ.get('ATLAS_BROWSER') or 'chromium')
ART.mkdir(parents=True, exist_ok=True)
checks = []
def check(name, result):
    checks.append({'name': name, 'pass': bool(result)})
    print(('PASS ' if result else 'FAIL ') + name, flush=True)

server = ThreadingHTTPServer(('127.0.0.1', 0), partial(SimpleHTTPRequestHandler, directory=str(ROOT)))
Thread(target=server.serve_forever, daemon=True).start()
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, **({'channel': os.environ['ATLAS_BROWSER']} if os.environ.get('ATLAS_BROWSER') else {}))
        for client in ('web', 'mini'):
            errors = []
            page = browser.new_page(viewport={'width':390, 'height':844})
            page.on('pageerror', lambda e: errors.append(str(e)))
            path = 'index.html' if client == 'web' else 'minitool/index.html'
            url = f'http://127.0.0.1:{server.server_port}/{path}'
            page.goto(url)
            page.wait_for_function('document.documentElement.dataset.appReady==="true"')
            page.add_style_tag(content='html,*{scroll-behavior:auto!important}')
            exists = page.locator('nav [data-view="leads"]').count() == 1
            check(client+' has separate lead navigation', exists)
            if not exists:
                page.close()
                continue
            check(client+' canonical data 22+7', page.evaluate('HAMILTON_APP_TEST.DATA.stops.length===22 && HAMILTON_APP_TEST.DATA.tourLeads.length===7'))
            check(client+' version badge', page.locator('#app-version').inner_text()=='v1.2')
            check(client+' lead layer off by default', page.locator('.lead-marker').count()==0 and not page.locator('#lead-layer-toggle').is_checked())
            check(client+' official count unchanged', page.locator('.map-marker').count()==22 and '22' in page.locator('#metric-stops').inner_text())
            page.locator('#lead-layer-toggle').check()
            check(client+' opt-in seven hollow markers', page.locator('.lead-marker').count()==7 and page.evaluate('getComputedStyle(document.querySelector(".lead-marker .lead-dot")).fill==="none"'))
            check(client+' visible risk warning', page.locator('#lead-map-warning').is_visible() and '未官宣' in page.locator('#lead-map-warning').inner_text())
            page.locator('[data-region-filter="asia"]').click()
            check(client+' Asia official count still two', page.locator('.map-marker').count()==2 and page.locator('.lead-marker').count()==7)
            check(client+' Asia fits city centres', page.evaluate('''() => {
                const app=HAMILTON_APP_TEST, b=document.querySelector('#world-map').viewBox.baseVal;
                return app.DATA.tourLeads.every(s=>{const p=app.projection(s);return p.x>b.x && p.x<b.x+b.width && p.y>b.y && p.y<b.y+b.height});
            }'''))
            check(client+' route only Korea', page.evaluate('document.querySelector(".korea-line").points.numberOfItems===2'))
            page.locator('#world-map').screenshot(path=str(ART/f'{client}-asia-lead-layer-390.png'))
            page.locator('#zoom-in').click()
            check(client+' lead positions follow projection after zoom', page.evaluate('''() => HAMILTON_APP_TEST.DATA.tourLeads.every(s=>{
                const p=HAMILTON_APP_TEST.projection(s),dot=document.querySelector('[data-lead="'+s.id+'"] .lead-dot');
                return Math.abs(+dot.getAttribute('cx')-p.x)<.001 && Math.abs(+dot.getAttribute('cy')-p.y)<.001;
            })'''))
            page.locator('#zoom-reset').click()
            marker = page.locator('.lead-marker[data-lead="lead-shanghai"]')
            marker.focus()
            page.keyboard.press('Enter')
            check(client+' keyboard marker opens evidence not booking', page.locator('#lead-dialog').is_visible() and '上海' in page.locator('#lead-dialog').inner_text())
            check(client+' modal focus trapped', page.evaluate('document.querySelector("#lead-dialog").contains(document.activeElement)'))
            page.keyboard.press('Escape')
            check(client+' close restores marker focus', page.evaluate('document.activeElement.dataset.lead==="lead-shanghai"'))
            page.locator('[data-region-filter="north-america"]').click()
            check(client+' excludes Asia leads from NA', page.locator('.lead-marker').count()==0 and page.locator('.map-marker').count()==19)
            page.locator('nav [data-view="leads"]').click()
            check(client+' seven risk-labelled cards', page.locator('.lead-card').count()==7 and page.evaluate('[...document.querySelectorAll(".lead-card")].every(e=>e.textContent.includes("未官宣")&&e.textContent.includes("不可据此订机酒"))'))
            check(client+' no lead booking/price/countdown', page.locator('#view-leads [data-stop],#view-leads [data-countdown],#view-leads .price-choice').count()==0)
            page.locator('.lead-card [data-lead="lead-tokyo"]').click()
            dialog = page.locator('#lead-dialog')
            check(client+' evidence honest about unread original', '访问失败' in dialog.inner_text() and '未独立核实' in dialog.inner_text() and '2026-11-06' in dialog.inner_text())
            if client=='mini':
                check('mini lead links have no new-tab target',page.locator('#lead-dialog a[target],#view-leads a[target]').count()==0)
            page.keyboard.press('Tab')
            check(client+' Tab remains inside source dialog', page.evaluate('document.querySelector("#lead-dialog").contains(document.activeElement)'))
            if client=='mini':
                dialog.locator('a').first.click()
                check('mini lead external URL uses safe text modal', page.locator('#mini-modal-text').is_visible() and 'note.com' in page.locator('#mini-modal-text').input_value())
                check('mini nested text modal receives focus',page.evaluate('document.querySelector("#mini-modal").contains(document.activeElement)'))
                page.keyboard.press('Escape')
                check('mini Escape closes only top modal', not page.locator('#mini-modal').is_visible() and page.locator('#lead-dialog').is_visible())
                check('mini nested modal restores source focus',page.evaluate('document.querySelector("#lead-dialog").contains(document.activeElement)'))
            page.keyboard.press('Escape')
            page.locator('nav [data-view="plan"]').click()
            check(client+' only official plan options', page.locator('#plan-stop option').count()==22 and 'lead-' not in page.locator('#plan-stop').inner_html())
            # Preserve the existing storage schema rather than resetting on upgrade.
            page.evaluate('localStorage.setItem("hamilton-world-atlas-v1",JSON.stringify({plan:{stopId:"london",quantity:"3",date:"",note:"legacy-v1"},checks:{}}))')
            page.reload()
            page.wait_for_function('document.documentElement.dataset.appReady==="true"')
            page.add_style_tag(content='html,*{scroll-behavior:auto!important}')
            page.locator('nav [data-view="plan"]').click()
            check(client+' legacy plan survives upgrade', 'legacy-v1' in page.locator('#saved-plan').inner_text() and page.locator('#plan-stop').input_value()=='london')
            page.locator('nav [data-view="map"]').click()
            check(client+' Korea scope visible', '一楼 VIP' in page.locator('#korea-quick-start').inner_text() and '资格' in page.locator('#korea-quick-start').inner_text())
            for width in (320,360,390,430,1440):
                page.set_viewport_size({'width':width, 'height':900})
                for view in ('map','leads','plan'):
                    page.locator('nav [data-view="'+view+'"]').click()
                    page.screenshot(path=str(ART/f'{client}-{view}-{width}.png'), full_page=True)
                    check(f'{client} {view} {width}px no overflow', page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'))
                page.locator('nav [data-view="leads"]').click()
                page.locator('.lead-card [data-lead="lead-hong-kong"]').click()
                page.screenshot(path=str(ART/f'{client}-source-{width}.png'), full_page=True)
                check(f'{client} source {width}px fits screen', page.evaluate('''() => {
                    const r=document.querySelector('#lead-dialog .lead-dialog-card').getBoundingClientRect();
                    return r.x>=0 && r.right<=innerWidth+1 && r.top>=0 && r.bottom<=innerHeight+1;
                }'''))
                page.keyboard.press('Escape')
            check(client+' no uncaught exception', not errors)
            page.close()
        report={'version':'1.2','testedAt':datetime.now().astimezone().isoformat(),'browser':browser.version,'checks':checks,
                'webSha256':hashlib.sha256((ROOT/'index.html').read_bytes()).hexdigest(),
                'miniScriptSha256':hashlib.sha256((ROOT/'minitool/app.js').read_bytes()).hexdigest()}
        (ART/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2), encoding='utf-8')
        browser.close()
finally:
    server.shutdown()
    server.server_close()
print(f'RESULT: {sum(c["pass"] for c in checks)}/{len(checks)}')
if not all(c['pass'] for c in checks):
    raise SystemExit(1)
