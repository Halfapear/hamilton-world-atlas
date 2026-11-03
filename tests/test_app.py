from pathlib import Path
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from functools import partial
from threading import Thread
import os
import sys
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
html=(ROOT/'index.html').read_text(encoding='utf-8')
checks=[]
sys.stdout.reconfigure(encoding='utf-8')
artifacts=ROOT/'output'/'playwright'
artifacts.mkdir(parents=True, exist_ok=True)
server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
Thread(target=server.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{server.server_port}/index.html'
def check(name, condition, detail=''):
    checks.append((name, bool(condition), detail)); print(('PASS' if condition else 'FAIL')+' '+name, flush=True)
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True, **({'channel':os.environ['ATLAS_BROWSER']} if os.environ.get('ATLAS_BROWSER') else {}))
    print(f'BROWSER: {os.environ.get("ATLAS_BROWSER") or "chromium"} {browser.version}', flush=True)
    page=browser.new_page(viewport={'width':1440,'height':1100}, accept_downloads=True)
    errors=[]
    external_requests=[]
    page.on('request',lambda r: external_requests.append(r.url) if r.url.startswith(('http://','https://')) and not r.url.startswith(url.rsplit('/',1)[0]+'/') else None)
    page.on('pageerror',lambda e: errors.append(str(e)))
    page.on('console',lambda m: errors.append(m.text) if m.type=='error' else None)
    page.goto(url,wait_until='domcontentloaded',timeout=10000)
    page.add_style_tag(content='html{scroll-behavior:auto!important} *{scroll-behavior:auto!important}')
    check('document title', 'Hamilton World Atlas' in page.title())
    check('app boot flag', page.locator('html').get_attribute('data-app-ready')=='true', page.locator('html').get_attribute('data-app-ready'))
    check('app test API exists', page.evaluate('typeof window.HAMILTON_APP_TEST')=='object')
    check('22 stops in data', page.evaluate('window.HAMILTON_APP_TEST.DATA.stops.length')==22)
    check('4 production groups', page.evaluate('window.HAMILTON_APP_TEST.DATA.productions.length')==4)
    check('22 map markers', page.locator('.map-marker').count()==22)
    check('4 production cards', page.locator('#production-list .prod-card').count()==4)
    check('dynamic count badges match data', page.locator('#metric-stops').inner_text().startswith('22') and page.locator('[data-region-filter="north-america"]').inner_text().endswith('19'))
    check('22 stop cards', page.locator('#stops-grid .stop-card').count()==22)
    check('Hamilton-only scope', 'KPOP' not in page.locator('body').inner_text() and '大麦' not in page.locator('body').inner_text())
    check('v1.1 metadata matches version badge',page.evaluate('HAMILTON_APP_TEST.DATA.meta.version')=='1.1' and page.locator('#app-version').inner_text()=='v1.1')
    check('map routes share geographic marker coordinates',page.evaluate('''() => {
      const app=HAMILTON_APP_TEST;
      const routes=[['.route-line','north-american-tour'],['.korea-line','korea-world-tour']];
      return routes.every(([selector,id])=>{
        const points=document.querySelector(selector).points;
        const stops=app.DATA.stops.filter(s=>s.productionId===id).sort((a,b)=>(a.routeOrder||0)-(b.routeOrder||0));
        return points.numberOfItems===stops.length&&stops.every((s,i)=>{
          const p=app.projection(s),q=points.getItem(i);
          return Math.abs(p.x-q.x)<.001&&Math.abs(p.y-q.y)<.001;
        });
      });
    }'''))
    alignment=page.evaluate('''() => {
      const app=HAMILTON_APP_TEST, lands=[...document.querySelectorAll('#map-content path.land')];
      return ['new-york','london','seoul','busan'].map(id=>{
        const s=app.stop(id),p=app.projection(s);
        const nearLand=[-2,0,2].some(dx=>[-2,0,2].some(dy=>lands.some(land=>land.isPointInFill(new DOMPoint(p.x+dx,p.y+dy)))));
        const dot=document.querySelector(`.map-marker[data-stop="${id}"] .dot`);
        return {id,nearLand,exact:Math.abs(+dot.getAttribute('cx')-p.x)<.001&&Math.abs(+dot.getAttribute('cy')-p.y)<.001};
      });
    }''')
    for landmark in alignment:
        check(f'{landmark["id"]} projected on or near land',landmark['nearLand'])
        check(f'{landmark["id"]} dot stays at geographic coordinate',landmark['exact'])
    # Map marker -> stop detail
    page.locator('.map-marker[data-stop="london"] circle.dot').click()
    check('click London map marker opens detail', page.locator('#view-stop').is_visible() and '伦敦' in page.locator('#stop-detail').inner_text())
    check('London official ticket link', page.locator('#stop-detail a[href="https://hamiltonmusical.com/london/tickets/"]').count()>=1)
    # Region -> production -> city hierarchy
    page.locator('nav [data-view="map"]').click()
    page.locator('#region-grid [data-region-open="asia"]').click()
    check('region card opens region layer', page.locator('#view-region').is_visible() and '亚洲' in page.locator('#region-detail').inner_text())
    check('region layer lists production before cities', page.locator('#region-detail [data-production="korea-world-tour"]').count()>=1)
    page.locator('#region-detail [data-production="korea-world-tour"]').first.click()
    check('region -> production navigation', page.locator('#view-production').is_visible() and '韩国世界巡演' in page.locator('#production-detail').inner_text())
    page.locator('#production-detail [data-stop="seoul"]').click()
    check('production -> city navigation', page.locator('#view-stop').is_visible() and '首尔' in page.locator('#stop-detail').inner_text())
    # Production hierarchy
    page.locator('nav [data-view="map"]').click()
    page.locator('[data-region-filter="all"]').click()
    page.locator('.map-marker[data-stop="london"] circle.dot').click()
    page.locator('#stop-detail [data-production="west-end"]').first.click()
    check('breadcrumb enters London production', page.locator('#view-production').is_visible() and '伦敦西区驻演' in page.locator('#production-detail').inner_text())
    check('London production has one stop', page.locator('#production-detail [data-stop="london"]').count()==1)
    page.locator('#production-detail [data-stop="london"]').click()
    check('production -> city navigation', page.locator('#view-stop').is_visible() and 'Victoria Palace Theatre' in page.locator('#stop-detail').inner_text())
    # Seoul price and ticket link
    page.locator('#stop-detail [data-view="stops"]').click()
    page.locator('#stop-search').fill('Seoul')
    check('search finds Seoul', page.locator('#stops-grid .stop-card').count()==1)
    page.locator('#stops-grid [data-stop="seoul"]').click()
    check('Seoul official NOL product link', page.locator('#stop-detail a[href="https://nol.yanolja.com/ticket/products/26015650"]').count()==1)
    check('Korea prices render five tiers', page.locator('#stop-detail [data-stop-price="seoul"]').count()==5)
    page.locator('#stop-detail [data-tier="VIP"][data-stop-price="seoul"]').click()
    page.locator('#detail-qty').select_option('2')
    check('VIP two-ticket estimate', '₩440,000' in page.locator('#detail-budget').inner_text(), page.locator('#detail-budget').inner_text())
    page.locator('#detail-qty').select_option('3')
    check('quantity updates budget', '₩660,000' in page.locator('#detail-budget').inner_text(), page.locator('#detail-budget').inner_text())
    page.locator('#detail-date').fill('2027-04-01')
    page.locator('#save-stop-plan').click()
    check('invalid date rejected', '日期超出' in page.locator('#toast').inner_text())
    page.locator('#detail-date').fill('2027-02-02')
    page.locator('#detail-note').fill('Test note')
    page.locator('#save-stop-plan').click()
    check('valid plan saved and navigates', page.locator('#view-plan').is_visible() and '首尔' in page.locator('#saved-plan').inner_text())
    check('plan keeps VIP and quantity', '3 张' in page.locator('#saved-plan').inner_text() and '₩660,000' in page.locator('#saved-plan').inner_text(), page.locator('#saved-plan').inner_text())
    # Map filter + zoom
    page.locator('nav [data-view="map"]').click()
    page.locator('[data-region-filter="europe"]').click()
    check('Europe filter leaves one marker', page.locator('.map-marker').count()==1)
    check('Europe filter is active', page.locator('[data-region-filter="europe"]').get_attribute('class').find('active')>=0)
    before=page.locator('#world-map').get_attribute('viewBox')
    check('Europe filter fits the viewport',before!='0 0 1000 500')
    page.locator('#zoom-in').click()
    after=page.locator('#world-map').get_attribute('viewBox')
    check('map zoom changes viewBox', before!=after, f'{before} -> {after}')
    page.locator('#zoom-reset').click()
    check('map zoom reset returns selected region', page.locator('#world-map').get_attribute('viewBox')==before)
    page.locator('[data-region-filter="all"]').click()
    page.locator('.map-marker[data-stop="london"]').focus()
    page.keyboard.press('Enter')
    check('keyboard opens map marker detail',page.locator('#view-stop').is_visible() and '伦敦' in page.locator('#stop-detail').inner_text())
    page.locator('nav [data-view="map"]').click()
    page.locator('[data-region-filter="asia"]').click()
    page.locator('#world-map').scroll_into_view_if_needed()
    bounds=page.locator('#world-map').bounding_box()
    before_pan=page.locator('#world-map').get_attribute('viewBox')
    page.mouse.move(bounds['x']+bounds['width']*.2,bounds['y']+bounds['height']*.8)
    page.mouse.down()
    page.mouse.move(bounds['x']+bounds['width']*.3,bounds['y']+bounds['height']*.8,steps=5)
    page.mouse.up()
    check('dragging map pans viewport',page.locator('#world-map').get_attribute('viewBox')!=before_pan)
    page.locator('#zoom-reset').click()
    page.locator('[data-region-filter="all"]').click()
    check('global filter restores 22 markers', page.locator('.map-marker').count()==22)
    check('global filter resets world viewport',page.locator('#world-map').get_attribute('viewBox')=='0 0 1000 500')
    page.locator('[data-region-filter="north-america"]').click()
    for stop_id in page.evaluate('HAMILTON_APP_TEST.DATA.stops.filter(s=>s.region==="north-america").map(s=>s.id)'):
        try:
            page.locator(f'.map-marker[data-stop="{stop_id}"] .dot').click(timeout=1500)
            check(f'North America marker clicks correct city: {stop_id}',page.evaluate('HAMILTON_APP_TEST.state.stopId')==stop_id and page.locator('#view-stop').is_visible())
        except Exception as error:
            check(f'North America marker clicks correct city: {stop_id}',False,str(error).splitlines()[0])
        page.locator('nav [data-view="map"]').click()
    page.locator('[data-region-filter="all"]').click()
    page.locator('#region-grid [data-region-open="asia"]').click()
    page.locator('nav [data-view="map"]').click()
    check('region navigation synchronizes returned map',page.locator('.map-marker').count()==2 and 'active' in page.locator('[data-region-filter="asia"]').get_attribute('class'))
    page.locator('[data-region-filter="asia"]').click()
    page.locator('#zoom-in').click()
    check('Korea stays inside zoomed viewport',page.evaluate('''() => {
      const box=document.querySelector('#world-map').viewBox.baseVal;
      return [...document.querySelectorAll('.map-marker .dot')].every(dot=>{
        const x=+dot.getAttribute('cx'),y=+dot.getAttribute('cy');
        return x>=box.x&&x<=box.x+box.width&&y>=box.y&&y<=box.y+box.height;
      });
    }'''))
    page.locator('[data-region-filter="all"]').click()
    # Production filters
    page.locator('nav [data-view="stops"]').click()
    page.locator('#stop-search').fill('Dream Theatre')
    check('venue search finds Busan', page.locator('#stops-grid .stop-card').count()==1 and '釜山' in page.locator('#stops-grid').inner_text())
    page.locator('#stop-search').fill('')
    page.locator('#stop-region').select_option('asia')
    check('Asia filter returns two stops', page.locator('#stops-grid .stop-card').count()==2)
    page.locator('#stop-region').select_option('all')
    page.locator('#stop-production').select_option('north-american-tour')
    check('North American tour filter returns 18 stops', page.locator('#stops-grid .stop-card').count()==18)
    # Guide, about and links
    page.locator('nav [data-view="guide"]').click()
    check('guide shows four official production links', page.locator('#guide-production-list .stop-card').count()==4)
    check('guide warns third-party passwords not collected', '不收集第三方密码' in page.locator('#view-guide').inner_text())
    page.locator('nav [data-view="about"]').click()
    check('about introduction populated', 'Lin-Manuel Miranda' in page.locator('#about-description').inner_text())
    check('about shows four productions', page.locator('#about-productions .stop-card').count()==4)
    check('about includes official Korea cast list', page.locator('#korea-cast .stop-card').count()==10)
    check('latest Korea update visible', '2026-10-27' in page.locator('#about-timeline').inner_text())
    # Plan, checklist, export
    page.locator('nav [data-view="plan"]').click()
    page.locator('#plan-stop').select_option('busan')
    page.locator('#plan-tier').select_option('R')
    page.locator('#plan-quantity').select_option('2')
    page.locator('#plan-date').fill('2026-12-20')
    page.locator('#plan-note').fill('Browser test')
    page.locator('#save-plan').click()
    check('plan form saves selected Busan date and tier', '釜山' in page.locator('#saved-plan').inner_text() and '₩360,000' in page.locator('#saved-plan').inner_text())
    page.locator('[data-check="official"]').check()
    check('checklist responds to user input', page.locator('[data-check="official"]').is_checked())
    page.reload(wait_until='domcontentloaded')
    page.locator('nav [data-view="plan"]').click()
    check('plan survives reload with original storage key',page.evaluate('JSON.parse(localStorage.getItem("hamilton-world-atlas-v1")).plan.stopId')=='busan' and '₩360,000' in page.locator('#saved-plan').inner_text())
    check('checklist survives reload',page.locator('[data-check="official"]').is_checked())
    with page.expect_download() as download_info:
        page.locator('#export-json').click()
    download=download_info.value
    check('JSON plan export downloads', download.suggested_filename=='hamilton-world-atlas-plan.json', download.suggested_filename)
    with page.expect_download() as download_info:
        page.locator('#download-ics').click()
    download=download_info.value
    check('ICS reminder export downloads', download.suggested_filename=='Hamilton-busan-reminder.ics', download.suggested_filename)
    check('no uncaught JS errors', len(errors)==0, '; '.join(errors))
    check('offline map loads no external resources',len(external_requests)==0,'; '.join(external_requests))
    # screenshot final home page
    page.locator('nav [data-view="map"]').click()
    page.add_style_tag(content='#toast{display:none!important}')
    page.screenshot(path=str(artifacts/'preview-desktop.png'),full_page=True)
    page.locator('#world-map').screenshot(path=str(artifacts/'map-global.png'))
    for region in ['north-america','europe','asia']:
        page.locator(f'[data-region-filter="{region}"]').click()
        page.locator('#world-map').screenshot(path=str(artifacts/f'map-{region}-desktop.png'))
    page.locator('[data-region-filter="all"]').click()
    page.set_viewport_size({'width':390,'height':844})
    page.evaluate('scrollTo(0,0)')
    check('mobile hero compact',page.locator('.hero').bounding_box()['height']<=260)
    check('mobile map closer to first screen',page.locator('#world-map').bounding_box()['y']<780)
    check('mobile touch controls at least 44px',page.evaluate('''() => [...document.querySelectorAll('.nav button,.map-filter,.zoom-controls button')].every(e=>e.getBoundingClientRect().height>=44)'''))
    check('Korea quick start exists',page.locator('#korea-quick-start').count()==1)
    check('mobile opening timezone visible',page.locator('.quick-start-heading small').is_visible())
    if page.locator('#korea-quick-start').count():
        for city in ['busan','seoul']:
            page.locator(f'#korea-quick-start [data-stop="{city}"]').click()
            check(f'quick entry opens {city}',page.evaluate('HAMILTON_APP_TEST.state.stopId')==city and page.locator('#view-stop').is_visible())
            page.locator('nav [data-view="map"]').click()
        check('quick start preserves data date', '2026-10-28' in page.locator('#korea-quick-start').inner_text())
        page.evaluate('scrollTo(0,0)')
    check('mobile layout has no horizontal overflow', page.evaluate('document.documentElement.scrollWidth <= window.innerWidth + 1'), f"{page.evaluate('document.documentElement.scrollWidth')} vs {page.evaluate('window.innerWidth')}")
    page.screenshot(path=str(artifacts/'preview-mobile.png'),full_page=True)
    page.locator('[data-region-filter="asia"]').click()
    page.locator('.map-marker[data-stop="seoul"] .dot').click()
    check('mobile Seoul marker opens correct detail',page.locator('#view-stop').is_visible() and page.evaluate('HAMILTON_APP_TEST.state.stopId')=='seoul')
    page.locator('nav [data-view="map"]').click()
    page.locator('.map-marker[data-stop="busan"] .dot').click()
    check('mobile Busan marker opens correct detail',page.locator('#view-stop').is_visible() and page.evaluate('HAMILTON_APP_TEST.state.stopId')=='busan')
    page.locator('nav [data-view="map"]').click()
    page.locator('#world-map').screenshot(path=str(artifacts/'map-asia-mobile.png'))
    browser.close()
server.shutdown()
server.server_close()
for i,(name,ok,detail) in enumerate(checks,1):
 print(f'{i:02d}. {"PASS" if ok else "FAIL"} - {name}'+(f' ({detail})' if detail else ''))
print(f'RESULT: {sum(ok for _,ok,_ in checks)}/{len(checks)} passed')
if not all(ok for _,ok,_ in checks): raise SystemExit(1)
