/* Local display of already-verified ticket times; never a live stock claim. */
function renderQuickStart(data){
  const container=document.getElementById('korea-quick-start');
  if(!container)return;
  const escapeText=value=>String(value==null?'':value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const cities=['busan','seoul'].map(id=>data.stops.find(s=>s.id===id)).filter(Boolean);
  const openingLabel=s=>{
    if(!s.ticketOpen)return '开票安排待官方公布';
    const date=new Date(s.ticketOpen);
    if(!isFinite(date.getTime()))return '请核对官方开票安排';
    const beijing=new Date(date.getTime()+8*60*60*1000);
    return (beijing.getUTCMonth()+1)+'月'+beijing.getUTCDate()+'日 '+String(beijing.getUTCHours()).padStart(2,'0')+':'+String(beijing.getUTCMinutes()).padStart(2,'0')+' 开票';
  };
  container.innerHTML='<div class="quick-start-heading"><h3>准备看韩巡？从这里开始</h3><small>开票时间 · 北京时间</small></div><div class="quick-start-grid">'+cities.map(s=>'<button class="quick-city" data-stop="'+escapeText(s.id)+'"><span><strong>'+escapeText(s.city)+' / '+escapeText(s.cityEn)+'</strong><small>'+escapeText(openingLabel(s))+'</small></span><span class="quick-arrow" aria-hidden="true">↗</span></button>').join('')+'</div><p class="quick-note">查看场馆、票档预算与观演计划。数据核验：'+escapeText(data.meta.lastVerified)+'；实际场次及余票以官方实时信息为准。</p>';
  container.querySelector('.quick-note').textContent='韩国核验 2026-11-06 · 其他资料基线 '+data.meta.lastVerified+'。首尔首轮仅 01-21 至 01-24、部分一楼 VIP；余票以官方为准。';
  container.insertAdjacentHTML('beforeend','<details class="korea-brief"><summary>资格预售与开票范围</summary><p>北京时间比韩国晚 1 小时。</p>'+cities.map(s=>'<p><strong>'+escapeText(s.city)+'：</strong>'+escapeText(s.ticketScope||s.bookingNote)+'</p>'+(s.presales||[]).map(p=>'<p>'+escapeText(p.label)+'：'+escapeText(p.start.replace('T',' ').replace('+08:00',''))+' 至 '+escapeText(p.end.replace('T',' ').replace('+08:00',''))+'（北京时间）。'+escapeText(p.eligibility)+'</p>').join('')+'<p>'+escapeText(s.dateConflict||'')+'</p>').join('')+'<p>VIP/R/S/A/B 票面价：₩220,000 / 180,000 / 140,000 / 100,000 / 70,000。票档价格不代表首轮均有售；海外购票资格及 NOL World 上架情况未确认。</p></details>');
}
