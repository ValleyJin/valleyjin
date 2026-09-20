#!/usr/bin/env python3
"""K3I (KOSDAQ 431190) 시세 배지 SVG 생성 — Naver 폴링 API(서버측, CORS 무관).
정적 호스팅이라 완전 실시간은 불가 → Action이 장중 주기적으로 갱신(near real-time)."""
import json, sys, urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "k3i-stock.svg"
URL = "https://polling.finance.naver.com/api/realtime/domestic/stock/431190"


def main():
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0",
                                               "Referer": "https://finance.naver.com/"})
    d = json.load(urllib.request.urlopen(req, timeout=30))["datas"][0]
    price = str(d.get("closePrice", "—"))
    ratio = d.get("fluctuationsRatio")
    code = str((d.get("compareToPreviousPrice") or {}).get("code", "3"))
    up, down = code in ("1", "2"), code in ("4", "5")
    arrow = "▲" if up else ("▼" if down else "—")
    color = "#26c281" if up else ("#f0616d" if down else "#8b949e")
    label = "K3I · KOSDAQ 431190"
    ptxt = "₩" + price
    ctxt = f"{arrow} {ratio}%" if ratio is not None else ""

    def w(s):  # 한글/기호는 넓게
        return sum(9.2 if ord(c) > 0x2000 else 7.2 for c in s)

    pad, gap = 13, 13
    x1 = pad
    x2 = x1 + w(label) + gap
    x3 = x2 + w(ptxt) + gap
    W = int(round(x3 + w(ctxt) + pad))
    H = 30
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" role="img" '
        f'aria-label="K3I KOSDAQ 431190 {ptxt} {ctxt}">'
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="7" fill="#0d1117" stroke="#2a2f37"/>'
        f'<g font-family="ui-monospace,SFMono-Regular,Menlo,monospace">'
        f'<text x="{x1:.0f}" y="19.5" font-size="11.5" fill="#8b949e">{label}</text>'
        f'<text x="{x2:.0f}" y="19.5" font-size="12.5" font-weight="700" fill="#e6edf3">{ptxt}</text>'
        f'<text x="{x3:.0f}" y="19.5" font-size="11.5" font-weight="700" fill="{color}">{ctxt}</text>'
        f'</g></svg>'
    )
    OUT.write_text(svg, encoding="utf-8")
    print("wrote", OUT.name, "|", ptxt, ctxt)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("stock fetch failed, keeping previous badge:", e, file=sys.stderr)
        sys.exit(0)
