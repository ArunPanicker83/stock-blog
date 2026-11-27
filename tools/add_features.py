#!/usr/bin/env python3
"""Add the reader features to the Daily Stock Market Blog page (idempotent).

Features: market-hours clock, watchlist (saved in the visitor's browser),
"What changed" (rating changes), sector view, compare (up to 3 stocks)
and a bigger price chart in the stock pop-up.

Usage: python3 tools/add_features.py <page.html>   (edits in place)
"""
import sys

MARK = "/* feat:v1 */"

CSS = MARK + """
.hours{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,250px),1fr));gap:12px;margin-bottom:20px}
.hr{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px;display:grid;gap:6px}
.hr .h1{display:flex;justify-content:space-between;align-items:center;gap:8px}
.hr .h1 b{font:600 16px var(--fd)}
.hr .clk{font:600 22px var(--fd);letter-spacing:-.01em}
.hr .clk small{font:500 13px var(--ft);color:var(--muted);margin-left:6px}
.hr .cd{font-size:14px;color:var(--muted)}
.pill{font-size:12px;font-weight:700;border-radius:999px;padding:3px 10px;white-space:nowrap;background:var(--zone);color:var(--muted);border:1px solid var(--line)}
.pill.open{background:var(--upbg);color:var(--up);border-color:transparent}
.pill.hol{background:color-mix(in srgb,var(--H) 18%,transparent);color:var(--H);border-color:transparent}
.prog{height:6px;border-radius:999px;background:var(--zone);overflow:hidden}.prog i{display:block;height:100%;background:linear-gradient(90deg,#6366f1,#14b8a6);border-radius:999px}
.row2{margin-top:20px}
.wl{display:grid;gap:6px;max-height:340px;overflow:auto}
.wli{display:grid;grid-template-columns:minmax(0,1fr) auto auto auto auto;gap:10px;align-items:center;padding:8px 10px;border:1px solid var(--line);border-radius:10px;background:var(--card)}
.wli .o{all:unset;cursor:pointer;display:block;min-width:0}
.wli .o b{display:block;font-size:15px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.wli .o span{font-size:13px;color:var(--muted)}
.wli .o:focus-visible{outline:2px solid var(--accent);outline-offset:4px;border-radius:4px}
.xbtn{background:transparent;border:0;color:var(--muted);font-size:18px;cursor:pointer;width:32px;height:32px;border-radius:8px}
.xbtn:hover{background:var(--zone);color:var(--ink)}
.chg{display:grid;gap:0;max-height:340px;overflow:auto}
.chg .ci{display:grid;grid-template-columns:62px minmax(0,1fr);gap:10px;padding:9px 0;border-top:1px solid var(--line);font-size:14px}
.chg .ci:first-child{border-top:0}
.chg .dt{color:var(--muted);font-variant-numeric:tabular-nums}
.chg .ci button{all:unset;cursor:pointer;font-weight:600}
.chg .ci button:hover{text-decoration:underline}
.tag{display:inline-block;font-size:12px;font-weight:700;border-radius:5px;padding:1px 6px;margin-right:6px}
.tag.Up{background:var(--upbg);color:var(--up)}.tag.Down{background:var(--downbg);color:var(--down)}.tag.New{background:var(--zone);color:var(--accent)}
.star{flex:none;background:transparent;border:1px solid var(--line);border-radius:8px;width:36px;height:36px;display:grid;place-items:center;cursor:pointer;color:var(--muted)}
.star svg{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:2}
.star[aria-pressed=true]{color:#f5b301;border-color:#f5b301}.star[aria-pressed=true] svg{fill:#f5b301}
.star:hover{border-color:var(--accent)}
.cmpb[aria-pressed=true]{background:var(--accent);color:#fff;border-color:var(--accent)}
.cmpbar{position:fixed;left:50%;transform:translateX(-50%);bottom:calc(16px + env(safe-area-inset-bottom,0px));z-index:40;display:flex;flex-wrap:wrap;gap:8px 12px;align-items:center;background:#0d1430;color:#fff;border:1px solid #4f46e5;border-radius:14px;padding:10px 12px 10px 16px;box-shadow:0 16px 40px -12px rgba(8,12,30,.6);max-width:calc(100vw - 32px)}
.cmpbar b{font-size:14px}.cmpbar span{font-size:14px;color:#c7d2fe}
.cmpbar button{font:600 14px var(--ft);border-radius:8px;padding:8px 12px;cursor:pointer;border:0}
.cmpbar .go{background:linear-gradient(90deg,#6366f1,#14b8a6);color:#fff}.cmpbar .cl{background:rgba(255,255,255,.12);color:#fff}
.ctab{width:100%;border-collapse:collapse;font-size:14px}
.ctab th,.ctab td{padding:9px 10px;border-bottom:1px solid var(--line);text-align:right;vertical-align:top}
.ctab th:first-child,.ctab td:first-child{text-align:left;color:var(--muted);font-weight:600}
.ctab thead th{color:var(--ink);font:600 15px var(--fd)}
.bigc{margin-top:14px;border:1px solid var(--line);border-radius:12px;padding:14px;background:var(--card)}
.bigc h4{margin:0 0 2px;font:600 16px var(--fd)}
.bigc .cap{font-size:13px;color:var(--muted);margin:6px 0 0}
.bigc svg{width:100%;height:auto;display:block;margin-top:8px}
.secsum{font-size:14px;color:var(--muted);font-weight:500}
.cds{display:none}
@media(max-width:600px){.hours{grid-template-columns:repeat(3,minmax(0,1fr));gap:6px}.hr{padding:10px;gap:4px}.hr .h1{flex-direction:column;align-items:flex-start;gap:4px}.hr .h1 b{font-size:14px}.hr .clk{font-size:18px}.hr .clk small{display:none}.hr .cd{font-size:12px}.cdl{display:none}.cds{display:inline}.pill{font-size:11px;padding:2px 8px}.wli{grid-template-columns:minmax(0,1fr) auto auto auto}.wli .rb{display:none}.ctab{font-size:13px}.ctab th,.ctab td{padding:7px 6px}}
"""

