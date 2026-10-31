(()=>{'use strict';
const form=document.querySelector('#inquiry-form');if(!form)return;
const en=document.documentElement.lang==='en',cn=document.documentElement.lang==='zh-Hans';
const text=(a,b,c)=>en?c:cn?b:a;
const status=document.querySelector('#email-status'),send=document.querySelector('#send-inquiry');
const emailCopy=document.querySelector('#email-copy');
function syncCopy(){emailCopy.disabled=!form.elements.email.value.trim();if(emailCopy.disabled)emailCopy.checked=false;emailCopy.title=emailCopy.disabled?text('填寫電子郵件後可寄送副本','填写电子邮箱后可发送副本','Enter an email address to receive a copy'):''}
form.elements.email.addEventListener('input',syncCopy);syncCopy();

function payload(){return {name:form.elements.name.value.trim(),email:form.elements.email.value.trim(),service:form.elements.service.value,from:form.elements.from.value,to:form.elements.to.value,date:form.elements.date.value,details:form.elements.details.value,copy:document.querySelector('#email-copy').checked&&!!form.elements.email.value.trim(),lang:document.documentElement.lang}}
function body(p){return `168 Moving & Auto — Inquiry\n\nName: ${p.name}\nEmail: ${p.email}\nService: ${form.elements.service.selectedOptions[0].textContent}\nFrom ZIP: ${p.from}\nTo ZIP: ${p.to}\nDate: ${p.date||'—'}\nDetails: ${p.details||'—'}\n\nInquiry only. Pricing and availability require confirmation.`}
form.addEventListener('submit',()=>{status.textContent=''});
send.addEventListener('click',()=>{const p=payload();if(!form.reportValidity())return;const url=new URL('https://mail.google.com/mail/');url.searchParams.set('view','cm');url.searchParams.set('fs','1');url.searchParams.set('to','help@carshipping168.com');url.searchParams.set('su','168 Inquiry: '+p.from+' → '+p.to);url.searchParams.set('body',body(p));if(p.copy)url.searchParams.set('cc',p.email);window.open(url.href,'_blank','noopener,noreferrer');status.textContent=text('請在 Gmail 確認內容並按寄送。若新分頁未開啟，請允許彈出視窗，或改用其他郵件軟體。網站尚未寄出郵件。','请在 Gmail 确认内容并点击发送。若新标签页未打开，请允许弹出窗口，或使用其他邮件软件。网站尚未发送邮件。','Review the draft in Gmail and press Send. If no tab opens, allow pop-ups or use another email app. The website has not sent an email.');});
document.querySelector('#email-draft').addEventListener('click',()=>{const p=payload();const url='mailto:help@carshipping168.com?subject='+encodeURIComponent('168 Inquiry: '+p.from+' → '+p.to)+'&body='+encodeURIComponent(body(p))+(p.copy?'&cc='+encodeURIComponent(p.email):'');location.href=url;status.textContent=text('已請求開啟郵件軟體，請確認收件人並按寄送。尚未確認寄出。','已请求打开邮件软件，请确认收件人并点击发送。尚未确认发出。','Requested your email app. Check the recipient and press Send. Sending has not been confirmed.')});
document.querySelector('#inquiry-wechat').addEventListener('click',()=>{document.querySelector('#quote-dialog').close();document.querySelector('#wechat-dialog').showModal()});
})();
