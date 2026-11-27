#!/usr/bin/env python3
"""Add the "All covered stocks" data table to the Daily Stock Market Blog page.

A sortable, filterable table across all three exchanges with view tabs
(Overview / Performance / Analysts), exchange tabs, industry / rating / size /
move filters, a live count, paging and filters kept in the web address.
Needs tools/add_features.py to have been applied first. Idempotent.

Usage: python3 tools/add_table.py <page.html>   (edits in place)
"""
import sys

MARK = "/* table:v1 */"

CSS = MARK + """
.tblsec{padding-block:30px 10px}
.th1{display:flex;flex-wrap:wrap;align-items:baseline;gap:4px 16px}
.th1 h2{font:600 clamp(24px,3.4vw,32px)/1.1 var(--fd);letter-spacing:-.02em;margin:0}
.th1 .sub{margin:0}
.tctl{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-top:16px}
.tctl input,.tctl select{font:15px var(--ft);color:var(--ink);background:var(--card);border:1px solid var(--line);border-radius:8px;padding:8px 10px;min-height:40px}
.tctl input{flex:1 1 200px;max-width:280px}
.tctl .rst{font:600 14px var(--ft);color:var(--accent);background:transparent;border:1px solid var(--line);border-radius:8px;padding:8px 12px;min-height:40px;cursor:pointer}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chips button{font:600 14px var(--ft);color:var(--ink);background:var(--card);border:1px solid var(--line);border-radius:999px;padding:7px 14px;cursor:pointer;min-height:38px}
.chips button small{font-weight:500;color:var(--muted);margin-left:4px}
.chips button[aria-selected=true]{background:var(--ink);color:var(--bg);border-color:var(--ink)}
.chips button[aria-selected=true] small{color:inherit;opacity:.75}
.views{display:flex;gap:2px;margin-top:18px;border-bottom:1px solid var(--line);overflow-x:auto}
.views button{font:600 15px var(--ft);color:var(--muted);background:transparent;border:0;border-bottom:2px solid transparent;padding:10px 14px;cursor:pointer;white-space:nowrap}
.views button[aria-selected=true]{color:var(--ink);border-bottom-color:var(--accent)}
.twrap{max-height:min(74vh,820px);overflow:auto;border:1px solid var(--line);border-top:0;border-radius:0 0 12px 12px;background:var(--card)}
.dt{width:100%;border-collapse:separate;border-spacing:0;font-size:14px}
.dt th,.dt td{padding:9px 12px;border-bottom:1px solid var(--line);white-space:nowrap;text-align:left}
.dt th{position:sticky;top:0;z-index:2;background:var(--zone);font-size:13px;font-weight:600;color:var(--muted)}
.dt th button{all:unset;cursor:pointer;display:inline-flex;gap:4px;align-items:center}
.dt th button:focus-visible{outline:2px solid var(--accent);outline-offset:3px;border-radius:3px}
.dt th[aria-sort] button{color:var(--ink)}
.dt th .ar{font-size:11px;opacity:.8}
.dt .r{text-align:right}.dt th.r button{justify-content:flex-end}
.dt td:first-child,.dt th:first-child{position:sticky;left:0;z-index:1;background:var(--card)}
.dt th:first-child{z-index:3;background:var(--zone)}
.dt tbody tr{cursor:pointer}
.dt tbody tr:hover td{background:var(--zone)}
.dt .sym{display:flex;align-items:center;gap:8px;font-weight:700;color:var(--accent)}
.dt .sym .star{width:28px;height:28px;border:0;border-radius:6px}
.dt .sym .star svg{width:16px;height:16px}
.dt .co{display:inline-block;vertical-align:middle;max-width:260px;overflow:hidden;text-overflow:ellipsis}
.dt .ex{font-size:12px;font-weight:700;color:var(--muted)}
.dt .rb{font-size:12px;padding:2px 7px}
.dt .lt{font-size:13px;color:var(--muted);max-width:280px;overflow:hidden;text-overflow:ellipsis}
.dt .na{color:var(--muted)}
.tfoot{display:flex;flex-wrap:wrap;gap:10px 16px;align-items:center;justify-content:space-between;padding:12px 2px;font-size:14px;color:var(--muted)}
.tfoot select{font:14px var(--ft);color:var(--ink);background:var(--card);border:1px solid var(--line);border-radius:8px;padding:6px 8px}
.pg{display:flex;gap:8px;align-items:center}
.pg button{font:600 14px var(--ft);color:var(--ink);background:var(--card);border:1px solid var(--line);border-radius:8px;padding:7px 12px;cursor:pointer}
.pg button:disabled{opacity:.4;cursor:default}
@media(max-width:600px){.tctl input{max-width:none;flex-basis:100%}.tctl select{flex:1 1 45%}.dt{font-size:13px}.dt th,.dt td{padding:8px 9px}.dt .co{max-width:130px}}
"""

