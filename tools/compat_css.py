"""Add plain-colour fallbacks for browsers without CSS light-dark() support
(roughly browsers older than mid-2024). Without this, every colour token is
invalid there: borders vanish and the sticky market bar turns transparent."""
import re

MARK = "/* compat: fallback for browsers without light-dark() */"
TOKEN = re.compile(r"(--[\w-]+):light-dark\(([^,()]+),([^()]+)\)")


def add_fallback(s, test="color:light-dark(#000,#fff)"):
    if MARK in s:
        return s
    toks = TOKEN.findall(s)
    if not toks:
        return s
    light = ";".join(f"{n}:{a.strip()}" for n, a, b in toks)
    dark = ";".join(f"{n}:{b.strip()}" for n, a, b in toks)
    css = (f"\n{MARK}\n@supports not ({test}){{"
           f":root{{{light}}}"
           f"@media(prefers-color-scheme:dark){{:root:not([data-theme=light]){{{dark}}}}}"
           f":root[data-theme=dark]{{{dark}}}}}\n")
    # insert right after the :root rule that defines the tokens
    first = s.index(toks[0][0] + ":light-dark(")
    end = s.index("}", s.index(";--fd" if ";--fd" in s[first:] else toks[-1][0], first))
    return s[:end + 1] + css + s[end + 1:]
