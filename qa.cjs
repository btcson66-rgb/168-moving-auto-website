const {chromium}=require('playwright');
const AxeBuilder=require('@axe-core/playwright').default;
const fs=require('fs');
const http=require('http');
const net=require('net');
const path=require('path');
const ROOT=path.resolve(__dirname,'dist');
const PORT=Number(process.env.PORT||4180);
const BASE=`http://127.0.0.1:${PORT}`;
const TYPES={'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8','.json':'application/json; charset=utf-8','.svg':'image/svg+xml','.jpg':'image/jpeg','.jpeg':'image/jpeg','.png':'image/png','.webp':'image/webp','.avif':'image/avif','.woff2':'font/woff2','.woff':'font/woff','.xml':'application/xml; charset=utf-8','.txt':'text/plain; charset=utf-8','.ico':'image/x-icon','.gif':'image/gif'};
function portInUse(port){return new Promise(resolve=>{const s=net.connect({host:'127.0.0.1',port});s.once('connect',()=>{s.destroy();resolve(true)});s.once('error',()=>resolve(false))})}
function startServer(){
 const server=http.createServer((req,res)=>{
  let pathname;try{pathname=decodeURIComponent(new URL(req.url,'http://127.0.0.1').pathname)}catch{res.writeHead(400);return res.end()}
  let file=path.join(ROOT,pathname);
  if(file!==ROOT&&!file.startsWith(ROOT+path.sep)){res.writeHead(403);return res.end()}
  let stat=null;try{stat=fs.statSync(file)}catch{}
  if(stat&&stat.isDirectory()){file=path.join(file,'index.html');try{stat=fs.statSync(file)}catch{stat=null}}
  if(!stat||!stat.isFile()){res.writeHead(404,{'Content-Type':'text/plain; charset=utf-8'});return res.end('Not found')}
  res.writeHead(200,{'Content-Type':TYPES[path.extname(file).toLowerCase()]||'application/octet-stream','Content-Length':stat.size,'Cache-Control':'no-store'});
  fs.createReadStream(file).pipe(res);
 });
 return new Promise((resolve,reject)=>{server.once('error',reject);server.listen(PORT,'127.0.0.1',()=>resolve(server))});
}
(async()=>{
 let server=null,b=null;
 try{
 if(!(await portInUse(PORT)))server=await startServer();
 const launchOptions={headless:true};
 if(process.env.CHROME_PATH)launchOptions.executablePath=process.env.CHROME_PATH;
 b=await chromium.launch(launchOptions);
 const out={pages:[],interactions:[],accessibility:[],errors:[]};
 const context=await b.newContext({reducedMotion:'reduce'});const p=await context.newPage();p.on('pageerror',e=>out.errors.push(String(e)));
 for(const lang of ['zh-hant','zh-hans','en'])for(const width of [1440,390]){
  await p.setViewportSize({width,height:900});
  for(const path of ['', 'plan/', 'guides/','guides/auto/','library/']){
   const response=await p.goto(`${BASE}/${lang}/${path}`);await p.waitForTimeout(100);
   out.pages.push({lang,width,path,status:response.status(),overflow:await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth),h1:await p.locator('h1').count(),canonical:await p.locator('link[rel=canonical]').getAttribute('href')});
  }
  if(width===1440){await p.goto(`${BASE}/${lang}/`);const axe=await new AxeBuilder({page:p}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();out.accessibility.push({lang,violations:axe.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.map(n=>({target:n.target,summary:n.failureSummary}))}))})}
 }
 await p.setViewportSize({width:1440,height:1000});await p.goto(`${BASE}/zh-hant/`);
 await p.locator('#quick-form input[name=from]').fill('90012');await p.locator('#quick-form input[name=to]').fill('10001');await p.locator('[data-service="2"]').click();
 await p.locator('#language').selectOption('en');await p.waitForURL('**/en/');
 if(await p.locator('#quick-form input[name=from]').inputValue()!=='90012')throw Error('Language switch lost ZIP');
 if(await p.locator('[data-service="2"]').getAttribute('aria-pressed')!=='true')throw Error('Language switch lost service');
 out.interactions.push('Language switching preserves route and selected service');
 await p.locator('#quick-form button[type=submit]').click();await p.waitForURL('**/plan/**');await p.locator('.planner-hero [data-quote]').click();await p.locator('#inquiry-form input[name=name]').fill('QA Test');await p.locator('#inquiry-form input[name=email]').fill('qa@example.com');await p.locator('#inquiry-form textarea').fill('<script>alert(1)</script> Toyota RAV4');await p.locator('#inquiry-form button[type=submit]').click();
 if(!(await p.locator('#wizard-summary').isVisible()))throw Error('Summary missing');
 if(!(await p.locator('#summary-fields').textContent()).includes('<script>alert(1)</script>'))throw Error('Escaping failed');
 const download=p.waitForEvent('download');await p.locator('#download-summary').click();const file=await download;await file.saveAs('research/test-inquiry.txt');out.interactions.push('Summary renders input as text and downloads locally');
 await p.locator('#edit-summary').click();await p.locator('#inquiry-form input[name=to]').fill('90012');await p.locator('#inquiry-form button[type=submit]').click();if(!(await p.locator('#form-error').textContent()).includes('different'))throw Error('Same ZIP accepted');out.interactions.push('Identical ZIP validation');
 await p.locator('#quote-dialog [data-close]').click();await p.goto(`${BASE}/en/`);await p.locator('[data-route]').first().click();if(await p.locator('#inquiry-form input[name=to]').inputValue()!=='10001')throw Error('Route autofill failed');out.interactions.push('Route button fills inquiry');await p.keyboard.press('Escape');
 await p.goto(`${BASE}/en/library/`);await p.waitForFunction(()=>document.querySelectorAll('.library-item').length>0);await p.locator('#library-search').fill('Tesla');await p.waitForTimeout(100);out.interactions.push('Article search: '+await p.locator('#library-count').textContent());await p.locator('#library-category').selectOption('auto');
 if(await p.locator('.library-item').count()){await p.locator('.library-item').first().click();if(await p.locator('.original-body').count()!==1)throw Error('Original article body missing');out.interactions.push('Original article readable')}
 await p.setViewportSize({width:390,height:844});await p.goto(`${BASE}/en/`);await p.locator('.menu-button').click();if(!(await p.locator('#navlinks').isVisible()))throw Error('Mobile nav missing');await p.locator('#navlinks a').first().click();if(await p.locator('.menu-button').getAttribute('aria-expanded')!=='false')throw Error('Mobile menu not closed');out.interactions.push('Mobile menu and anchor navigation');
 await p.locator('.menu-button').click();await p.locator('.mobile-nav-quote').click();if(!(await p.locator('#quote-dialog').isVisible()))throw Error('Mobile menu inquiry action failed');if(await p.locator('.menu-button').getAttribute('aria-expanded')!=='false')throw Error('Mobile menu stayed open behind dialog');await p.keyboard.press('Escape');out.interactions.push('Mobile menu inquiry action opens dialog and closes navigation');
 fs.writeFileSync('research/qa.json',JSON.stringify(out,null,2));console.log(JSON.stringify(out,null,2));
 const failures=[];
 for(const r of out.pages){
  const where=`${r.lang} ${r.width}px /${r.path}`;
  if(r.status!==200)failures.push(`${where}: HTTP ${r.status}`);
  if(r.overflow)failures.push(`${where}: horizontal overflow`);
  if(r.h1!==1)failures.push(`${where}: ${r.h1} h1 elements (expected 1)`);
 }
 for(const a of out.accessibility)for(const v of a.violations)failures.push(`${a.lang} axe ${v.id} (${v.impact}): ${v.nodes.length} node(s)`);
 if(failures.length){console.error('QA failed:\n- '+failures.join('\n- '));process.exitCode=1}
 }finally{
  if(b)await b.close();
  if(server)await new Promise(resolve=>server.close(resolve));
 }
})().catch(e=>{console.error(e);process.exit(1)});