HTML = """<section class="band tblsec" id="table" aria-labelledby="tT"><div class="in">
<div class="th1"><h2 id="tT">All covered stocks</h2><p class="sub" id="tcount"></p></div>
<div class="tctl" role="group" aria-label="Table filters">
<div class="chips" id="tex" role="tablist" aria-label="Exchange"></div>
<label class="vh" for="tq">Filter by name or symbol</label><input id="tq" type="search" placeholder="Filter by name or symbol" autocomplete="off">
<label class="vh" for="tind">Industry</label><select id="tind"></select>
<label class="vh" for="trt">Rating</label><select id="trt"><option value="">All ratings</option><option value="SB">Strong Buy</option><option value="B">Buy</option><option value="H">Hold</option><option value="S">Sell</option></select>
<label class="vh" for="tsz">Company size</label><select id="tsz"><option value="">All sizes</option><option value="mega">Mega cap (over $200B)</option><option value="large">Large cap ($10B–200B)</option><option value="mid">Mid cap ($2B–10B)</option><option value="small">Small cap (under $2B)</option></select>
<label class="vh" for="tmv">Move today</label><select id="tmv"><option value="">Up or down</option><option value="up">Up today</option><option value="down">Down today</option></select>
<button type="button" class="rst" id="treset">Reset</button>
</div>
<div class="views" id="tview" role="tablist" aria-label="Table view"><button type="button" role="tab" data-v="ov">Overview</button><button type="button" role="tab" data-v="pf">Performance</button><button type="button" role="tab" data-v="an">Analysts</button></div>
<div class="twrap"><table class="dt" id="dt"><thead></thead><tbody></tbody></table></div>
<div class="tfoot"><span id="tnote"></span><span class="pg"><label for="tn">Rows</label><select id="tn"><option>25</option><option selected>50</option><option>100</option><option value="0">All</option></select><button type="button" id="tprev" aria-label="Previous page">‹ Prev</button><span id="tpage"></span><button type="button" id="tnext" aria-label="Next page">Next ›</button></span></div>
</div></section>
"""