ZONE_ROW = ('<div class="in top2 row2"><div class="panel"><h2>Your watchlist</h2><p class="sub">Saved in this browser only. '
            'Tap the star on any stock to add it.</p><div id="wlp"></div></div>'
            '<div class="panel"><h2>What changed</h2><p class="sub">Analyst upgrades, downgrades and new coverage in the past two weeks, '
            'plus consensus changes since the previous day.</p><div id="chg"></div></div></div>')

PRE = r"""
/* feat:v1 — shared helpers */
const STO={get(k){try{return JSON.parse(localStorage.getItem(k)||"null");}catch(_){return null;}},set(k,v){try{localStorage.setItem(k,JSON.stringify(v));}catch(_){}}};
const wkey=(id,tk)=>id+"|"+tk;
let WL=new Set(Array.isArray(STO.get('ipulse-watch'))?STO.get('ipulse-watch'):[]);
let CMP=[];
const STAR='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z" stroke-linejoin="round"/></svg>';
const starBtn=(id,s)=>{const on=WL.has(wkey(id,s.t));return '<button type="button" class="star" data-w="'+esc(wkey(id,s.t))+'" aria-pressed="'+on+'" aria-label="'+(on?'Remove ':'Add ')+esc(s.n)+(on?' from':' to')+' watchlist" title="Watchlist">'+STAR+'</button>';};
const cmpBtn=(id,s)=>{const on=CMP.includes(wkey(id,s.t));return '<button type="button" class="anb cmpb" data-cmp="'+esc(wkey(id,s.t))+'" aria-pressed="'+on+'">'+(on?'✓ Comparing':'+ Compare')+'</button>';};
const SCORE={SB:4,B:3,H:2,S:1};
const scoreLbl=v=>v>=3.5?"Strong Buy":v>=2.75?"Buy":v>=1.75?"Hold":"Sell";
function findStock(k){const [id,tk]=k.split("|");const m=byId[id];const s=m&&m.stocks.find(x=>x.t===tk);if(s)return {s,id,day:t,isToday:true};
 for(const d of days){const mm=d.markets.find(x=>x.id===id);const ss=mm&&mm.stocks.find(x=>x.t===tk);if(ss)return {s:ss,id,day:d,isToday:d===t};}return null;}
function consInfo(s){const c=String(s.cons||"");const n=(c.match(/(\d+)\s+analysts/)||[])[1];const m=c.match(/avg PT\s*([^\d·]{0,3})([\d,]+(?:\.\d+)?)\s*(p\b)?/);
 const pt=m?(m[1]+m[2]+(m[3]||"")).trim():null;const ptn=m?parseFloat(m[2].replace(/,/g,"")):null;
 const pc=String(s.p||"").replace(/^[≈~\s]+/,"");const cp=/p\s*$/.test(pc)?"p":(pc.match(/^[^\d]*/)||[""])[0].trim();const ct=m?(m[3]?"p":m[1].trim()):"";
 return {n:n?+n:null,pt:pt,up:ptn&&s.pn&&cp===ct?(ptn/s.pn-1)*100:null};}
function hchg(s,i){const v=s.h&&s.h[i];return v!=null&&s.pn!=null?(s.pn/v-1)*100:null;}
function bigChart(s,id){const lab=["1Y ago","6M ago","1M ago","1W ago","1D ago","Latest"];const raw=(s.h||[]).slice().reverse().concat([s.pn]);
 const pts=raw.map((v,i)=>[i,v]).filter(p=>p[1]!=null);if(pts.length<2)return '<div class="bigc"><h4>Price history</h4><p class="cap">Not enough verified closing prices for a chart yet.</p></div>';
 const W=600,H=230,L=12,R=12,T=26,B=34,vs=pts.map(p=>p[1]),lo=Math.min(...vs),hi=Math.max(...vs),pad=(hi-lo)*0.12||hi*0.02||1;
 const y0=lo-pad,y1=hi+pad,X=i=>L+i/5*(W-L-R),Y=v=>T+(y1-v)/(y1-y0)*(H-T-B);
 const up=vs[vs.length-1]>=vs[0],col=up?"var(--up)":"var(--down)",cur=curOf(s,id);
 const line=pts.map((p,i)=>(i?"L":"M")+X(p[0]).toFixed(1)+" "+Y(p[1]).toFixed(1)).join(" ");
 const area=line+" L"+X(pts[pts.length-1][0]).toFixed(1)+" "+(H-B)+" L"+X(pts[0][0]).toFixed(1)+" "+(H-B)+" Z";
 const gid="g"+Math.random().toString(36).slice(2,8);
 let g='<svg viewBox="0 0 '+W+' '+H+'" role="img" aria-label="Closing prices at six points over the past year"><defs><linearGradient id="'+gid+'" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="'+(up?'#22c55e':'#ef4444')+'" stop-opacity=".22"/><stop offset="1" stop-color="'+(up?'#22c55e':'#ef4444')+'" stop-opacity="0"/></linearGradient></defs>';
 [0,1,2,3,4,5].forEach(i=>{g+='<line x1="'+X(i)+'" x2="'+X(i)+'" y1="'+T+'" y2="'+(H-B)+'" stroke="var(--line)" stroke-dasharray="3 4"/><text x="'+X(i)+'" y="'+(H-10)+'" text-anchor="'+(i===0?'start':i===5?'end':'middle')+'" font-size="12" fill="var(--muted)">'+lab[i]+'</text>';});
 g+='<path d="'+area+'" fill="url(#'+gid+')"/><path d="'+line+'" fill="none" stroke="'+col+'" stroke-width="2.5" stroke-linejoin="round"/>';
 pts.forEach((p,k)=>{const x=X(p[0]),yy=Y(p[1]);g+='<circle cx="'+x+'" cy="'+yy+'" r="4" fill="var(--card)" stroke="'+col+'" stroke-width="2"/><text x="'+x+'" y="'+(yy-10)+'" text-anchor="'+(p[0]===0?'start':p[0]===5?'end':'middle')+'" font-size="12" font-weight="600" fill="var(--ink)">'+esc(fmt(p[1],cur))+'</text>';});
 g+='</svg>';const ch=(vs[vs.length-1]/vs[0]-1)*100;
 return '<div class="bigc"><h4>Price history</h4><span class="num '+cls(ch)+'" style="font-weight:700">'+pct(ch)+'</span> <span class="cap" style="display:inline">since '+lab[pts[0][0]].replace(" ago"," ago")+'</span>'+g+
 '<p class="cap">The line joins verified closing prices on these dates; it isn’t a full daily chart. Missing points weren’t verified.</p></div>';}
"""

