/* Shared v1.2 provenance UI. Leads never enter booking or saved-plan data. */
let leadLayerEnabled=false, leadReturnFocus=null;
const tourLeads=()=>DATA.tourLeads||[];
const leadLinkTarget=()=>document.body.classList.contains('mini-container')?'':' target="_blank"';
function mapVisiblePoints(){
  const points=DATA.stops.filter(s=>state.region==='all'||s.region===state.region);
  return leadLayerEnabled?points.concat(tourLeads().filter(s=>state.region==='all'||s.region===state.region)):points;
}
function sourceTime(value){return value?value.replace('T',' ').replace('+08:00','（北京时间）'):'未独立核实';}
function leadCard(lead){
  return '<article class="lead-card"><div class="lead-card-top"><span class="lead-status">未官宣</span><span class="lead-kind">WORLD TOUR · 亚洲线索</span></div>'+
    '<h3>'+esc(lead.city)+' <small>'+esc(lead.cityEn)+'</small></h3><p class="lead-date">'+esc(lead.dateText)+'</p><p>'+esc(lead.venueText)+'</p>'+
    '<div class="lead-provenance"><strong>'+esc(lead.evidenceLevel)+'</strong><span>'+esc(lead.verificationStatus)+'</span></div>'+
    '<div class="lead-card-bottom"><small>不可据此订机酒</small><button class="btn" data-lead="'+esc(lead.id)+'">查看依据 ↗</button></div></article>';
}
function showLead(id){
  const lead=tourLeads().find(s=>s.id===id);
  if(!lead)return;
  leadReturnFocus=document.activeElement;
  const sources=lead.sources.map(s=>'<article class="lead-source"><h4>'+esc(s.title)+'</h4><p>原站状态：'+esc(s.accessStatus)+'</p><p>公布日期：'+esc(s.publicationDate||'未知')+' · '+esc(s.publicationNote)+'</p><p>尝试读取：'+esc(sourceTime(s.attemptedAt))+'</p>'+
    (s.url?'<a class="lead-source-url" href="'+esc(s.url)+'"'+leadLinkTarget()+' rel="noopener">'+esc(s.url)+'</a>':'<p>摘要未提供独立原站链接。</p>')+'</article>').join('');
  $('#lead-dialog-body').innerHTML='<span class="lead-status">未官宣 · 不等于官方排期</span><h2 id="lead-dialog-title">'+esc(lead.city)+' / '+esc(lead.cityEn)+'</h2>'+
    '<p class="lead-date">'+esc(lead.dateText)+'</p><p>'+esc(lead.venueText)+'</p><div class="lead-warning">不可据此订机酒。日期与场馆尚未独立核实，不能据此推断开票或余票。</div>'+
    '<p>证据性质：'+esc(lead.evidenceLevel)+'<br>核验状态：'+esc(lead.verificationStatus)+'<br>摘要整理：'+esc(sourceTime(lead.receivedAt))+'<br>独立核验：'+esc(sourceTime(lead.verifiedAt))+'<br>地图定位：城市中心，非剧院坐标</p>'+
    sources+'<p class="footnote">'+esc(lead.changeNote)+'</p>';
  $('#lead-dialog').classList.remove('hidden');
  document.body.classList.add('lead-dialog-open');
  $('#lead-dialog button[data-lead-close]').focus();
}
function closeLead(){
  $('#lead-dialog').classList.add('hidden');
  document.body.classList.remove('lead-dialog-open');
  if(leadReturnFocus&&document.contains(leadReturnFocus))leadReturnFocus.focus();
}
function renderLeadMap(){
  const group=$('#map-leads');
  if(!group)return;
  const visible=leadLayerEnabled?tourLeads().filter(s=>state.region==='all'||s.region===state.region):[];
  const scale=mapViewport().width/1000/state.zoom;
  const offsets={'lead-shanghai':[-15,18],'lead-beijing':[-14,-17],'lead-tokyo':[16,-16],'lead-taipei':[17,-3],'lead-kaohsiung':[17,15],'lead-hong-kong':[-16,-8],'lead-manila':[17,18]};
  group.innerHTML=visible.map(s=>{
    const p=projection(s),offset=offsets[s.id]||[16,-16],tx=p.x+offset[0]*scale,ty=p.y+offset[1]*scale;
    return '<g class="lead-marker" data-lead="'+esc(s.id)+'" tabindex="0" role="button" aria-label="'+esc(s.city)+'，未官宣，查看依据">'+
      '<title>'+esc(s.city)+' · 未官宣 · 不可据此订机酒</title><circle class="lead-hit" cx="'+p.x+'" cy="'+p.y+'" r="'+8*scale+'"/>'+
      '<circle class="lead-dot" cx="'+p.x+'" cy="'+p.y+'" r="'+4.5*scale+'" style="stroke-width:'+1.8*scale+'"/>'+
      '<line class="lead-leader" x1="'+p.x+'" y1="'+p.y+'" x2="'+tx+'" y2="'+ty+'"/>'+
      '<text x="'+tx+'" y="'+ty+'" text-anchor="'+(offset[0]<0?'end':'start')+'" style="font-size:'+8*scale+'px;stroke-width:'+2.8*scale+'px">'+esc(s.city)+' · 未官宣</text></g>';
  }).join('');
  $('#lead-map-warning').classList.toggle('hidden',!leadLayerEnabled);
  $('#lead-layer-count').textContent=leadLayerEnabled?'当前图层：'+visible.length+' 条未官宣线索':'默认仅显示已确认站点';
}
function initializeTourLeads(){
  const leadCount=tourLeads().length;
  const navButton=document.createElement('button');
  navButton.dataset.view='leads';navButton.textContent='巡演线索';
  $('.nav').insertBefore(navButton,$('.nav [data-view="guide"]'));
  const section=document.createElement('section');
  section.className='view';section.id='view-leads';
  section.innerHTML='<div class="section lead-intro"><div class="eyebrow">WORLD TOUR · WATCHLIST</div><div class="section-head"><div><h2>下一幕，尚待官宣。</h2><p>'+leadCount+' 条亚洲巡演线索，单独整理，不属于正式演出站点。</p></div><span class="lead-status">未官宣</span></div>'+
    '<div class="lead-warning">以下仅为用户提供摘要，原文／截图未独立核实。暂定日期不是售票日程，不可据此订机酒。</div></div>'+
    '<div class="lead-grid">'+tourLeads().map(leadCard).join('')+'</div>'+
    '<div class="panel lead-official"><h3>以官宣校准线索</h3><p>2026-11-06 读取 World Tour 官方页：仅列釜山、首尔。International Tour 是另一个栏目，未列即将演出站点；北美巡演不等于 World Tour。</p>'+
    '<div class="btn-row"><a class="btn" href="https://hamiltonmusical.com/world-tour/tickets/"'+leadLinkTarget()+' rel="noopener">World Tour 官方 ↗</a>'+
    '<a class="btn" href="https://hamiltonmusical.com/international-tour/tickets/"'+leadLinkTarget()+' rel="noopener">International Tour 官方 ↗</a><button class="btn primary" data-view="map">返回确认站点 →</button></div></div>';
  $('main').appendChild(section);
  const strip=document.createElement('div');
  strip.className='confidence-strip';
  strip.innerHTML='<span><strong>'+DATA.stops.length+'</strong> 已确认站点</span><button data-view="leads"><strong>'+leadCount+'</strong> 待核实线索 <span aria-hidden="true">↗</span></button><small>韩国核验 11.06 · 其他资料基线 10.28</small>';
  $('.hero').insertAdjacentElement('afterend',strip);
  $('#world-map').closest('.section').classList.add('atlas-map-section');
  let badge=$('#app-version');
  if(!badge){badge=document.createElement('span');badge.id='app-version';badge.className='chip';$('.top-meta').prepend(badge);}
  badge.textContent='v'+DATA.meta.version;
  const caption=$('.map-caption span');
  if(caption&&caption.textContent.includes('v1.1'))caption.textContent=caption.textContent.replace('v1.1','v1.2');
  $$('.top-meta .chip').filter(e=>e!==badge&&e.textContent.includes('数据核验')).forEach(e=>e.textContent='分条核验 · 见站点详情');
  const controls=document.createElement('div');
  controls.className='lead-layer-controls';
  controls.innerHTML='<label><input type="checkbox" id="lead-layer-toggle">显示未官宣线索 <span>手动开启</span></label><small id="lead-layer-count">默认仅显示已确认站点</small>';
  $('.map-panel .map-controls').insertAdjacentElement('afterend',controls);
  const warning=document.createElement('p');warning.id='lead-map-warning';warning.className='lead-map-warning hidden';warning.textContent='○ 空心点：未官宣线索，城市中心定位；不可据此订机酒。';
  $('.map-panel .legend').insertAdjacentElement('afterend',warning);
  const group=document.createElementNS('http://www.w3.org/2000/svg','g');group.id='map-leads';
  $('#map-content').insertBefore(group,$('#map-markers'));
  const dialog=document.createElement('div');dialog.id='lead-dialog';dialog.className='lead-dialog hidden';dialog.setAttribute('role','dialog');dialog.setAttribute('aria-modal','true');dialog.setAttribute('aria-labelledby','lead-dialog-title');
  dialog.innerHTML='<div class="lead-dialog-backdrop" data-lead-close="true"></div><div class="lead-dialog-card"><button class="lead-dialog-close" data-lead-close="true" aria-label="关闭依据">×</button><div id="lead-dialog-body"></div></div>';
  document.body.appendChild(dialog);
  $('#lead-layer-toggle').addEventListener('change',e=>{leadLayerEnabled=e.target.checked;state.zoom=1;state.pan={x:0,y:0};applyZoom();});
  document.addEventListener('click',e=>{const close=e.target.closest('[data-lead-close]');if(close){closeLead();return;}const lead=e.target.closest('[data-lead]');if(lead)showLead(lead.dataset.lead);});
  document.addEventListener('keydown',e=>{
    const modal=$('#lead-dialog'),mini=$('#mini-modal');
    if(mini&&!mini.classList.contains('hidden'))return;
    if(!modal.classList.contains('hidden')){
      if(e.key==='Escape'){e.preventDefault();closeLead();}
      if(e.key==='Tab'){
        const items=$$('button,a[href],input,textarea,select,[tabindex="0"]',modal).filter(el=>el.getClientRects().length);
        const first=items[0],last=items[items.length-1];
        if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}
        else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}
      }
      return;
    }
    const marker=e.target.closest('.lead-marker');
    if(marker&&(e.key==='Enter'||e.key===' ')){e.preventDefault();showLead(marker.dataset.lead);}
  });
  renderLeadMap();
}
