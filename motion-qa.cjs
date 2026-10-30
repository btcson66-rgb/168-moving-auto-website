const {chromium}=require('playwright');
const fs=require('fs');
(async()=>{
 const options={headless:true};
 if(process.env.CHROME_EXECUTABLE_PATH)options.executablePath=process.env.CHROME_EXECUTABLE_PATH;
 else if(process.platform==='win32'&&fs.existsSync('C:/Program Files/Google/Chrome/Application/chrome.exe'))options.executablePath='C:/Program Files/Google/Chrome/Application/chrome.exe';
 const browser=await chromium.launch(options),context=await browser.newContext(),page=await context.newPage({viewport:{width:1440,height:1000}});
 const output={baseCommit:'61de28ad97881ecf821eabd2a7bc78f15b8905c0',checks:[],responsive:[],errors:[]};page.on('pageerror',e=>output.errors.push(String(e)));
 const ensure=(value,message)=>{if(!value)throw Error(message);output.checks.push(message)};
 await page.goto('http://127.0.0.1:4173/en/');await page.locator('.fleet-band').scrollIntoViewIfNeeded();
 const transform=()=>page.locator('.freight-near').evaluate(el=>getComputedStyle(el).transform);
 const first=await transform();await page.waitForTimeout(400);ensure(first!==await transform(),'Freight truck position advances over time');
 await page.locator('.fleet-band [data-motion-toggle]').click();const stopped=await transform();await page.waitForTimeout(350);ensure(stopped===await transform(),'Pause control freezes the freight truck');
 ensure(await page.locator('.map-motion-control').textContent()==='Play animation','Map and fleet controls share the same pause state');
 await page.locator('.fleet-band [data-motion-toggle]').click();await page.locator('#routes').scrollIntoViewIfNeeded();await page.waitForTimeout(300);
 const matrix=()=>page.locator('.route-arrow').first().evaluate(el=>{const m=el.getCTM();return[m.a,m.b,m.c,m.d,m.e,m.f].map(x=>x.toFixed(2)).join(',')});
 const arrow=await matrix();await page.waitForTimeout(400);ensure(arrow!==await matrix(),'Map arrow travels along its actual route');
 await page.locator('.map-motion-control').click();const pausedArrow=await matrix();await page.waitForTimeout(300);ensure(pausedArrow===await matrix(),'Pause control freezes the route arrow');
 await page.locator('[data-route]').nth(2).click();ensure(await page.locator('#quote-dialog').isVisible(),'Route selection still opens the inquiry dialog');
 ensure(await page.locator('#inquiry-form input[name=to]').inputValue()==='75201','Dallas route keeps the correct destination ZIP');await page.keyboard.press('Escape');
 ensure((await page.locator('.route-status').textContent()).includes('Dallas'),'Map status follows the selected route');
 for(const lang of ['en','zh-hans','zh-hant'])for(const width of [375,768,1440]){
  await page.setViewportSize({width,height:900});await page.goto(`http://127.0.0.1:4173/${lang}/`);
  const record={lang,width,overflow:await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),brokenImages:await page.locator('img').evaluateAll(els=>els.filter(e=>e.complete&&e.naturalWidth===0).length),heroLines:await page.locator('.hero h1').evaluate(el=>Math.round(el.getBoundingClientRect().height/parseFloat(getComputedStyle(el).lineHeight)))};
  output.responsive.push(record);if(record.overflow||record.brokenImages)throw Error('Responsive image or layout failure '+JSON.stringify(record));
 }
 const reduced=await browser.newContext({reducedMotion:'reduce'}),reducedPage=await reduced.newPage();await reducedPage.goto('http://127.0.0.1:4173/en/');await reducedPage.locator('.route-map').scrollIntoViewIfNeeded();await reducedPage.waitForTimeout(200);
 ensure(await reducedPage.locator('.freight-near').evaluate(el=>getComputedStyle(el).animationName)==='none','Reduced-motion preference disables truck animation');
 ensure(await reducedPage.locator('.route-diagram').evaluate(el=>el.animationsPaused()),'Reduced-motion preference pauses SVG route movement');
 ensure(await reducedPage.locator('.map-motion-control').isDisabled(),'System reduced-motion preference is not overridden by the control');
 output.checkedAt=new Date().toISOString();fs.writeFileSync('research/midnight-motion-qa.json',JSON.stringify(output,null,2));console.log(JSON.stringify(output,null,2));await browser.close();
 if(output.errors.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exit(1)});
