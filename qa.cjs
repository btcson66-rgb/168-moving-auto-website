const {chromium}=require('playwright');
const AxeBuilder=require('@axe-core/playwright').default;
const fs=require('fs');
(async()=>{
 const b=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 const out={pages:[],interactions:[],accessibility:[],errors:[]};
 const context=await b.newContext();const p=await context.newPage();p.on('pageerror',e=>out.errors.push(String(e)));
 for(const lang of ['zh-hant','zh-hans','en'])for(const width of [1440,390]){
  await p.setViewportSize({width,height:900});
  for(const path of ['', 'guides/','guides/auto/','library/']){
   const response=await p.goto(`http://127.0.0.1:4173/${lang}/${path}`);await p.waitForTimeout(100);
   out.pages.push({lang,width,path,status:response.status(),overflow:await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth),h1:await p.locator('h1').count(),canonical:await p.locator('link[rel=canonical]').getAttribute('href')});
  }
  if(width===1440){await p.goto(`http://127.0.0.1:4173/${lang}/`);const axe=await new AxeBuilder({page:p}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();out.accessibility.push({lang,violations:axe.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.map(n=>({target:n.target,summary:n.failureSummary}))}))})}
 }
 await p.setViewportSize({width:1440,height:1000});await p.goto('http://127.0.0.1:4173/zh-hant/');
 await p.locator('#quick-form input[name=from]').fill('90012');await p.locator('#quick-form input[name=to]').fill('10001');await p.locator('[data-service="2"]').click();
 await p.locator('#language').selectOption('en');await p.waitForURL('**/en/');
 if(await p.locator('#quick-form input[name=from]').inputValue()!=='90012')throw Error('Language switch lost ZIP');
 if(await p.locator('[data-service="2"]').getAttribute('aria-pressed')!=='true')throw Error('Language switch lost service');
 out.interactions.push('Language switching preserves route and selected service');
 await p.locator('#quick-form button[type=submit]').click();await p.locator('#inquiry-form textarea').fill('<script>alert(1)</script> Toyota RAV4');await p.locator('#inquiry-form button[type=submit]').click();
 if(!(await p.locator('#wizard-summary').isVisible()))throw Error('Summary missing');
 if(!(await p.locator('#summary-fields').textContent()).includes('<script>alert(1)</script>'))throw Error('Escaping failed');
 const download=p.waitForEvent('download');await p.locator('#download-summary').click();const file=await download;await file.saveAs('research/test-inquiry.txt');out.interactions.push('Summary renders input as text and downloads locally');
 await p.locator('#edit-summary').click();await p.locator('#inquiry-form input[name=to]').fill('90012');await p.locator('#inquiry-form button[type=submit]').click();if(!(await p.locator('#form-error').textContent()).includes('different'))throw Error('Same ZIP accepted');out.interactions.push('Identical ZIP validation');
 await p.locator('#quote-dialog [data-close]').click();await p.locator('[data-route]').first().click();if(await p.locator('#inquiry-form input[name=to]').inputValue()!=='10001')throw Error('Route autofill failed');out.interactions.push('Route button fills inquiry');await p.keyboard.press('Escape');
 await p.goto('http://127.0.0.1:4173/en/library/');await p.waitForFunction(()=>document.querySelectorAll('.library-item').length>0);await p.locator('#library-search').fill('Tesla');await p.waitForTimeout(100);out.interactions.push('Article search: '+await p.locator('#library-count').textContent());await p.locator('#library-category').selectOption('auto');
 if(await p.locator('.library-item').count()){await p.locator('.library-item').first().click();if(await p.locator('.original-body').count()!==1)throw Error('Original article body missing');out.interactions.push('Original article readable')}
 await p.setViewportSize({width:390,height:844});await p.goto('http://127.0.0.1:4173/en/');await p.locator('.menu-button').click();if(!(await p.locator('#navlinks').isVisible()))throw Error('Mobile nav missing');await p.locator('#navlinks a').first().click();if(await p.locator('.menu-button').getAttribute('aria-expanded')!=='false')throw Error('Mobile menu not closed');out.interactions.push('Mobile menu and anchor navigation');
 await p.locator('.menu-button').click();await p.locator('.mobile-nav-quote').click();if(!(await p.locator('#quote-dialog').isVisible()))throw Error('Mobile menu inquiry action failed');if(await p.locator('.menu-button').getAttribute('aria-expanded')!=='false')throw Error('Mobile menu stayed open behind dialog');await p.keyboard.press('Escape');out.interactions.push('Mobile menu inquiry action opens dialog and closes navigation');
 fs.writeFileSync('research/qa.json',JSON.stringify(out,null,2));console.log(JSON.stringify(out,null,2));await b.close();
})().catch(e=>{console.error(e);process.exit(1)});
