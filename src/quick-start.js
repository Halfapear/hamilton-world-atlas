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
}
