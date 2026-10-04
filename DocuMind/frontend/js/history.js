let status="",timer;const list=$("#list");
async function load(){
  try{const d=await api(`/api/history?q=${encodeURIComponent($("#q").value)}&status=${status}`);
    list.innerHTML=d.items.length?d.items.map(i=>`<article class="card"><div class="row sp"><h3>${esc(i.question)}</h3><span class="meta">${esc(i.document)} · ${esc(i.created_at)}</span></div>
      <p ${i.found?"":'class="meta"'}>${esc(i.answer)}</p><div class="row">${i.found?`<span class="badge">Match strength: ${esc(i.strength)}</span><button class="btn" data-a="copy" data-t="${esc(i.answer)}">Copy answer</button>`:""}<button class="btn danger" data-a="del" data-id="${i.id}">Delete</button></div></article>`).join("")
      :`<p class="meta">No questions found. <a href="/workspace">Ask one</a>.</p>`}
  catch(e){list.innerHTML=`<p class="msg err">${esc(e.message)}</p>`}
}
list.onclick=async e=>{const b=e.target.closest("button");if(!b)return;
  if(b.dataset.a==="copy")return copyText(b.dataset.t);
  if(!confirm("Delete this entry?"))return;
  try{await api("/api/history/"+b.dataset.id,{method:"DELETE"});toast("Deleted");load()}catch(x){toast(x.message)}};
$("#q").oninput=()=>{clearTimeout(timer);timer=setTimeout(load,250)};
document.querySelectorAll("[data-s]").forEach(b=>b.onclick=()=>{status=b.dataset.s;document.querySelectorAll("[data-s]").forEach(x=>x.setAttribute("aria-pressed",x===b));load()});
load();
