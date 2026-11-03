"""Render privacy-clean, real-app screenshots into editable note cards."""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
import argparse
import html
import sys
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, default=ROOT/'output/note-assets')
args=parser.parse_args()
args.output.mkdir(parents=True,exist_ok=True)
sys.stdout.reconfigure(encoding='utf-8')
server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(ROOT/'minitool')))
Thread(target=server.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{server.server_port}/index.html'
try:
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        context=browser.new_context(viewport={'width':390,'height':844},device_scale_factor=2)
        page=context.new_page()
        page.goto(url)
        page.wait_for_function('document.documentElement.dataset.appReady === "true"')
        page.add_style_tag(content='html,*{scroll-behavior:auto!important}#toast{display:none!important}')
        page.screenshot(path=str(args.output/'app-home.png'),full_page=True)
        screenshots=[]
        page.locator('#korea-quick-start').screenshot(path=str(args.output/'quick.png'))
        page.locator('.map-panel').screenshot(path=str(args.output/'map.png'))
        screenshots.append(('01-cover.png','HAMILTON · WORLD ATLAS','为了看汉密尔顿<br>我做了个小工具','查城市 · 看场馆 · 算预算 · 存计划','map.png','工科生的看剧准备笔记 / 非官方 · 非抢票器'))
        page.locator('#korea-quick-start [data-stop="seoul"]').click()
        page.locator('#detail-qty').select_option('2')
        page.locator('[data-stop-price="seoul"][data-tier="VIP"]').click()
        page.locator('.price-grid').screenshot(path=str(args.output/'prices.png'))
        page.locator('#detail-budget').screenshot(path=str(args.output/'budget.png'))
        # Capture the actual city panel, including data date and price disclaimer.
        page.locator('#stop-detail .detail-grid > div').first.screenshot(path=str(args.output/'seoul.png'))
        screenshots.append(('02-korea.png','KOREA · TICKET PREPARATION','首尔还是釜山？<br>先把信息放一起','韩国开票时间（北京时间）· 票档与票面预算','seoul.png','内置数据核验：2026-10-28 / 场次及余票请核对官方'))
        page.locator('nav [data-view="plan"]').click()
        page.locator('#plan-stop').select_option('seoul')
        page.locator('#plan-tier').select_option('A')
        page.locator('#plan-quantity').select_option('2')
        page.locator('#plan-note').fill('演示：先核对场次，再决定出行；这不是订单。')
        page.locator('#save-plan').click()
        page.locator('#view-plan .plan-grid > .panel').first.screenshot(path=str(args.output/'plan.png'))
        screenshots.append(('03-plan.png','MY THEATRE PLAN · DEMO','少翻几次攻略<br>存下自己的看剧计划','城市 · 意向日期 · 张数 · 备注','plan.png','演示计划，不是购票订单 / 信息只保存在本地'))
        # A 1080×1440 CSS layout: no copyrighted production photography.
        card=browser.new_page(viewport={'width':1080,'height':1440},device_scale_factor=1)
        for filename,kicker,title,subtitle,shot,foot in screenshots:
            import base64
            files=['quick.png','prices.png','budget.png'] if filename=='02-korea.png' else [shot]
            pictures=''.join('<img alt="实际工具截图" src="data:image/png;base64,'+base64.b64encode((args.output/item).read_bytes()).decode()+'">' for item in files)
            card.set_content(f'''<!doctype html><html lang="zh"><meta charset="utf-8"><style>
            *{{box-sizing:border-box}}body{{margin:0;background:#111b28;color:#fffdf8;font-family:'Microsoft YaHei','Segoe UI',sans-serif}}
            main{{width:1080px;height:1440px;padding:64px 64px 42px;display:flex;flex-direction:column}}
            .kicker{{font-size:21px;letter-spacing:4px;color:#d7b568;font-weight:700}}h1{{font-size:65px;line-height:1.3;letter-spacing:-2px;margin:28px 0 20px}}
            .subtitle{{font-size:24px;color:#c5cdd4;margin:0 0 34px}}.shot{{flex:1;min-height:0;border-radius:24px;background:#f2efe7;padding:20px;display:flex;justify-content:center;align-items:center;overflow:hidden}}
            img{{display:block;max-width:100%;max-height:100%;width:auto;height:auto;object-fit:contain}}.shot.stack{{flex-direction:column;gap:38px;padding:32px}}.stack img{{width:100%;max-height:43%;flex-shrink:1;min-height:0}}footer{{font-size:20px;color:#d7b568;margin-top:26px;line-height:1.5}}.badge{{float:right;background:#d7b568;color:#111b28;border-radius:999px;padding:8px 18px;font-size:20px}}
            </style><main><div class="kicker">{html.escape(kicker)}<span class="badge">v1.1</span></div><h1>{title}</h1><p class="subtitle">{html.escape(subtitle)}</p><div class="shot {'stack' if len(files)>1 else ''}">{pictures}</div><footer>{html.escape(foot)}</footer></main></html>''')
            card.screenshot(path=str(args.output/filename))
            print('Rendered:',args.output/filename)
        narrow=browser.new_page(viewport={'width':320,'height':700})
        narrow.goto(url)
        narrow.wait_for_function('document.documentElement.dataset.appReady === "true"')
        assert narrow.evaluate('document.documentElement.scrollWidth <= innerWidth+1'), '320px horizontal overflow'
        narrow.screenshot(path=str(args.output/'qa-320.png'),full_page=True)
        print('QA: 320px no horizontal overflow; isolated context contains no user plans')
        browser.close()
finally:
    server.shutdown()
    server.server_close()
