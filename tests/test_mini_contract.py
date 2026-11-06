"""Documented platform-contract simulations, NOT real App acceptance tests."""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[1]
server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(ROOT/'minitool')))
Thread(target=server.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{server.server_port}/index.html'
checks=[]
def check(name,ok):
    checks.append(bool(ok))
    print(('PASS ' if ok else 'FAIL ')+name,flush=True)
try:
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        page=browser.new_page(viewport={'width':390,'height':844})
        page.add_init_script('''window.xhs={launchOptions:{miniToolEnv:{buildVersion:9490001}},miniTool:{
            getStorage:async()=>({data:null}),setStorage:async()=>{throw Error('native write failed')},
            getWindowInfo:async()=>({safeArea:{left:0,top:24,right:390,bottom:810,width:390,height:786},
                windowWidth:390,windowHeight:844,screenWidth:390,screenHeight:844,
                pixelRatio:1,statusBarHeight:24,screenTop:0,
                menuButtons:{back:{left:8,top:24,right:48,bottom:88,width:40,height:64},me:null,share:null}})
        }};''')
        page.goto(url)
        page.wait_for_function('document.documentElement.dataset.appReady === "true"')
        check('native menu rectangle avoided',page.locator('.shell').bounding_box()['y']>=96)
        page.evaluate('''window.xhs.miniTool.getWindowInfo=async()=>({safeArea:{top:24},
            menuButtons:{back:{bottom:112},me:null,share:null}});window.dispatchEvent(new Event('resize'));''')
        page.wait_for_timeout(150)
        check('window resize updates native menu avoidance',page.locator('.shell').bounding_box()['y']>=120)
        page.evaluate("document.documentElement.classList.remove('supports-flex-gap')")
        check('Flex gap baseline uses actual margins',page.evaluate("parseFloat(getComputedStyle(document.querySelectorAll('.nav button')[1]).marginLeft)>=2"))
        check('new lead confidence row has flex-gap fallback',page.evaluate("parseFloat(getComputedStyle(document.querySelector('.confidence-strip button')).marginLeft)>=8"))
        page.locator('nav [data-view="leads"]').click()
        check('new lead card has vertical margin fallback',page.evaluate("parseFloat(getComputedStyle(document.querySelector('.lead-card h3')).marginTop)>=10"))
        check('new lead grid retains legacy grid-gap',page.evaluate("getComputedStyle(document.querySelector('.lead-grid')).gridRowGap==='12px'"))
        css=(ROOT/'src/tour-leads.css').read_text(encoding='utf-8')
        check('dialog explicit legacy viewport edges', 'left:0;top:0;right:0;bottom:0;inset:0' in css)
        page.locator('nav [data-view="map"]').click()
        check('production card baseline separates icon and text',page.evaluate("parseFloat(getComputedStyle(document.querySelector('.prod-card > :nth-child(2)')).marginLeft)>=11"))
        page.locator('#korea-quick-start [data-stop="busan"]').click()
        check('stop card baseline separates vertically stacked fields',page.evaluate("parseFloat(getComputedStyle(document.querySelector('.stop-card > :nth-child(2)')).marginTop)>=8"))
        page.locator('nav [data-view="plan"]').click()
        page.locator('#plan-note').fill('contract test')
        page.locator('#save-plan').click()
        page.wait_for_timeout(150)
        check('native write failure not reported saved','未持久保存' in page.locator('#saved-plan').inner_text())
        check('native write failure notice','未能保存' in page.locator('#toast').inner_text())
        check('native failure does not silently use legacy store',page.evaluate("localStorage.getItem('hamilton-world-atlas-v1')===null"))
        page.evaluate('() => {window.xhs.miniTool.setStorage=async()=>({errMsg:"setStorage:ok"})}')
        page.locator('#save-plan').click()
        page.wait_for_function('document.querySelector("#saved-plan").textContent.includes("已保存到本地")')
        page.evaluate('() => {window.xhs.miniTool.setStorage=async()=>{throw Error("checkbox write failed")}}')
        page.locator('[data-check="official"]').check()
        page.wait_for_timeout(150)
        check('checkbox write failure refreshes saved status','未持久保存' in page.locator('#saved-plan').inner_text())
        check('checkbox write failure gives notice','未能保存' in page.locator('#toast').inner_text())
        page.close()
        page=browser.new_page(viewport={'width':390,'height':844})
        page.add_init_script("Object.defineProperty(window,'localStorage',{get(){throw Error('denied')}})")
        page.goto(url)
        page.wait_for_function('document.documentElement.dataset.appReady === "true"')
        page.locator('nav [data-view="plan"]').click()
        page.locator('#save-plan').click()
        page.wait_for_timeout(150)
        check('no storage keeps honest volatile status','未持久保存' in page.locator('#saved-plan').inner_text())
        browser.close()
finally:
    server.shutdown();server.server_close()
print(f'RESULT: {sum(checks)}/{len(checks)} passed (contract simulation only)')
if not all(checks):raise SystemExit(1)
