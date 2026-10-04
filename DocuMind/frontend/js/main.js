const PAGES=[["/","Home"],["/workspace","Workspace"],["/history","History"],["/analytics","Analytics"],["/about","About"]];
const $=(s,r=document)=>r.querySelector(s);
const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
function setTheme(t){document.documentElement.dataset.theme=t;localStorage.setItem("theme",t)}
setTheme(localStorage.getItem("theme")||(matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light"));
document.addEventListener("DOMContentLoaded",()=>{
  const p=location.pathname.replace(/\/$/,"")||"/";
  $("#nav").innerHTML=`<nav aria-label="Main"><div class="wrap"><a class="brand" href="/">DocuMind</a>`+
   PAGES.map(([h,t])=>`<a class="link ${h===p?"active":""}" href="${h}" ${h===p?'aria-current="page"':""}>${t}</a>`).join("")+
   `<button class="btn" id="theme" aria-label="Toggle dark mode">Dark / Light</button></div></nav>`;
  $("#theme").onclick=()=>setTheme(document.documentElement.dataset.theme==="dark"?"light":"dark");
  $("#foot").innerHTML=`<footer><div class="wrap">DocuMind is a Text and Speech Analysis project. Automated summaries may omit context or contain errors; review them before relying on them for academic or professional use.</div></footer>`;
});
function toast(m){const t=document.createElement("div");t.className="toast";t.setAttribute("role","status");t.textContent=m;document.body.append(t);setTimeout(()=>t.remove(),2200)}
async function api(url,opt={}){
  try{const r=await fetch(url,{headers:{"Content-Type":"application/json"},...opt});const d=await r.json();
    if(!r.ok)throw new Error(d.error||"Request failed.");return d}
  catch(e){throw new Error(e instanceof TypeError?"Cannot reach the server. Is it running?":e.message)}
}
async function copyText(t){try{await navigator.clipboard.writeText(t);toast("Copied to clipboard")}catch{toast("Copy failed. Select the text manually.")}}
function download(name,text){const a=document.createElement("a");a.href=URL.createObjectURL(new Blob([text],{type:"text/plain"}));a.download=name.replace(/[^\w-]+/g,"_")+".txt";a.click();URL.revokeObjectURL(a.href)}