JS = r"""
/* table:v1 — all covered stocks */
(function(){const host=document.getElementById('dt');if(!host)return;
 const ROWS=t.markets.flatMap(m=>m.stocks.map(s=>({s,id:m.id})));
 const D={ex:"all",q:"",ind:"",r:"",sz:"",mv:"",v:"ov",s:"mc",d:-1,n:50,p:1};let T=Object.assign({},D);
 try{const u=new URLSearchParams(location.search);Object.keys(D).forEach(k=>{if(u.has(k)){const v=u.get(k);T[k]=typeof D[k]==="number"?(+v||D[k]):v;}});if(u.get("n")==="0")T.n=0;}catch(_){}
 const big=n=>n==null?null:n>=1e12?(n/1e12).toFixed(2)+"T":n>=1e9?(n/1e9).toFixed(2)+"B":n>=1e6?(n/1e6).toFixed(2)+"M":String(n);
 const na='<span class="na">–</span>';
 const pc=v=>v==null||isNaN(v)?na:'<span class="num '+cls(v)+'">'+pct(v)+'</span>';
 const size=n=>n==null?"":n>=2e11?"mega":n>=1e10?"large":n>=2e9?"mid":"small";
 function spark(s){const v=(s.h||[]).slice().reverse().concat([s.pn]).filter(x=>x!=null);if(v.length<2)return na;const lo=Math.min(...v),hi=Math.max(...v),r=hi-lo||1;
  const p=v.map((x,i)=>(i?"L":"M")+(i/(v.length-1)*76+2).toFixed(1)+" "+(22-(x-lo)/r*18).toFixed(1)).join(" ");const up=v[v.length-1]>=v[0];
  return '<svg width="80" height="24" viewBox="0 0 80 24" aria-hidden="true"><path d="'+p+'" fill="none" stroke="'+(up?'var(--up)':'var(--down)')+'" stroke-width="1.6"/></svg>';}
 const SYM={k:"t",l:"Symbol",g:o=>o.s.t,h:o=>'<span class="sym">'+starBtn(o.id,o.s)+esc(o.s.t)+'</span>'};
 const CO={k:"n",l:"Company",g:o=>o.s.n,h:o=>'<span class="co" title="'+esc(o.s.n)+'">'+esc(o.s.n)+'</span>'};
 const PRICE={k:"pn",l:"Price",r:1,g:o=>o.s.pn,h:o=>'<span class="num">'+esc(o.s.p||"–")+'</span>'};
 const DAY={k:"c",l:"% Today",r:1,g:o=>o.s.c,h:o=>pc(o.s.c)};
 const RT={k:"cat",l:"Rating",g:o=>SCORE[o.s.cat]||0,h:o=>'<span class="rb b'+esc(o.s.cat)+'">'+esc(CN[o.s.cat]||o.s.cat)+'</span>'};
 const VIEWS={
  ov:[SYM,CO,{k:"ex",l:"Exchange",g:o=>EXN[o.id],h:o=>'<span class="ex">'+esc(EXN[o.id])+'</span>'},{k:"ind",l:"Industry",g:o=>o.s.ind||"",h:o=>esc(o.s.ind||"–")},
      {k:"mc",l:"Market cap",r:1,g:o=>o.s.mc,h:o=>o.s.mc!=null?'<span class="num">$'+big(o.s.mc)+'</span>':na},PRICE,DAY,RT],
  pf:[SYM,CO,PRICE,DAY].concat(["1D","1W","1M","6M","1Y"].map((l,i)=>({k:"h"+i,l:l,r:1,g:o=>hchg(o.s,i),h:o=>pc(hchg(o.s,i))}))).concat([{k:"sp",l:"Trend",ns:1,h:o=>spark(o.s)}]),
  an:[SYM,CO,RT,{k:"na",l:"Analysts",r:1,g:o=>consInfo(o.s).n,h:o=>{const v=consInfo(o.s).n;return v!=null?'<span class="num">'+v+'</span>':na;}},
      {k:"pt",l:"Avg target",r:1,g:o=>{const c=consInfo(o.s);return c.up;},h:o=>{const c=consInfo(o.s);return c.pt?'<span class="num">'+esc(c.pt)+'</span>':na;}},
      {k:"up",l:"Upside",r:1,g:o=>consInfo(o.s).up,h:o=>pc(consInfo(o.s).up)},
      {k:"la",l:"Latest analyst action",ns:1,h:o=>{const a=(o.s.an||[])[0];return a?'<span class="lt" title="'+esc(a.join(" · "))+'">'+esc(a[1])+' · '+esc(a[3])+' '+esc(a[2])+(a[4]&&a[4]!=="n/a"?' · '+esc(a[4]):'')+' · '+esc(a[5])+'</span>':na;}}]};
 const $=id=>document.getElementById(id);
 const inds=[...new Set(ROWS.map(o=>o.s.ind).filter(Boolean))].sort();
 $('tind').innerHTML='<option value="">All industries</option>'+inds.map(x=>'<option>'+esc(x)+'</option>').join("");
 const cnt=id=>ROWS.filter(o=>id==="all"||o.id===id).length;
 function save(){try{const u=new URLSearchParams(location.search);Object.keys(D).forEach(k=>{if(k==="p"||T[k]===D[k])u.delete(k);else u.set(k,T[k]);});const q=u.toString();history.replaceState(null,"",location.pathname+(q?"?"+q:"")+location.hash);}catch(_){}}
 function filt(){const q=T.q.trim().toLowerCase();return ROWS.filter(o=>(T.ex==="all"||o.id===T.ex)&&(!q||(o.s.n+" "+o.s.t).toLowerCase().includes(q))&&(!T.ind||o.s.ind===T.ind)&&(!T.r||o.s.cat===T.r)&&(!T.sz||size(o.s.mc)===T.sz)&&(!T.mv||(T.mv==="up"?o.s.c>0:o.s.c<0)));}
 function draw(){const cols=VIEWS[T.v]||VIEWS.ov;if(!cols.some(c=>c.k===T.s&&!c.ns)){T.s=T.v==="pf"?"c":T.v==="an"?"up":"mc";T.d=-1;}
  const col=cols.find(c=>c.k===T.s);let xs=filt();
  xs.sort((a,b)=>{const x=col.g(a),y=col.g(b);const nx=x==null||x==="",ny=y==null||y==="";if(nx&&ny)return 0;if(nx)return 1;if(ny)return -1;return (typeof x==="string"?x.localeCompare(y):x-y)*T.d;});
  const tot=xs.length,per=T.n||tot||1,pages=Math.max(1,Math.ceil(tot/per));if(T.p>pages)T.p=pages;const pg=xs.slice((T.p-1)*per,(T.p-1)*per+per);
  host.tHead.innerHTML='<tr>'+cols.map(c=>{const on=c.k===T.s;return '<th scope="col" class="'+(c.r?'r':'')+'"'+(on?' aria-sort="'+(T.d>0?'ascending':'descending')+'"':'')+'>'+(c.ns?esc(c.l):'<button type="button" data-sort="'+c.k+'">'+esc(c.l)+'<span class="ar" aria-hidden="true">'+(on?(T.d>0?'▲':'▼'):'')+'</span></button>')+'</th>';}).join("")+'</tr>';
  host.tBodies[0].innerHTML=pg.length?pg.map(o=>'<tr data-open="'+esc(wkey(o.id,o.s.t))+'">'+cols.map(c=>'<td class="'+(c.r?'r':'')+'">'+c.h(o)+'</td>').join("")+'</tr>').join(""):'<tr><td colspan="'+cols.length+'" class="na" style="padding:18px">No stocks match these filters. <button type="button" class="anb" data-treset="1">Reset filters</button></td></tr>';
  $('tex').innerHTML=[["all","All"]].concat(t.markets.map(m=>[m.id,EXN[m.id]])).map(e=>'<button type="button" role="tab" data-ex="'+e[0]+'" aria-selected="'+(T.ex===e[0])+'">'+esc(e[1])+'<small>'+cnt(e[0])+'</small></button>').join("");
  document.querySelectorAll('#tview button').forEach(b=>b.setAttribute('aria-selected',b.dataset.v===T.v));
  $('tq').value=T.q;$('tind').value=T.ind;$('trt').value=T.r;$('tsz').value=T.sz;$('tmv').value=T.mv;$('tn').value=String(T.n);
  const by=t.markets.map(m=>EXN[m.id]+' '+m.stocks.length).join(' · ');
  $('tcount').innerHTML='<b>'+tot+' of '+ROWS.length+' stocks</b> · '+esc(by);
  $('tpage').textContent='Page '+T.p+' of '+pages;$('tprev').disabled=T.p<=1;$('tnext').disabled=T.p>=pages;
  $('tnote').textContent='Market cap in US dollars, approximate. Prices in each market’s own currency. Click a row for details.';save();}
 const sec=document.getElementById('table');
 sec.addEventListener('click',e=>{const s=e.target.closest('[data-sort]');if(s){const k=s.dataset.sort;if(T.s===k)T.d=-T.d;else{T.s=k;T.d=(k==="t"||k==="n"||k==="ex"||k==="ind")?1:-1;}T.p=1;draw();return;}
  const x=e.target.closest('[data-ex]');if(x){T.ex=x.dataset.ex;T.p=1;draw();return;}
  const v=e.target.closest('#tview button');if(v){T.v=v.dataset.v;T.p=1;draw();return;}
  if(e.target.closest('#treset,[data-treset]')){T=Object.assign({},D,{v:T.v});draw();return;}
  if(e.target.closest('#tprev')){T.p--;draw();sec.querySelector('.twrap').scrollTop=0;return;}if(e.target.closest('#tnext')){T.p++;draw();sec.querySelector('.twrap').scrollTop=0;return;}});
 $('tq').addEventListener('input',e=>{T.q=e.target.value;T.p=1;draw();});
 [['tind','ind'],['trt','r'],['tsz','sz'],['tmv','mv']].forEach(([id,k])=>$(id).addEventListener('change',e=>{T[k]=e.target.value;T.p=1;draw();}));
 $('tn').addEventListener('change',e=>{T.n=+e.target.value;T.p=1;draw();});
 draw();})();
"""


def patch(s):
    if MARK in s:
        return s
    if "/* feat:v1 */" not in s:
        sys.exit("add_table: run add_features.py first")

    def rep(old, new, what):
        nonlocal s
        if s.count(old) != 1:
            sys.exit(f"add_table: expected one '{what}', found {s.count(old)}")
        s = s.replace(old, new)

    i = s.index("</style>", s.index(".tabs{"))
    s = s[:i] + CSS + s[i:]
    rep('\n<nav class="tabs band"', '\n' + HTML + '<nav class="tabs band"', "tabs nav")
    anchor = "/* feat:v1 — clicks */"
    i = s.index(anchor)
    s = s[:i] + JS + s[i:]
    return s


if __name__ == "__main__":
    p = sys.argv[1]
    src = open(p, encoding="utf-8").read()
    out = patch(src)
    open(p, "w", encoding="utf-8").write(out)
