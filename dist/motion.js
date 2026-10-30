/* Local transport illustration: no live-location feed, booking or tracking backend. */
(()=>{'use strict';
 const controls=[...document.querySelectorAll('[data-motion-toggle]')];
 const scenes=[...document.querySelectorAll('[data-animated-svg]')];
 const reduced=matchMedia('(prefers-reduced-motion: reduce)');let userPaused=false;
 const language=document.documentElement.lang;
 const reducedLabel=language==='en'?'Motion off':language==='zh-Hans'?'动态效果已关闭':'動態效果已關閉';
 const reducedMessage=language==='en'?'Motion is disabled in your system preferences.':language==='zh-Hans'?'已按照系统的减少动态效果设置停止动画。':'已依照系統的減少動態效果設定停止動畫。';
 const inView=new Map(scenes.map(el=>[el,true]));
 function sync(){
  const paused=userPaused||reduced.matches;
  document.documentElement.dataset.motion=paused?'paused':'playing';
  controls.forEach(b=>{b.textContent=reduced.matches?reducedLabel:paused?b.dataset.playLabel:b.dataset.pauseLabel;b.classList.toggle('is-paused',paused);b.disabled=reduced.matches;b.title=reduced.matches?reducedMessage:''});
  scenes.forEach(svg=>{if(typeof svg.pauseAnimations!=='function')return;(paused||document.hidden||!inView.get(svg))?svg.pauseAnimations():svg.unpauseAnimations()});
 }
 controls.forEach(b=>b.addEventListener('click',()=>{userPaused=!userPaused;sync()}));
 reduced.addEventListener('change',sync);document.addEventListener('visibilitychange',sync);
 if('IntersectionObserver'in window){const observer=new IntersectionObserver(entries=>{entries.forEach(e=>inView.set(e.target,e.isIntersecting));sync()},{rootMargin:'100px'});scenes.forEach(el=>observer.observe(el))}
 document.querySelectorAll('[data-route]').forEach((b,index)=>b.addEventListener('click',()=>{
  document.querySelectorAll('.route-path,.route-arrow').forEach(el=>el.classList.toggle('is-current',Number(el.dataset.routeIndex)===index));
  document.querySelectorAll('[data-route]').forEach(el=>el.classList.toggle('is-current',el===b));
  const status=document.querySelector('.route-status');if(status)status.textContent=b.dataset.routeLabel;
 }));
 sync();
})();
