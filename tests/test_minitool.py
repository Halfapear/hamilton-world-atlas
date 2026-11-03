"""Browser regression tests; real Xiaohongshu WebView still needs on-device QA."""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
import os
import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'minitool'
artifacts = ROOT / 'output' / 'playwright' / 'minitool'
artifacts.mkdir(parents=True, exist_ok=True)
checks = []

def check(name, value):
    checks.append((name, bool(value)))
    print(('PASS ' if value else 'FAIL ') + name, flush=True)

server = ThreadingHTTPServer(('127.0.0.1', 0), partial(SimpleHTTPRequestHandler, directory=str(SOURCE)))
Thread(target=server.serve_forever, daemon=True).start()
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, **({'channel': os.environ['ATLAS_BROWSER']} if os.environ.get('ATLAS_BROWSER') else {}))
        print('BROWSER:', browser.version)
        page = browser.new_page(viewport={'width': 390, 'height': 844})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto(f'http://127.0.0.1:{server.server_port}/index.html')
        page.wait_for_function('document.documentElement.dataset.appReady === "true"')
        page.add_style_tag(content='html,*{scroll-behavior:auto!important}#toast{display:none!important}')
        check('standalone fallback boots', page.locator('.map-marker').count() == 22)
        page.screenshot(path=str(artifacts/'mini-home-mobile.png'),full_page=True)
        print('HOME GEOMETRY:',page.evaluate('''() => ['.top','.nav','.hero','#korea-quick-start','.section-head','.map-title','.map-controls','#world-map'].map(s=>{const r=document.querySelector(s).getBoundingClientRect();return {selector:s,y:r.y,height:r.height}})'''))
        check('mobile hero compact',page.locator('.hero').bounding_box()['height']<=260)
        print('MOBILE MAP TOP:',page.locator('#world-map').bounding_box()['y'])
        check('map closer to first screen',page.locator('#world-map').bounding_box()['y']<780)
        check('touch controls at least 44px',page.evaluate('''() => [...document.querySelectorAll('.nav button,.map-filter,.zoom-controls button')].every(e=>e.getBoundingClientRect().height>=44)'''))
        check('container top offset at least 56px',page.locator('.shell').bounding_box()['y']>=56)
        check('Korea quick start exists',page.locator('#korea-quick-start').count()==1)
        check('mobile opening timezone visible',page.locator('.quick-start-heading small').is_visible())
        if page.locator('#korea-quick-start').count():
            for city in ['busan','seoul']:
                page.locator(f'#korea-quick-start [data-stop="{city}"]').click()
                check('quick entry '+city,page.evaluate('HAMILTON_APP_TEST.state.stopId')==city and page.locator('#view-stop').is_visible())
                page.locator('nav [data-view="map"]').click()
        for stop_id in ['new-york', 'london', 'seoul', 'busan']:
            check(stop_id + ' dot matches geographic coordinate', page.evaluate('''id => {
                const p=HAMILTON_APP_TEST.projection(HAMILTON_APP_TEST.stop(id));
                const dot=document.querySelector(`.map-marker[data-stop="${id}"] .dot`);
                return Math.abs(+dot.getAttribute('cx')-p.x)<.001 && Math.abs(+dot.getAttribute('cy')-p.y)<.001;
            }''', stop_id))
        page.locator('[data-region-filter="asia"]').click()
        check('Asia filter wires and shows two cities', page.locator('.map-marker').count() == 2)
        check('Asia viewport fits selected region', page.locator('#world-map').get_attribute('viewBox') != '0 0 1000 500')
        before = page.locator('#world-map').get_attribute('viewBox')
        page.locator('#zoom-in').click()
        check('regional zoom changes viewport', page.locator('#world-map').get_attribute('viewBox') != before)
        page.locator('#zoom-reset').click()
        check('reset keeps selected region', page.locator('#world-map').get_attribute('viewBox') == before)
        # Continue with all-city fallback even when the failing old filter did not wire.
        page.evaluate('HAMILTON_APP_TEST.regionFilter("asia")')
        for stop_id in ['seoul','busan']:
            page.locator(f'.map-marker[data-stop="{stop_id}"] .dot').click()
            check(stop_id + ' opens matching detail', page.evaluate('HAMILTON_APP_TEST.state.stopId') == stop_id)
            if stop_id == 'seoul':
                page.locator('#stop-detail a[href="https://nol.yanolja.com/ticket/products/26015650"]').click()
                check('external ticket URL stays in safe text modal', page.locator('#mini-modal-text').is_visible() and 'nol.yanolja.com' in page.locator('#mini-modal-text').input_value())
                page.locator('button[data-modal-close]').first.click()
            page.locator('nav [data-view="map"]').click()
        page.locator('#region-grid [data-region-open="europe"]').click()
        page.locator('nav [data-view="map"]').click()
        check('return map synchronizes region', page.locator('.map-marker').count() == 1)
        page.locator('nav [data-view="plan"]').click()
        page.locator('#share-plan').click()
        check('missing native share API falls back to text', page.locator('#mini-modal-text').is_visible())
        page.locator('button[data-modal-close]').first.click()
        check('mobile has no horizontal overflow', page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'))
        check('no uncaught JS exceptions', not errors)
        page.locator('nav [data-view="map"]').click()
        page.screenshot(path=str(artifacts / 'mini-mobile.png'), full_page=True)
        browser.close()
finally:
    server.shutdown()
    server.server_close()
print(f'RESULT: {sum(ok for _,ok in checks)}/{len(checks)} passed')
if not all(ok for _,ok in checks):
    raise SystemExit(1)
