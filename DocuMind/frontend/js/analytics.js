(async()=>{
  try{
    const s=await api("/api/stats");
    $("#kpis").innerHTML=[["Documents",s.total_documents],["Words indexed",s.total_words.toLocaleString()],["Questions asked",s.total_questions],["Questions answered",s.answer_rate+"%"]]
      .map(([a,b])=>`<div class="stat"><span class="meta">${a}</span><b>${b}</b></div>`).join("");
    if(!s.total_questions){$("#empty").hidden=false;return}
    const acc=getComputedStyle(document.documentElement).getPropertyValue("--acc").trim();
    new Chart($("#c1"),{type:"line",data:{labels:s.over_time.map(r=>r.date),datasets:[{label:"Questions",data:s.over_time.map(r=>r.count),borderColor:acc,backgroundColor:acc+"33",fill:true,tension:.3}]},options:{scales:{y:{beginAtZero:true,ticks:{precision:0}}}}});
    new Chart($("#c2"),{type:"doughnut",data:{labels:["Answered","Not found"],datasets:[{data:[s.answered,s.not_found],backgroundColor:["#0f766e","#94a3b8"]}]}});
  }catch(e){$("#kpis").innerHTML=`<p class="msg err">${esc(e.message)}</p>`}
})();