POST = r"""
/* feat:v1 — market hours */
const MH={us:{tz:"America/New_York",city:"New York",o:570,c:960},uk:{tz:"Europe/London",city:"London",o:480,c:990},in:{tz:"Asia/Kolkata",city:"Mumbai",o:555,c:930}};
const HOL={us:["2026-12-25","2027-01-01"],uk:["2026-12-25","2026-12-28","2027-01-01"],in:["2026-12-25"]};
const EARLY={"us:2026-11-27":780,"us:2026-12-24":780,"uk:2026-12-24":750,"uk:2026-12-31":750};
function tzNow(tz,ms){const p={};new Intl.DateTimeFormat("en-GB",{timeZone:tz,year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit",hourCycle:"h23",weekday:"short"}).formatToParts(new Date(ms)).forEach(x=>p[x.type]=x.value);
 return {date:p.year+"-"+p.month+"-"+p.day,wd:p.weekday,min:(+p.hour)*60+(+p.minute),hm:p.hour+":"+p.minute};}
const dur=m=>{m=Math.max(0,Math.round(m));const d=Math.floor(m/1440),h=Math.floor(m%1440/60),mm=m%60;return (d?d+"d ":"")+(d||h?h+"h ":"")+mm+"m";};
function isClosedDay(id,n){if(n.wd==="Sat"||n.wd==="Sun")return "Weekend";if((HOL[id]||[]).includes(n.date))return "Holiday";const m=byId[id];if(m&&m.closed&&t.date===n.date)return "Holiday";return "";}
function sess(id,ms){const cfg=MH[id],n=tzNow(cfg.tz,ms),cl=EARLY[id+":"+n.date]||cfg.c,off=isClosedDay(id,n);
 if(!off&&n.min>=cfg.o&&n.min<cl)return {n,open:true,left:cl-n.min,prog:(n.min-cfg.o)/(cl-cfg.o),early:cl!==cfg.c,cl};
 let k=(!off&&n.min<cfg.o)?0:1;for(;k<10;k++){const nn=tzNow(cfg.tz,ms+k*864e5);if(!isClosedDay(id,nn))break;}
 const wait=k===0?cfg.o-n.min:(k*1440-n.min+cfg.o);const nn=tzNow(cfg.tz,ms+k*864e5);return {n,open:false,off,wait,nextWd:k===0?"today":k===1?"tomorrow":nn.wd};}
function hhmm(m){return String(Math.floor(m/60)).padStart(2,"0")+":"+String(m%60).padStart(2,"0");}
function drawHours(){const el=document.getElementById('hours');if(!el)return;const ms=Date.now();
 el.innerHTML=t.markets.map(m=>{const id=m.id,cfg=MH[id];if(!cfg)return "";const s=sess(id,ms);
  const pill=s.open?'<span class="pill open">Open</span>':s.off==="Holiday"?'<span class="pill hol">Holiday</span>':'<span class="pill">Closed</span>';
  const cd=s.open?'<span class="cdl">Closes in '+dur(s.left)+' · at '+hhmm(s.cl)+(s.early?' (early close)':'')+'</span><span class="cds">Closes in '+dur(s.left)+'</span>':'<span class="cdl">Opens '+s.nextWd+' at '+hhmm(cfg.o)+' · in '+dur(s.wait)+'</span><span class="cds">Opens in '+dur(s.wait)+'</span>';
  return '<div class="hr"><div class="h1"><b>'+esc(SHORT[id]||m.name)+'</b>'+pill+'</div><div class="clk num">'+s.n.hm+'<small>'+esc(cfg.city)+' time</small></div><div class="cd">'+cd+'</div>'+(s.open?'<div class="prog" aria-hidden="true"><i style="width:'+(s.prog*100).toFixed(1)+'%"></i></div>':'')+'</div>';}).join("");}
drawHours();setInterval(drawHours,20000);

/* feat:v1 — watchlist */
function drawWL(){const el=document.getElementById('wlp');if(!el)return;const xs=[...WL].map(findStock).filter(Boolean);
 if(!xs.length){el.innerHTML='<p class="empty">Your watchlist is empty. Tap ☆ on any stock card to keep it here, across all three markets.</p>';return;}
 el.innerHTML='<div class="wl">'+xs.map(o=>{const s=o.s,k=wkey(o.id,s.t);return '<div class="wli"><button class="o" data-open="'+esc(k)+'"><b>'+esc(s.n)+'</b><span>'+esc(s.t)+' · '+esc(EXN[o.id])+(o.isToday?'':' · from '+esc(o.day.label))+'</span></button><span class="num" style="font-weight:600">'+esc(s.p)+'</span><span class="cg num '+cls(s.c)+'">'+(s.cn?esc(s.cn):pct(s.c))+'</span><span class="rb b'+esc(s.cat)+'">'+esc(CN[s.cat]||s.cat)+'</span><button class="xbtn" data-w="'+esc(k)+'" aria-label="Remove '+esc(s.n)+' from watchlist">×</button></div>';}).join("")+'</div>';}
function syncBtns(){document.querySelectorAll('[data-w].star').forEach(b=>{const on=WL.has(b.dataset.w);b.setAttribute('aria-pressed',on);});
 document.querySelectorAll('[data-cmp]').forEach(b=>{const on=CMP.includes(b.dataset.cmp);b.setAttribute('aria-pressed',on);b.textContent=on?'✓ Comparing':'+ Compare';});
 const sb=document.querySelector('#seg button[data-c="watch"] span');if(sb){const m=byId[state.tab];sb.textContent=m?m.stocks.filter(s=>WL.has(wkey(m.id,s.t))).length:0;}}

/* feat:v1 — what changed */
const MON={Jan:0,Feb:1,Mar:2,Apr:3,May:4,Jun:5,Jul:6,Aug:7,Sep:8,Oct:9,Nov:10,Dec:11};
function pd(x){const m=String(x||"").match(/([A-Z][a-z]{2})\s+(\d{1,2}),\s*(\d{4})/);return m&&MON[m[1]]!=null?Date.UTC(+m[3],MON[m[1]],+m[2]):null;}
function drawChg(){const el=document.getElementById('chg');if(!el)return;const D0=Date.parse(t.date+"T00:00:00Z"),items=[],prev=days[1];
 t.markets.forEach(m=>m.stocks.forEach(s=>{
  if(prev){const pm=prev.markets.find(x=>x.id===m.id),ps=pm&&pm.stocks.find(x=>x.t===s.t);if(ps&&ps.cat&&s.cat&&ps.cat!==s.cat)items.push({d:D0,id:m.id,s,kind:(SCORE[s.cat]>SCORE[ps.cat])?"Up":"Down",txt:'Consensus '+CN[ps.cat]+' → '+CN[s.cat]});}
  (s.an||[]).forEach(r=>{const a=String(r[3]||"");if(!/upgrad|downgrad|initiat/i.test(a))return;const dd=pd(r[5]);if(dd==null||D0-dd>14*864e5||dd>D0+864e5)return;
   items.push({d:dd,id:m.id,s,kind:/upgrad/i.test(a)?"Up":/downgrad/i.test(a)?"Down":"New",txt:esc(r[1])+' '+(/initiat/i.test(a)?'starts at':/upgrad/i.test(a)?'upgrades to':'downgrades to')+' '+esc(r[2])+(r[4]&&r[4]!=="n/a"?' · target '+esc(r[4]):'')});});}));
 items.sort((a,b)=>b.d-a.d);
 if(!items.length){el.innerHTML='<p class="empty">No upgrades, downgrades or new coverage in the past two weeks among the stocks covered here.</p>';return;}
 const fd=d=>new Date(d).toLocaleDateString("en-GB",{day:"numeric",month:"short",timeZone:"UTC"});
 el.innerHTML='<div class="chg">'+items.map(o=>'<div class="ci"><span class="dt">'+fd(o.d)+'</span><span><span class="tag '+o.kind+'">'+(o.kind==="Up"?"Upgrade":o.kind==="Down"?"Downgrade":"New")+'</span><button data-open="'+esc(wkey(o.id,o.s.t))+'">'+esc(o.s.n)+'</button> <span style="color:var(--muted)">'+esc(o.s.t)+' · '+esc(EXN[o.id])+'</span><br>'+o.txt+'</span></div>').join("")+'</div>';}
drawWL();drawChg();

/* feat:v1 — compare */
const cbar=document.getElementById('cmpbar');
function drawBar(){if(!cbar)return;if(!CMP.length){cbar.hidden=true;return;}cbar.hidden=false;
 cbar.innerHTML='<b>Compare</b><span>'+CMP.map(k=>esc(k.split("|")[1])).join(" · ")+(CMP.length<2?' · pick one more':'')+'</span>'+(CMP.length>1?'<button class="go" data-cgo="1">Compare '+CMP.length+'</button>':'')+'<button class="cl" data-cclr="1">Clear</button>';}
function openCompare(){const xs=CMP.map(findStock).filter(Boolean);if(xs.length<2)return;
 const row=(lab,f)=>'<tr><td>'+lab+'</td>'+xs.map(o=>'<td>'+f(o.s,o.id)+'</td>').join("")+'</tr>';
 const ch=v=>'<span class="num '+cls(v)+'">'+pct(v)+'</span>';
 openDlg('Compare '+xs.length+' stocks','<div class="scroll"><table class="ctab"><thead><tr><th></th>'+xs.map(o=>'<th>'+esc(o.s.n)+'<br><small style="color:var(--muted);font:500 13px var(--ft)">'+esc(o.s.t)+'</small></th>').join("")+'</tr></thead><tbody>'+
  row('Exchange',(s,id)=>esc(EXN[id]))+row('Industry',s=>esc(s.ind||'n/a'))+row('Price',s=>'<b class="num">'+esc(s.p)+'</b>')+row('Today',s=>s.cn?esc(s.cn):ch(s.c))+
  row('Consensus',s=>'<span class="rb b'+esc(s.cat)+'">'+esc(CN[s.cat]||s.cat)+'</span>')+row('Analysts',s=>{const c=consInfo(s);return c.n!=null?c.n:'n/a';})+
  row('Average target',s=>{const c=consInfo(s);return c.pt?esc(c.pt):'n/a';})+row('Upside to target',s=>{const c=consInfo(s);return c.up!=null?ch(c.up):'n/a';})+
  row('1 week',s=>ch(hchg(s,1)))+row('1 month',s=>ch(hchg(s,2)))+row('6 months',s=>ch(hchg(s,3)))+row('1 year',s=>ch(hchg(s,4)))+
  '</tbody></table></div><p class="lead" style="margin-top:12px">Prices are in each market’s own currency, so compare percentages rather than prices. n/a means the figure wasn’t verified.</p>');}

/* feat:v1 — clicks */
document.addEventListener('click',e=>{const w=e.target.closest('[data-w]');if(w){const k=w.dataset.w;if(WL.has(k))WL.delete(k);else WL.add(k);STO.set('ipulse-watch',[...WL]);syncBtns();drawWL();if(state.cat==="watch"){const m=byId[state.tab];m&&upd(m);}return;}
 const c=e.target.closest('[data-cmp]');if(c){const k=c.dataset.cmp;if(CMP.includes(k))CMP=CMP.filter(x=>x!==k);else{CMP.push(k);if(CMP.length>3)CMP.shift();}syncBtns();drawBar();return;}
 if(e.target.closest('[data-cgo]')){openCompare();return;}if(e.target.closest('[data-cclr]')){CMP=[];syncBtns();drawBar();return;}
 const o=e.target.closest('[data-open]');if(o){const f=findStock(o.dataset.open);if(f)openFromLocal(f);}});
"""


