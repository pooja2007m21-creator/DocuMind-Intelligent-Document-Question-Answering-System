let docId=null;const msg=(t,k)=>{const m=$("#msg");m.className="msg "+(k||"");m.textContent=t};
async function loadDocs(sel){
  try{const d=await api("/api/documents");
    $("#docs").innerHTML=d.items.length?d.items.map(i=>`<div class="doc" role="button" tabindex="0" data-id="${i.id}" aria-current="${i.id===docId}"><span><b>${esc(i.name)}</b><br><span class="meta">${i.word_count} words · ${i.sentence_count} sentences</span></span><button class="btn danger" data-del="${i.id}" aria-label="Delete ${esc(i.name)}">Delete</button></div>`).join(""):`<p class="meta">No documents yet. Upload one above.</p>`;
    if(sel){docId=sel}
    $("#ask").disabled=!docId;
  }catch(e){msg(e.message,"err")}
}
$("#docs").onclick=async e=>{
  const del=e.target.closest("[data-del]");
  if(del){if(!confirm("Delete this document and its questions?"))return;
    try{await api("/api/documents/"+del.dataset.del,{method:"DELETE"});if(docId==del.dataset.del){docId=null;$("#res").innerHTML=""}loadDocs()}catch(x){msg(x.message,"err")}return}
  const d=e.target.closest(".doc");if(d){docId=+d.dataset.id;$("#res").innerHTML="";loadDocs()}
};
async function added(p){msg(p.status+" "+p.name+" is selected.","ok");docId=p.id;await loadDocs();$("#q").focus()}
$("#file").onchange=async e=>{
  const f=e.target.files[0];if(!f)return;const fd=new FormData();fd.append("file",f);msg("Reading file…");
  try{const r=await fetch("/api/documents",{method:"POST",body:fd});const p=await r.json();if(!r.ok)throw new Error(p.error);await added(p)}
  catch(x){msg(x.message,"err")}finally{e.target.value=""}
};
$("#addtext").onclick=async()=>{
  try{const p=await api("/api/documents",{method:"POST",body:JSON.stringify({name:$("#pname").value,text:$("#ptext").value})});$("#ptext").value="";await added(p)}
  catch(x){msg(x.message,"err")}
};
async function ask(){
  const q=$("#q").value;$("#bar").classList.add("on");$("#ask").disabled=true;$("#res").innerHTML="";
  try{
    const d=await api("/api/ask",{method:"POST",body:JSON.stringify({document_id:docId,question:q})});
    $("#res").innerHTML=`<div class="card"><div class="row sp"><h3>Answer</h3>${d.found?`<span class="badge">Match strength: ${esc(d.strength)}</span>`:""}</div>
      <p class="ans" ${d.found?"":'style="color:var(--mute)"'}>${esc(d.answer)}</p>
      ${d.found?`<button class="btn" id="cp">Copy answer</button><h3 style="margin-top:18px">Where this came from</h3><p class="meta">Highlighted sentences form the answer. Always check them against the document.</p>`+
      d.sources.map(s=>`<div class="src">${s.sentences.map(x=>x.used?`<mark>${esc(x.text)}</mark>`:esc(x.text)).join(" ")}</div>`).join(""):""}</div>`;
    if(d.found)$("#cp").onclick=()=>copyText(d.answer);
  }catch(x){msg(x.message,"err")}finally{$("#bar").classList.remove("on");$("#ask").disabled=!docId}
}
$("#ask").onclick=ask;$("#q").onkeydown=e=>{if(e.key==="Enter"&&!$("#ask").disabled)ask()};
document.querySelectorAll("[data-tab]").forEach(b=>b.onclick=()=>{document.querySelectorAll("[data-tab]").forEach(x=>x.setAttribute("aria-pressed",x===b));$("#t-file").hidden=b.dataset.tab!=="file";$("#t-text").hidden=b.dataset.tab!=="text"});
loadDocs();
