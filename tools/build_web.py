#!/usr/bin/env python3
"""Turn the Claude artifact page of the Daily Stock Market Blog into the
investpulse.uk website version.

Usage: python3 tools/build_web.py <artifact-page.html> <output index.html>

Changes made:
- Google Fonts links -> self-hosted fonts (fonts/fonts.css)
- Google favicon service -> local logos (logos/<domain>.png), initials fallback
- adds colour fallbacks for older browsers (tools/compat_css.py)
- adds the TradingView market screener (loads only after a click)
- adds site favicon, canonical URL and a legal footer (Impressum, privacy, disclaimer)
The blog data and design are otherwise left exactly as they are.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compat_css import add_fallback

SITE = "https://investpulse.uk/"

SCREENER = """<section class="in scr" id="screener" aria-labelledby="scrT">
<h2 id="scrT">Market screener</h2>
<p class="sub">Every listed stock, with live prices, % change today, market cap and sector. Sort by any column. Provided by TradingView; the US view covers NASDAQ and NYSE.</p>
<div class="scrbar" role="tablist" aria-label="Screener market"><button type="button" role="tab" data-mk="america" aria-selected="true">United States</button><button type="button" role="tab" data-mk="uk" aria-selected="false">United Kingdom (LSE)</button><button type="button" role="tab" data-mk="india" aria-selected="false">India (NSE/BSE)</button></div>
<div class="scrbox" id="scrBox"><div class="scrgate"><p><b>The screener is provided by TradingView.</b> Loading it connects your browser to TradingView, Inc. (USA), which receives your IP address and may store cookies. Nothing is loaded until you click. <a href="datenschutz.html#tradingview">Privacy details</a></p><button type="button" class="scrgo" id="scrGo">Load the screener</button></div></div>
</section>"""

SCREENER_CSS = (".scr{padding-block:36px 8px;border-top:1px solid var(--line);margin-top:28px}"
    ".scr h2{font:600 28px/1.1 var(--fd);margin:0 0 4px}"
    ".scrbar{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0 12px}"
    ".scrbar button{font:600 14px var(--ft);color:var(--ink);background:var(--card);border:1px solid var(--line);border-radius:999px;padding:9px 16px;cursor:pointer;min-height:40px}"
    ".scrbar button[aria-selected=true]{background:linear-gradient(120deg,#0d1430,#312e81 70%,#134e4a 130%);color:#fff;border-color:#4f46e5}"
    ".scrbox{border:1px solid var(--line);border-radius:12px;overflow:hidden;background:var(--card);min-height:220px}"
    ".scrgate{display:grid;place-items:center;gap:14px;text-align:center;padding:40px 20px;max-width:620px;margin:0 auto}"
    ".scrgate p{margin:0;color:var(--muted);font-size:15px}.scrgate b{color:var(--ink)}"
    ".scrgo{font:600 15px var(--ft);color:#fff;background:linear-gradient(90deg,#6366f1,#14b8a6);border:0;border-radius:10px;padding:12px 20px;cursor:pointer}"
    ".scrbox .tradingview-widget-copyright{font-size:13px;padding:8px 12px;color:var(--muted)}")

SCREENER_JS = """<script>
(function(){var box=document.getElementById('scrBox'),bar=document.querySelector('.scrbar'),mk='america',on=false;
function dark(){var r=document.documentElement.getAttribute('data-theme');if(r)return r==='dark';return window.matchMedia&&matchMedia('(prefers-color-scheme: dark)').matches;}
function load(){on=true;box.innerHTML='';var c=document.createElement('div');c.className='tradingview-widget-container';
 var w=document.createElement('div');w.className='tradingview-widget-container__widget';c.appendChild(w);
 var cp=document.createElement('div');cp.className='tradingview-widget-copyright';cp.innerHTML='<a href="https://www.tradingview.com/screener/" rel="noopener nofollow" target="_blank">Stock screener by TradingView</a>';c.appendChild(cp);
 var s=document.createElement('script');s.src='https://s3.tradingview.com/external-embedding/embed-widget-screener.js';s.async=true;
 s.text=JSON.stringify({width:'100%',height:640,defaultColumn:'overview',defaultScreen:'most_capitalized',market:mk,showToolbar:true,colorTheme:dark()?'dark':'light',isTransparent:true,locale:'en'});
 c.appendChild(s);box.appendChild(c);}
document.getElementById('scrGo').addEventListener('click',load);
bar.addEventListener('click',function(e){var b=e.target.closest('button');if(!b)return;mk=b.getAttribute('data-mk');
 bar.querySelectorAll('button').forEach(function(x){x.setAttribute('aria-selected',x===b?'true':'false');});if(on)load();});})();
</script>"""


def must_replace(s, old, new, what):
    if old not in s:
        sys.exit(f"build_web: pattern not found ({what}); page structure changed")
    return s.replace(old, new, 1)


def build(src, dst):
    s = open(src, encoding="utf-8").read()

    s = must_replace(s, '<link rel="preconnect" href="https://fonts.googleapis.com">\n', "", "font preconnect")
    s = must_replace(
        s,
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap">',
        '<link rel="stylesheet" href="fonts/fonts.css">\n'
        '<link rel="icon" href="favicon.svg" type="image/svg+xml">\n'
        f'<link rel="canonical" href="{SITE}">',
        "Google Fonts stylesheet",
    )

    s = must_replace(
        s,
        'fav="https://www.google.com/s2/favicons?domain="+encodeURIComponent(s.d||"")+"&sz=128"',
        'fav="logos/"+encodeURIComponent(s.d||"")+".png"',
        "logo source",
    )

    legal_css = (
        ".legal{display:flex;flex-wrap:wrap;gap:8px 20px;align-items:center;justify-content:space-between;"
        "margin-top:28px;padding-top:18px;border-top:1px solid var(--line);font-size:14px;color:var(--muted)}"
        ".legal p{margin:0;max-width:80ch}.legal nav{display:flex;gap:16px}"
        ".legal a{font-weight:600;text-decoration:none}.legal a:hover{text-decoration:underline}\n</style>"
    )
    i = s.index("</style>", s.index(".tabs{"))
    s = s[:i] + legal_css + s[i + len("</style>"):]

    s = must_replace(
        s,
        '<footer class="band"><div class="in fgrid" id="footer"></div></footer>',
        '<footer class="band"><div class="in fgrid" id="footer"></div>'
        '<div class="in legal"><p>Data may be delayed, incomplete or contain errors. Ratings are third-party analyst '
        'opinions, collected for information only, not a recommendation to buy or sell any security.</p>'
        '<nav aria-label="Legal"><a href="impressum.html">Impressum</a><a href="datenschutz.html">Privacy</a></nav></div></footer>',
        "footer",
    )

    s = must_replace(s, '<section class="in arch">', SCREENER + '\n<section class="in arch">', "archive section")
    i = s.index("</style>", s.index(".tabs{"))
    s = s[:i] + SCREENER_CSS + s[i:]
    s = must_replace(s, "</body>", SCREENER_JS + "\n</body>", "body end") if "</body>" in s else s + SCREENER_JS
    s = add_fallback(s)

    if "fonts.googleapis" in s or "s2/favicons" in s:
        sys.exit("build_web: a Google resource is still referenced")
    open(dst, "w", encoding="utf-8").write(s)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    build(sys.argv[1], sys.argv[2])