def patch(s):
    if MARK in s:
        return s

    def rep(old, new, what, count=1):
        nonlocal s
        n = s.count(old)
        if n != count:
            sys.exit(f"add_features: expected {count} of '{what}', found {n}")
        s = s.replace(old, new)

    # CSS (before the end of the main stylesheet)
    i = s.index("</style>", s.index(".tabs{"))
    s = s[:i] + CSS + s[i:]
    # HTML hosts
    rep('<section class="zone band"><div class="in top2">',
        '<section class="zone band"><div class="in hours" id="hours" aria-label="Market hours"></div><div class="in top2">', "zone start")
    rep('<footer class="band">', '<div class="cmpbar" id="cmpbar" hidden></div>\n<footer class="band">', "footer")
    # helpers before tabs are built
    rep("const tabs=document.getElementById('tabs');", PRE + "const tabs=document.getElementById('tabs');", "tabs const")
    # card: star + compare
    rep("""<span class="rb b'+esc(s.cat)+'">'+esc(CN[s.cat]||s.cat)+'</span></div>'+\n '<div class="pr">""",
        """<span class="rb b'+esc(s.cat)+'">'+esc(CN[s.cat]||s.cat)+'</span>'+starBtn(id,s)+'</div>'+\n '<div class="pr">""", "card rating badge")
    rep("""(s.src?'<a href="'+esc(s.src)+'" target="_blank" rel="noopener">Rating source</a>':"")""",
        """(s.src?'<a href="'+esc(s.src)+'" target="_blank" rel="noopener">Rating source</a>':"")+cmpBtn(id,s)""", "card links")
    rep("""'<div class="cons">'+esc(s.cons)+'</div><p class="why">'""",
        """'<div class="cons">'+esc(s.cons)+'</div>'+(s.ind?'<p class="pt">'+esc(s.ind)+'</p>':'')+'<p class="why">'""", "card cons")
    # list filter: watchlist
    rep("""(state.cat==="all"||s.cat===state.cat)""",
        """(state.cat==="all"||(state.cat==="watch"?WL.has(wkey(m.id,s.t)):s.cat===state.cat))""", "list filter")
    # cards: watch empty text + sector grouping
    rep("""function cards(m){const xs=list(m);if(!xs.length)return '<p class="empty" style="margin-top:20px">No stocks match. Clear the search or pick another rating.</p>';""",
        """function cards(m){const xs=list(m);if(!xs.length)return '<p class="empty" style="margin-top:20px">'+(state.cat==="watch"?'None of your watchlist stocks are in this market. Tap ☆ on a card to add one.':'No stocks match. Clear the search or pick another rating.')+'</p>';
 if(state.sort==="sector"){const g={};xs.forEach(s=>{(g[s.ind||"Other"]=g[s.ind||"Other"]||[]).push(s);});
  return Object.entries(g).sort((a,b)=>b[1].length-a[1].length||a[0].localeCompare(b[0])).map(([k,v])=>{const sc=v.reduce((a,s)=>a+(SCORE[s.cat]||2),0)/v.length;const cs=v.filter(s=>s.c!=null);const ac=cs.length?cs.reduce((a,s)=>a+s.c,0)/cs.length:null;
   return '<div class="lane"><h3>'+esc(k)+'<small>'+v.length+' stock'+(v.length>1?'s':'')+' · average rating '+scoreLbl(sc)+' · average move <span class="num '+cls(ac)+'">'+pct(ac)+'</span></small></h3><div class="grid">'+v.map(s=>card(s,m.id)).join("")+'</div></div>';}).join("");}""", "cards start")
    rep("""[["all","All"]].concat(CATS).map(c=>{const k=c[0]==="all"?m.stocks.length:m.stocks.filter(s=>s.cat===c[0]).length;""",
        """[["all","All"]].concat(CATS).concat([["watch","★ Watchlist"]]).map(c=>{const k=c[0]==="all"?m.stocks.length:c[0]==="watch"?m.stocks.filter(s=>WL.has(wkey(m.id,s.t))).length:m.stocks.filter(s=>s.cat===c[0]).length;""", "seg")
    rep('<option value="rating">Group by rating</option>', '<option value="rating">Group by rating</option><option value="sector">Group by sector</option>', "sort option")
    # bigger chart in stock pop-up
    rep("""'</div>'+card(s,id)+'<div class="extra">'""", """'</div>'+card(s,id)+bigChart(s,id)+'<div class="extra">'""", "openStock")
    # post code before the final closing of the main block
    anchor = "document.getElementById('footer').innerHTML="
    i = s.index(anchor)
    j = s.index("\n", i)
    s = s[:j + 1] + POST + s[j + 1:]
    return s


if __name__ == "__main__":
    p = sys.argv[1]
    src = open(p, encoding="utf-8").read()
    out = patch(src)
    open(p, "w", encoding="utf-8").write(out)
