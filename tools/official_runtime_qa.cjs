const fs = require('node:fs');
const crypto = require('node:crypto');
const http = require('node:http');
const { chromium } = require('playwright');

const path = require('node:path');
const root = path.resolve(__dirname, '..');
const output = root + '/output/official-runtime-v1.2';
fs.mkdirSync(output,{recursive:true});
const runtimeUrl = 'https://miniapp-sandbox.xiaohongshu.com/simulator/releases/v0.2.2-9d88c5546499-0b9c738464e0';

(async () => {
  const isolated = true;
  const browser = await chromium.launch({headless:true,channel:'msedge'});
  const page = await browser.newPage({viewport:{width:1280,height:960}});
  if (!page) throw new Error('Expected task creator page is missing');
  let qaServer;
  if (isolated) {
    qaServer = http.createServer((request, response) => {
      response.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
      response.end('<!doctype html><html><head><title>Hamilton isolated official-runtime diagnostic</title></head><body><p>Task-only preview diagnostic; no account login.</p></body></html>');
    });
    await new Promise(resolve => qaServer.listen(0, '127.0.0.1', resolve));
    await page.goto('http://127.0.0.1:' + qaServer.address().port, { waitUntil: 'domcontentloaded' });
  }
  page.on('pageerror', error => console.log('RUNTIME_PAGEERROR=' + error.message));
  page.on('console', message => {
    if (message.text().includes('miniapp') || message.type() === 'error') console.log('RUNTIME_CONSOLE=' + message.text().slice(0,1000));
  });
  const zip = fs.readFileSync(root + '/output/Hamilton_World_Atlas_XHS_MiniTool_v1.2-compliant.zip');
  const hash = crypto.createHash('sha256').update(zip).digest('hex').toUpperCase();
  console.log('ZIP_SHA256=' + hash);
  await page.evaluate(url => {
    if (document.getElementById('hamilton-task-runtime-check')) throw new Error('QA frame already exists');
    const iframe = document.createElement('iframe');
    iframe.id = 'hamilton-task-runtime-check';
    iframe.title = 'Hamilton task-only official runtime QA';
    iframe.style.cssText = 'position:fixed;right:0;top:0;width:420px;height:900px;z-index:10000;border:0;background:white';
    iframe.src = url;
    window.__hamiltonRuntimeQa = { events: [], responses: {}, counter: 0, ready: false };
    iframe.addEventListener('load', () => {
      const channel = new MessageChannel();
      const state = window.__hamiltonRuntimeQa;
      state.port = channel.port1;
      channel.port1.onmessage = event => {
        const message = event.data;
        if (message.type === 'ready') state.ready = message;
        if (message.type === 'response') state.responses[message.requestId] = message;
        if (message.type === 'event') state.events.push({ event: message.event, payload: message.payload });
      };
      channel.port1.start();
      iframe.contentWindow.postMessage({ type: 'miniapp-simulator:connect', protocolVersion: 7,
        sessionId: 'hamilton-isolated-v12-20261106', appId: '6aea400c74b80400158a253a',
        businessLine: 'creator', options: { viewport: { width: 390, height: 844 } },
        hostApiMethods: [], hostApiStubs: {}, tracker: false }, new URL(url).origin, [channel.port2]);
    });
    document.body.appendChild(iframe);
  }, runtimeUrl);
  await page.waitForFunction(() => Boolean(window.__hamiltonRuntimeQa?.ready), null, { polling: 100, timeout: 30000 });
  console.log('OFFICIAL_RUNTIME_READY=' + JSON.stringify(await page.evaluate(() => window.__hamiltonRuntimeQa.ready)));
  const result = await page.evaluate(async bytes => {
    const state = window.__hamiltonRuntimeQa;
    const id = 'qa-load-zip';
    state.port.postMessage({ type: 'request', requestId: id, method: 'loadZip',
      args: [{ buffer: Uint8Array.from(bytes).buffer, options: { entry: 'index.html' } }] });
    return id;
  }, [...zip]);
  await page.waitForFunction(id => Boolean(window.__hamiltonRuntimeQa.responses[id]), result, { polling: 100, timeout: 30000 });
  const response = await page.evaluate(id => window.__hamiltonRuntimeQa.responses[id], result);
  console.log('OFFICIAL_RUNTIME_LOAD=' + JSON.stringify(response));
  console.log('RUNTIME_EVENTS=' + JSON.stringify(await page.evaluate(() => window.__hamiltonRuntimeQa.events)));
  console.log('FRAMES=' + JSON.stringify(page.frames().map(f => ({ name: f.name(), url: f.url() }))));
  if (!response.ok) throw new Error('Official runtime rejected ZIP: ' + JSON.stringify(response.error));
  let guest = page.frames().find(f => f.url().startsWith(runtimeUrl + '/app/') && f.url().includes('index.html'));
  if (!guest) throw new Error('Official service-worker guest frame missing');
  await guest.waitForFunction(() => document.documentElement.dataset.appReady === 'true', null, { polling: 100, timeout: 20000 });
  const checks = [];
  const check = (name, passed, details) => {
    checks.push({ name, passed: Boolean(passed), details });
    console.log((passed ? 'PASS ' : 'FAIL ') + name + (details === undefined ? '' : ' ' + JSON.stringify(details)));
  };
  console.log('GUEST_SNAPSHOT=' + (await guest.locator('body').ariaSnapshot()).slice(0,8000));
  check('Official runtime boots 22 map cities', await guest.locator('.map-marker').count() === 22);
  check('Native SDK is injected by official simulator', await guest.evaluate(() => Boolean(window.xhs?.miniTool)));
  check('No horizontal overflow', await guest.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
  for (const city of ['new-york','london','seoul','busan']) {
    check(city + ' dot uses shared geographic projection', await guest.evaluate(id => {
      const projected = HAMILTON_APP_TEST.projection(HAMILTON_APP_TEST.stop(id));
      const dot = document.querySelector('.map-marker[data-stop="' + id + '"] .dot');
      return Math.abs(Number(dot.getAttribute('cx')) - projected.x) < .001 && Math.abs(Number(dot.getAttribute('cy')) - projected.y) < .001;
    }, city));
  }
  await guest.locator('[data-region-filter="asia"]').click();
  check('Asia filter shows Seoul and Busan only', await guest.locator('.map-marker').count() === 2);
  const regionalBox = await guest.locator('#world-map').getAttribute('viewBox');
  await guest.locator('#zoom-in').click();
  check('Regional zoom changes viewBox', await guest.locator('#world-map').getAttribute('viewBox') !== regionalBox);
  await guest.locator('#zoom-reset').click();
  check('Zoom reset preserves region', await guest.locator('#world-map').getAttribute('viewBox') === regionalBox);
  for (const city of ['seoul','busan']) {
    await guest.locator('.map-marker[data-stop="' + city + '"] .dot').click();
    check(city + ' map click opens correct details', await guest.evaluate(id => HAMILTON_APP_TEST.state.stopId === id, city));
    await guest.locator('nav [data-view="map"]').click();
  }
  await guest.locator('#korea-quick-start [data-stop="seoul"]').click();
  await guest.locator('#detail-qty').selectOption('3');
  await guest.locator('[data-stop-price="seoul"][data-tier="A"]').click();
  check('Korea budget calculates A tier x3', (await guest.locator('#detail-budget').textContent()).includes('300,000'));
  await guest.locator('#stop-detail a[href="https://nol.yanolja.com/ticket/products/26015650"]').click();
  check('External booking URL stays in text dialog', await guest.locator('#mini-modal-text').isVisible() && (await guest.locator('#mini-modal-text').inputValue()).includes('nol.yanolja.com'));
  await guest.locator('button[data-modal-close]').first().click();
  await guest.locator('#detail-note').fill('TASK QA ONLY 2026-11-06');
  await guest.locator('#save-stop-plan').click();
  check('Plan form receives selected city and quantity', await guest.locator('#plan-stop').inputValue() === 'seoul' && await guest.locator('#plan-quantity').inputValue() === '3');
  console.log('SAVED_PLAN=' + await guest.locator('#saved-plan').textContent());
  check('Official simulator storage reports persistence', (await guest.locator('#saved-plan').textContent()).includes('已保存到本地'));
  await guest.locator('#export-json').click();
  check('Backup text contains only test plan', (await guest.locator('#mini-modal-text').inputValue()).includes('TASK QA ONLY 2026-11-06'));
  await guest.locator('button[data-modal-close]').first().click();
  const invoke = async (method, args = []) => {
    const id = await page.evaluate(({method,args}) => {
      const state = window.__hamiltonRuntimeQa;
      const id = 'qa-command-' + (++state.counter);
      state.port.postMessage({type:'request',requestId:id,method,args});
      return id;
    }, {method,args});
    await page.waitForFunction(id => Boolean(window.__hamiltonRuntimeQa.responses[id]), id, {polling:100,timeout:20000});
    const response = await page.evaluate(id => window.__hamiltonRuntimeQa.responses[id],id);
    if (!response.ok) throw new Error(method + ' failed: ' + JSON.stringify(response.error));
    return response.result;
  };
  await invoke('reload');
  guest = page.frames().find(f => f.url().startsWith(runtimeUrl + '/app/') && f.url().includes('index.html'));
  await guest.waitForFunction(() => document.documentElement.dataset.appReady === 'true', null, {polling:100,timeout:20000});
  await guest.locator('nav [data-view="plan"]').click();
  check('Plan persists after official runtime reload', await guest.locator('#plan-stop').inputValue() === 'seoul' && await guest.locator('#plan-quantity').inputValue() === '3' && await guest.locator('#plan-note').inputValue() === 'TASK QA ONLY 2026-11-06');
  if (isolated) {
    const countBefore = await page.evaluate(() => window.__hamiltonRuntimeQa.events.length);
    console.log('SHARE_API=' + JSON.stringify(await guest.evaluate(() => ({miniTool:typeof window.xhs?.miniTool,postNote:typeof window.xhs?.miniTool?.postNote}))));
    await guest.locator('#share-plan').click();
    await guest.waitForFunction(() => Boolean(document.querySelector('#toast.show')) || document.querySelector('#mini-modal-text')?.offsetHeight > 0, null, {polling:100,timeout:15000});
    const outcome = await guest.evaluate(() => ({toast:document.querySelector('#toast')?.textContent, modal:document.querySelector('#mini-modal-text')?.offsetHeight > 0 ? document.querySelector('#mini-modal-text').value : '',body:document.body.innerText.slice(-1600)}));
    console.log('SHARE_UI_RESULT=' + JSON.stringify(outcome));
    console.log('SHARE_RESULT=' + JSON.stringify(await page.evaluate(count => window.__hamiltonRuntimeQa.events.slice(count).filter(e=>e.event !== 'screenShot'),countBefore)).slice(0,6000));
    console.log('SIMULATOR_AFTER_SHARE=' + (await page.frames().find(f=>f.url()===runtimeUrl).locator('body').ariaSnapshot()).slice(-7000));
    check('Share action gives explicit user feedback in simulator', Boolean(outcome.modal) || /已唤起|无法/.test(outcome.toast), {toast:outcome.toast, hasFallback:Boolean(outcome.modal)});
    if (outcome.modal) await guest.locator('button[data-modal-close]').first().click();
  }
  await guest.locator('nav [data-view="map"]').click();
  await guest.locator('[data-region-filter="all"]').click();
  await invoke('router.redirectTo',['minitool']);
  await guest.locator('#world-map').screenshot({path: output + '/official-runtime-map-qa.png', animations: 'disabled'});
  await guest.locator('body').screenshot({path: output + '/official-runtime-qa.png', animations: 'disabled'});
  check('Official simulator enters minitool route', await invoke('router.getRoute') === 'minitool');
  await page.frames().find(f=>f.url()===runtimeUrl).getByRole('button',{name:'返回',exact:true}).last().click();
  let backRoute = await invoke('router.getRoute');
  for (let attempt=0; backRoute !== 'note' && attempt<12; attempt++) {
    await new Promise(resolve => setTimeout(resolve,250));
    backRoute = await invoke('router.getRoute');
  }
  check('Official top back returns to note preview', backRoute === 'note', {route:backRoute});
  await invoke('router.redirectTo',['minitool']);
  guest = page.frames().find(f => f.url().startsWith(runtimeUrl + '/app/') && f.url().includes('index.html'));
  if (!guest) throw new Error('Guest must be restored after top back');
  await guest.waitForFunction(() => document.documentElement.dataset.appReady === 'true', null, {polling:100,timeout:20000});
  await guest.locator('nav [data-view="map"]').click();
  await guest.locator('#lead-layer-toggle').check();
  check('Optional lead layer has seven hollow markers',await guest.locator('.lead-marker').count()===7);
  await guest.locator('[data-region-filter="asia"]').click();
  check('Lead layer does not change official count',await guest.locator('.map-marker').count()===2);
  await guest.locator('nav [data-view="leads"]').click();
  check('Separate source cards retain seven leads',await guest.locator('.lead-card').count()===7);
  await guest.locator('#view-leads button[data-lead="lead-shanghai"]').click();
  check('Source detail labels unread original', (await guest.locator('#lead-dialog').textContent()).includes('访问失败'));
  await guest.locator('button[data-lead-close]').click();
  await guest.locator('nav [data-view="map"]').click();
  check('Product badge v1.2',await guest.locator('#app-version').textContent()==='v1.2');
  const finalEvents = await page.evaluate(() => window.__hamiltonRuntimeQa.events);
  check('No official guest error event', !finalEvents.some(event => event.event === 'error'), finalEvents.filter(event => event.event === 'error'));
  const report = { version:'1.2', testedAt:new Date().toISOString(), date: '2026-11-06', mode: isolated ? 'official runtime in isolated headless Edge; not creator account acceptance or real device' : 'official runtime in background creator task page', zipHash: hash, runtimeUrl, checks, events: finalEvents };
  fs.writeFileSync(output + '/official-runtime-qa-report.json', JSON.stringify(report,null,2));
  console.log('RESULT=' + checks.filter(c => c.passed).length + '/' + checks.length);
  if (isolated) { await browser.close(); await new Promise(resolve => qaServer.close(resolve)); }
  if (checks.some(c => !c.passed)) throw new Error('Official runtime QA includes a failing check');
  process.exit(0);
})().catch(error => { console.error(error.stack); process.exit(1); });
