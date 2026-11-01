const {chromium}=require('playwright');
const AxeBuilder=require('@axe-core/playwright').default;
const fs=require('fs');
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.platform==='win32'?{executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'}:{})});
 try{
 const context=await browser.newContext({reducedMotion:'reduce'}),page=await context.newPage(),out={checks:[],pages:[],accessibility:[],errors:[]};page.on('pageerror',e=>out.errors.push(String(e)));
 const check=(v,m)=>{if(!v)throw Error(m);out.checks.push(m)};
 for(const lang of ['zh-hant','zh-hans','en']){
  for(const width of [375,768,1101,1440]){
   await page.setViewportSize({width,height:892});await page.goto(`http://127.0.0.1:4180/${lang}/plan/`);
   const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);if(overflow)throw Error('Planner overflow '+lang+width);out.pages.push({lang,width,overflow});
  }
  out.accessibility.push({lang,violations:(await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze()).violations.map(v=>v.id)});
  await page.goto(`http://127.0.0.1:4180/${lang}/library/`);check(await page.locator('.archive-index a').count()===205,lang+': 205 original articles have static links');
 }
 await page.goto('http://127.0.0.1:4180/zh-hant/');await page.locator('#quick-form input[name=from]').fill('90012');await page.locator('#quick-form input[name=to]').fill('10001');await page.locator('#quick-form button[type=submit]').click();await page.waitForURL('**/plan/**');
 check((await page.locator('#plan-route-summary').textContent()).includes('90012'),'Quick form carries route to planner');
 await page.locator('#language').selectOption('en');await page.waitForURL('**/en/plan/');check((await page.locator('#plan-route-summary').textContent()).includes('10001'),'Planner language switch retains route');
 await page.locator('.planner-hero [data-quote]').click();check(await page.locator('#inquiry-form input[name=from]').inputValue()==='90012','Planner opens inquiry with route');
 check(await page.locator('#email-copy').isDisabled(),'Copy option requires an email address');
 await page.locator('#inquiry-form input[name=name]').fill('Optional email tester');await page.locator('#inquiry-form button[type=submit]').click();check(await page.locator('#wizard-summary').isVisible(),'Inquiry can be prepared without an email address');await page.keyboard.press('Escape');
 await page.goto('http://127.0.0.1:4180/en/guides/auto/');check(await page.locator('.article-layout article .related-reading a[href^="/original/"]').count()===3,'Guide links to three historical originals');
 const original=await page.locator('.article-layout a[href^="/original/"]').first().getAttribute('href');await page.goto('http://127.0.0.1:4180'+original);check(await page.locator('.original-body').count()===1&&await page.locator('.related-reading a[href*="/guides/"]').count()>0,'Original article links back to guides');
 fs.writeFileSync('research/discovery-qa.json',JSON.stringify(out,null,2));console.log(JSON.stringify(out,null,2));if(out.errors.length||out.accessibility.some(a=>a.violations.length))process.exitCode=1;
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
