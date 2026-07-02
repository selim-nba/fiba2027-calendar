#!/usr/bin/env python3
"""Generate ICS calendars for FIBA 2027 World Cup from FIBA (authoritative, auto-updating).

- docs/turkiye.ics  : Türkiye matches in European qualifiers (+ World Cup once fixtures known)
- docs/worldcup.ics : all 2027 FIBA Basketball World Cup tournament matches (when published)

Data source: FIBA website embedded Next.js games JSON (authoritative dates/times/venues).
Replaces the earlier Wikipedia source, which had stale/wrong dates (e.g. Türkiye-İsviçre
was shown 5 Jul 2026 Sunday; FIBA confirms 6 Jul 2026 Monday, 19:00 İstanbul).
"""
import json, re, sys, datetime, urllib.request, urllib.parse, os
from zoneinfo import ZoneInfo

OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")
os.makedirs(OUTDIR, exist_ok=True)
IST = ZoneInfo("Europe/Istanbul")
UA = "Mozilla/5.0 (compatible: fiba2027-calendar-bot/1.0; +https://github.com/selim-nba/fiba2027-calendar)"
EQ_SLUG = "fiba-basketball-world-cup-2027-european-qualifiers"
WC_SLUG = "fiba-basketball-world-cup-2027"

# ---------- FIBA team code -> ISO 3166-1 alpha-2 (for flag emoji) ----------
# FIBA uses IOC-ish codes that differ from ISO for several countries.
FIBA_CODE_ISO = {
 "AUT":"AT","BEL":"BE","BIH":"BA","CRO":"HR","CYP":"CY","CZE":"CZ","DEN":"DK","ESP":"ES",
 "EST":"EE","FIN":"FI","FRA":"FR","GBR":"GB","GEO":"GE","GER":"DE","GRE":"GR","HUN":"HU",
 "ISL":"IS","ISR":"IL","ITA":"IT","LAT":"LV","LTU":"LT","MNE":"ME","NED":"NL","POL":"PL",
 "POR":"PT","ROU":"RO","SLO":"SI","SRB":"RS","SUI":"CH","SWE":"SE","TUR":"TR","UKR":"UA",
 "SVK":"SK","BUL":"BG","LUX":"LU","ALB":"AL","NOR":"NO","RUS":"RU","BLR":"BY","MDA":"MD",
 "TUR":"TR",
 # World Cup / other FIBA codes
 "USA":"US","ARG":"AR","AUS":"AU","BRA":"BR","CAN":"CA","CHN":"CN","EGY":"EG","IRN":"IR",
 "JPN":"JP","MEX":"MX","NZL":"NZ","NGA":"NG","PHI":"PH","PUR":"PR","SEN":"SN","SSD":"SS",
 "ANG":"AO","CPV":"CV","DOM":"DO","CIV":"CI","JOR":"JO","LBN":"LB","TUN":"TN","VEN":"VE",
 "QAT":"QA","KOR":"KR","TPE":"TW","COL":"CO","URU":"UY","PAR":"PY","CHI":"CL","MAS":"MY",
 "JOR":"JO",
}
# ---------- FIBA shortName (English) -> Turkish ----------
TR_NAMES = {
 "Austria":"Avusturya","Belgium":"Belçika","Bosnia and Herzegovina":"Bosna-Hersek",
 "Bulgaria":"Bulgaristan","Croatia":"Hırvatistan","Cyprus":"Kıbrıs","Czech Republic":"Çekya",
 "Denmark":"Danimarka","Estonia":"Estonya","Finland":"Finlandiya","France":"Fransa",
 "Georgia":"Gürcistan","Germany":"Almanya","Great Britain":"Büyük Britanya","Greece":"Yunanistan",
 "Hungary":"Macaristan","Iceland":"İzlanda","Israel":"İsrail","Italy":"İtalya","Latvia":"Letonya",
 "Lithuania":"Litvanya","Luxembourg":"Lüksemburg","Montenegro":"Karadağ","Netherlands":"Hollanda",
 "Norway":"Norveç","Poland":"Polonya","Portugal":"Portekiz","Romania":"Romanya","Russia":"Rusya",
 "Serbia":"Sırbistan","Slovakia":"Slovakya","Slovenia":"Slovenya","Spain":"İspanya",
 "Sweden":"İsveç","Switzerland":"İsviçre","Türkiye":"Türkiye","Turkey":"Türkiye","Ukraine":"Ukrayna",
 "United States":"ABD","USA":"ABD","Argentina":"Arjantin","Australia":"Avustralya","Brazil":"Brezilya",
 "Canada":"Kanada","China":"Çin","Egypt":"Mısır","Iran":"İran","Japan":"Japonya","Mexico":"Meksika",
 "New Zealand":"Yeni Zelanda","Nigeria":"Nijerya","Philippines":"Filipinler","Puerto Rico":"Porto Riko",
 "Senegal":"Senegal","South Sudan":"Güney Sudan","Angola":"Angola","Cape Verde":"Yeşil Burun Adaları",
 "Dominican Republic":"Dominik Cumhuriyeti","Ivory Coast":"Fildişi Sahili","Jordan":"Ürdün",
 "Lebanon":"Lübnan","Tunisia":"Tunus","Venezuela":"Venezuela","Qatar":"Katar","South Korea":"Güney Kore",
 "Chinese Taipei":"Çin Taipei","Colombia":"Kolombiya","Uruguay":"Uruguay","Paraguay":"Paraguay",
 "Chile":"Şili","Malaysia":"Malezya",
}
ROUND_TR = {"1st Round":"1. Tur","2nd Round":"2. Tur","3rd Round":"3. Tur","4th Round":"4. Tur"}

def flag(code):
    iso = FIBA_CODE_ISO.get(code)
    if not iso or len(iso) != 2:
        return ""
    return chr(0x1F1E6 + (ord(iso[0]) - ord('A'))) + chr(0x1F1E6 + (ord(iso[1]) - ord('A')))

def tr_name(short):
    return TR_NAMES.get(short, short)

def esc(s):
    return str(s).replace("\\", "\\\\").replace("\n", "\\n").replace(",", "\\,").replace(";", "\\;")

# ---------- FIBA fetch + parse ----------
def fetch_fiba_html(slug):
    """Fetch the FIBA games page HTML (contains embedded games JSON). Returns text or ''."""
    url = f"https://www.fiba.basketball/en/events/{slug}/games"
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en"})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.read().decode("utf-8", "replace")
    except Exception as e:
        print(f"  !! FIBA fetch failed for {slug!r}: {e}", file=sys.stderr)
        return ""

def parse_fiba_games(html):
    """Parse the embedded games JSON. Returns list of game dicts (empty on failure).

    FIBA embeds the games array (sometimes twice: list + calendar view); we dedupe
    by gameId. gameId precedes teamA in each game object, so we use gameId positions
    as game boundaries (splitting on teamA alone misaligns the id by one game).
    """
    if not html:
        return []
    h = html.replace('\\\"', '"')  # normalise escaped quotes
    games = {}
    # positions of each "gameId":<digits>
    idx = [m.start() for m in re.finditer(r'"gameId":(\d+)', h)]
    idx.append(len(h))  # sentinel end
    for k in range(len(idx) - 1):
        block = h[idx[k]:idx[k + 1]]
        gid = re.match(r'"gameId":(\d+)', block)
        if not gid:
            continue
        gid = gid.group(1)
        def first(rx):
            m = re.search(rx, block)
            return m.group(1) if m else ""
        # teamA = first teamA object; teamB = second teamX code/name
        ta = re.search(r'"teamA":\{"teamId":\d+,"organisationId":\d+,"code":"([^"]+)","officialName":"[^"]*","shortName":"([^"]*)"', block)
        tb = re.search(r'"teamB":\{"teamId":\d+,"organisationId":\d+,"code":"([^"]+)","officialName":"[^"]*","shortName":"([^"]*)"', block)
        if not ta or not tb:
            continue
        sa = first(r'"teamAScore":(\d+|null)')
        sb = first(r'"teamBScore":(\d+|null)')
        cps = first(r'"currentPeriodStatus":"([^"]*)"')
        lgs = first(r'"liveGameStatus":(\d+)')
        games[gid] = {
            "gameId": int(gid),
            "ca": ta.group(1), "na": ta.group(2),
            "cb": tb.group(1), "nb": tb.group(2),
            "sa": None if sa in ("", "null") else int(sa),
            "sb": None if sb in ("", "null") else int(sb),
            "dtu": first(r'"gameDateTimeUTC":"([^"]*)"'),
            "dtl": first(r'"gameDateTime":"([^"]*)"'),
            "tz": first(r'"ianaTimeZone":"([^"]*)"'),
            "city": first(r'"hostCity":"([^"]*)"').strip().rstrip('\\\\ \' "'),
            "venue": first(r'"venueName":"([^"]*)"').strip().rstrip('\\\\ \' "'),
            "postponed": first(r'"isPostponed":(true|false)') == "true",
            "round": first(r'"roundName":"([^"]*)"'),
            "group": first(r'"groupPairingCode":"([^"]*)"'),
            "finished": cps == "E" or lgs == "999",
        }
    return list(games.values())

def parse_utc(iso):
    # "2026-07-06T16:00:00"
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})", iso)
    if not m:
        return None
    return datetime.datetime(int(m[1]), int(m[2]), int(m[3]),
                             int(m[4]), int(m[5]), int(m[6]), tzinfo=ZoneInfo("UTC"))

# ---------- ICS build ----------
def build_ics(matches, path, calname, caldesc):
    L = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//FIBA 2027 Calendar//TR//",
         "CALSCALE:GREGORIAN", "METHOD:PUBLISH", f"X-WR-CALNAME:{esc(calname)}",
         "X-WR-TIMEZONE:Europe/Istanbul", f"X-WR-CALDESC:{esc(caldesc)}"]
    # sort by UTC start, then matchup
    def key(m):
        u = parse_utc(m["dtu"])
        return (u or datetime.datetime.max.replace(tzinfo=ZoneInfo("UTC")),
                m["ca"] + m["cb"])
    uc = 0
    for m in sorted(matches, key=key):
        u = parse_utc(m["dtu"])
        if not u:
            continue
        na, nb = tr_name(m["na"]), tr_name(m["nb"])
        fa, fb = flag(m["ca"]), flag(m["cb"])
        grp = m["group"] or "?"
        rnd = ROUND_TR.get(m["round"], m["round"] or "")
        played = bool(m.get("finished")) and m["sa"] is not None and m["sb"] is not None
        score = f"  {m['sa']}-{m['sb']}" if played else ""
        summary = f"🏀 {fa} {na} - {fb} {nb} · Grup {grp}{score}"
        dp = [caldesc]
        if rnd:
            dp.append(f"Tur: {rnd}")
        dp.append(f"Grup: {grp}")
        dp.append(f"Maç: {fa} {na} - {fb} {nb}{score}" + (" (oynandı)" if played else ""))
        if m["postponed"]:
            dp.append("DİKKAT: Bu maç ertelendi (FIBA)")
        if m["venue"]:
            dp.append(f"Salon: {m['venue']}")
        if m["city"]:
            dp.append(f"Şehir: {m['city']}")
        # venue local time + İstanbul time
        if m["tz"]:
            try:
                ldt = u.astimezone(ZoneInfo(m["tz"]))
                dp.append(f"Başlangıç (yerel): {ldt.strftime('%H:%M')} ({m['tz']})")
            except Exception:
                pass
        ist = u.astimezone(IST)
        dp.append(f"Başlangıç (İstanbul): {ist.strftime('%H:%M')}")
        dp.append(f"FIBA: https://www.fiba.basketball/en/games/{m['gameId']}")
        desc = "\\n".join(esc(x) for x in dp)
        uc += 1
        end = u + datetime.timedelta(hours=2, minutes=15)
        L += ["BEGIN:VEVENT", f"UID:fiba2027-{m['gameId']}@selim-nba",
              f"DTSTART:{u.strftime('%Y%m%dT%H%M%SZ')}",
              f"DTEND:{end.strftime('%Y%m%dT%H%M%SZ')}",
              f"SUMMARY:{esc(summary)}", f"DESCRIPTION:{desc}"]
        loc = ", ".join(x for x in [m["venue"], m["city"]] if x)
        if loc:
            L.append(f"LOCATION:{esc(loc)}")
        L += ["STATUS:CONFIRMED", "TRANSP:OPAQUE", "END:VEVENT"]
    L.append("END:VCALENDAR")
    with open(path, "w") as f:
        f.write("\r\n".join(L) + "\r\n")
    return uc

def write_if_better(path, matches, calname, caldesc):
    """Write ICS only when we have real data; never wipe a good file on a bad fetch."""
    if not matches:
        if os.path.exists(path):
            print(f"  ~ kept existing {os.path.basename(path)} (no new matches; preserving last-good file)")
            return 0
    return build_ics(matches, path, calname, caldesc)

def main():
    eq_html = fetch_fiba_html(EQ_SLUG)
    eq = parse_fiba_games(eq_html)
    print(f"  European qualifiers: {len(eq)} games parsed")
    tur_eq = [g for g in eq if g["ca"] == "TUR" or g["cb"] == "TUR"]

    wc_html = fetch_fiba_html(WC_SLUG)
    wc = parse_fiba_games(wc_html)
    print(f"  World Cup: {len(wc)} games parsed")
    tur_wc = [g for g in wc if g["ca"] == "TUR" or g["cb"] == "TUR"]

    # Single Türkiye calendar: qualifiers + World Cup (when fixtures are published).
    turkiye = tur_eq + tur_wc
    if tur_eq or tur_wc:
        n1 = write_if_better(os.path.join(OUTDIR, "turkiye.ics"), turkiye,
                             "FIBA 2027 - Türkiye A Milli Takımı",
                             "FIBA 2027 Türkiye A Milli Takımı maçları: Avrupa Elemeleri + Dünya Kupası (otomatik güncellenir)")
        print(f"  turkiye.ics: {n1} events (elemeler: {len(tur_eq)}, dünya kupası: {len(tur_wc)})")
    else:
        print("  ~ turkiye.ics: both fetches failed; kept last-good file")

    # Bonus: full World Cup tournament calendar (all teams, when published).
    if wc:
        n2 = write_if_better(os.path.join(OUTDIR, "worldcup.ics"), wc,
                             "FIBA 2027 Dünya Kupası",
                             "FIBA Basketbol 2027 Dünya Kupası - tüm turnuva maçları (otomatik güncellenir)")
        print(f"  worldcup.ics: {n2} events")
    else:
        print("  ~ worldcup.ics: no WC fixtures published yet; kept last-good file")

    html = r"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>FIBA 2027 - Türkiye A Milli Takımı Takvimi</title>
<style>
  :root{--red:#E30A17;--ink:#1b1d21;--muted:#6b7177;--line:#e6e8eb;--bg:#f7f5f2}
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--ink);
       font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
  .wrap{max-width:760px;margin:0 auto;padding:28px 20px 64px}
  header h1{font-size:clamp(26px,5vw,38px);margin:8px 0 2px;letter-spacing:-.5px}
  header .flag{font-size:clamp(40px,9vw,64px);line-height:1}
  .sub{color:var(--muted);margin:0 0 4px}
  .toprow{display:flex;align-items:center;justify-content:space-between;gap:12px}
  .hype{font-size:18px;font-weight:600;margin:18px 0 6px}
  .hype small{display:block;font-weight:400;color:var(--muted);font-size:14px;margin-top:4px}
  .next{border:1px solid var(--line);border-left:5px solid var(--red);border-radius:10px;
        padding:16px 18px;margin:18px 0;background:#fff}
  .next .label{font-size:12px;text-transform:uppercase;letter-spacing:1px;color:var(--muted)}
  .next .who{font-size:22px;font-weight:700;margin:6px 0 2px}
  .next .meta{color:var(--muted);font-size:14px}
  .next .cd{font-variant-numeric:tabular-nums;font-weight:700;color:var(--red);margin-top:8px;font-size:18px}
  section{margin:26px 0}
  h2{font-size:14px;text-transform:uppercase;letter-spacing:1px;color:var(--muted);margin:0 0 12px}
  .cal{border:1px solid var(--line);border-radius:10px;background:#fff;padding:14px 16px;margin:12px 0}
  .cal .name{font-weight:700;margin-bottom:2px}
  .cal .desc{color:var(--muted);font-size:14px;margin-bottom:10px}
  .urlrow{display:flex;gap:8px;align-items:center}
  code{flex:1;font:13px/1.4 ui-monospace,SFMono-Regular,Menlo,monospace;background:#f1f0ed;
       border:1px solid var(--line);border-radius:8px;padding:8px 10px;word-break:break-all;white-space:pre-wrap}
  button{border:1px solid var(--line);background:#fff;border-radius:8px;padding:8px 12px;
         cursor:pointer;font-size:14px;white-space:nowrap}
  button:hover{border-color:var(--ink)}
  button.ok{border-color:#2e7d32;color:#2e7d32}
  ol{margin:6px 0 0;padding-left:20px}
  ol li{margin:6px 0}
  .btns{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}
  a.btn{border:1px solid var(--line);background:#fff;border-radius:8px;padding:8px 12px;
        font-size:14px;text-decoration:none;color:var(--ink);white-space:nowrap;cursor:pointer;display:inline-block}
  a.btn:hover{border-color:var(--ink)}
  .credit{margin-top:10px;font-size:13px}
  .credit a{font-weight:600;color:var(--ink);text-decoration:none;border-bottom:1px solid var(--line)}
  .credit a:hover{border-color:var(--red);color:var(--red)}
  .foot{margin-top:34px;padding-top:16px;border-top:1px solid var(--line);color:var(--muted);font-size:13px}
  a{color:var(--red)}
  .share{margin-top:14px;border:1px solid var(--red);background:var(--red);color:#fff;
         border-radius:8px;padding:10px 16px;font-size:15px;font-weight:600;cursor:pointer}
  .share:hover{background:#c00814}
  .share.copied{background:#2e7d32;border-color:#2e7d32}
  @media(max-width:520px){.urlrow{flex-direction:column;align-items:stretch}code{font-size:12px}}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div class="toprow">
      <div class="flag">🇹🇷</div>
      <button class="share" id="shareBtn">Paylaş</button>
    </div>
    <h1>FIBA 2027 — Türkiye A Milli Takımı</h1>
    <p class="sub">Avrupa Elemeleri + Dünya Kupası · takvimden takip</p>
  </header>

  <p class="hype">12 Dev Adam'a giden yolda hiçbir maçı kaçırma. 🇹🇷
    <small>Takvim otomatik güncellenir: fikstür netleştikçe yeni maçlar kendiliğinden eklenir, saatler İstanbul saatine çevrilir.</small>
  </p>

  <div class="next" id="next">
    <div class="label">Sıradaki maç</div>
    <div class="who" id="who">…</div>
    <div class="meta" id="meta"></div>
    <div class="cd" id="cd"></div>
  </div>

  <section>
    <h2>Takvime abone ol</h2>
    <div class="cal">
      <div class="name">🇹🇷 Türkiye — tüm maçlar (elemeler + Dünya Kupası)</div>
      <div class="desc">Sadece Türkiye A Milli Takımı'nın maçları. Tek takvimde birleşik.</div>
      <div class="urlrow">
        <code id="u1"></code>
        <button onclick="copy('u1',this)">Kopyala</button>
      </div>
      <div class="btns">
        <a class="btn" id="g1" target="_blank" rel="noopener">📅 Google Takvim</a>
        <a class="btn" id="a1">🍎 Apple Takvim</a>
        <a class="btn" id="o1" target="_blank" rel="noopener">🟦 Outlook</a>
        <a class="btn" id="d1" download>⬇️ .ics indir</a>
      </div>
    </div>
    <div class="cal">
      <div class="name">🌍 2027 Dünya Kupası — tüm turnuva</div>
      <div class="desc">Tüm takımların turnuva maçları (fikstür yayınlandıkça dolar).</div>
      <div class="urlrow">
        <code id="u2"></code>
        <button onclick="copy('u2',this)">Kopyala</button>
      </div>
      <div class="btns">
        <a class="btn" id="g2" target="_blank" rel="noopener">📅 Google Takvim</a>
        <a class="btn" id="a2">🍎 Apple Takvim</a>
        <a class="btn" id="o2" target="_blank" rel="noopener">🟦 Outlook</a>
        <a class="btn" id="d2" download>⬇️ .ics indir</a>
      </div>
    </div>
  </section>

  <section>
    <h2>Google Calendar — 30 saniyede kurulum</h2>
    <ol>
      <li><a href="https://calendar.google.com" target="_blank" rel="noopener">calendar.google.com</a> → dişli ⚙ → <b>Ayarlar</b></li>
      <li>Sol menü → <b>Takvim ekle</b> → <b>URL'den</b></li>
      <li>Yukarıdaki adresi yapıştır → <b>Takvim ekle</b></li>
      <li>Telefonda aynı Google hesabında senkron görünür. Google abone takvimleri birkaç saatte bir yeniler.</li>
    </ol>
  </section>

  <div class="foot">
    Veri kaynağı: <a href="https://en.wikipedia.org/wiki/2027_FIBA_Basketball_World_Cup_qualification_(Europe)" target="_blank" rel="noopener">Wikipedia / FIBA</a>.
    Her gün GitHub Action ile otomatik yenilenir.
    <a href="https://github.com/selim-nba/fiba2027-calendar" target="_blank" rel="noopener">Kaynak repo</a>.
    <div class="credit">Yapan: <a href="https://www.linkedin.com/in/selimyoruk/" target="_blank" rel="noopener">Selim Yoruk</a> 🇹🇷</div>
  </div>
</div>

<script>
const base = location.origin + location.pathname.replace(/index\.html$/, "");
document.getElementById("u1").textContent = base + "turkiye.ics";
document.getElementById("u2").textContent = base + "worldcup.ics";

function wireCal(n, file){
  const https = base + file;
  const webcal = https.replace(/^https?:\/\//, "webcal://");
  // Google: subscribe via webcal URL (https cid is rejected by Google).
  document.getElementById("g"+n).href = "https://calendar.google.com/calendar/render?cid=" + encodeURIComponent(webcal);
  // Apple Calendar: native webcal:// handler subscribes & auto-updates.
  document.getElementById("a"+n).href = webcal;
  // Outlook (web): add-calendar-from-web deeplink with the https URL. Works in
  // outlook.live.com / Microsoft 365 web when logged in; Outlook desktop also registers webcal://.
  document.getElementById("o"+n).href =
    "https://outlook.live.com/calendar/0/deeplink/addcalendar?path=/calendar/action/addcalendar&url=" + encodeURIComponent(https);
  // Universal fallback: download the .ics (one-time import, does NOT auto-update).
  document.getElementById("d"+n).href = https;
}
wireCal(1, "turkiye.ics");
wireCal(2, "worldcup.ics");

const shareBtn = document.getElementById("shareBtn");
const shareData = {
  title: "FIBA 2027 — Türkiye A Milli Takımı Takvimi",
  text: "2027 Avrupa Elemeleri + Dünya Kupası maçlarını takviminden takip et 🇹🇷",
  url: location.href
};
function shareDone(msg){ shareBtn.textContent = msg; shareBtn.classList.add("copied");
  setTimeout(()=>{ shareBtn.textContent="Paylaş"; shareBtn.classList.remove("copied"); },1800); }
shareBtn.addEventListener("click", async () => {
  if (navigator.share) {
    try { await navigator.share(shareData); } catch (e) { /* user cancelled */ }
  } else {
    try { await navigator.clipboard.writeText(location.href); shareDone("Link kopyalandı ✓"); }
    catch (e) { window.prompt("Bu linki kopyala:", location.href); }
  }
});

function copy(id, btn){
  navigator.clipboard.writeText(document.getElementById(id).textContent).then(()=>{
    btn.textContent="Kopyalandı ✓"; btn.classList.add("ok");
    setTimeout(()=>{btn.textContent="Kopyala"; btn.classList.remove("ok");},1600);
  });
}

// Parse the Türkiye ICS client-side, show next match + live countdown.
function parseIcs(text){
  const evs=[]; const blocks=text.split("BEGIN:VEVENT");
  for(let i=1;i<blocks.length;i++){
    const b=blocks[i].split("END:VEVENT")[0];
    const get=k=>{const m=b.match(new RegExp(k+":([^\r\n]+)"));return m?m[1].trim():"";};
    const sum=get("SUMMARY");
    const dt=get("DTSTART");
    let d=null;
    if(/T\d{6}Z$/.test(dt)) d=new Date(Date.UTC(+dt.slice(0,4),+dt.slice(4,6)-1,+dt.slice(6,8),+dt.slice(9,11),+dt.slice(11,13)));
    else if(/^\d{8}$/.test(dt)) d=new Date(Date.UTC(+dt.slice(0,4),+dt.slice(4,6)-1,+dt.slice(6,8)));
    const locm=b.match(/LOCATION:([^\r\n]+)/); const loc=locm?locm[1].replace(/\\,/g,",").trim():"";
    const descm=b.match(/DESCRIPTION:([^\r\n]+)/); let desc=descm?descm[1]:"";
    desc=desc.replace(/\\n/g," · ").replace(/\\,/g,",").replace(/\\;/g,";");
    evs.push({sum, d, loc, desc});
  }
  return evs;
}
fetch(base+"turkiye.ics").then(r=>r.text()).then(t=>{
  const evs=parseIcs(t);
  const now=Date.now();
  const up=evs.filter(e=>e.d && e.d.getTime()>=now).sort((a,b)=>a.d-b.d);
  const e=up[0];
  if(!e){document.getElementById("who").textContent="Planlanmış maç yok (fikstür bekleniyor)";return;}
  document.getElementById("who").textContent=e.sum.replace("🏀","").trim();
  const when=e.d.toLocaleDateString("tr-TR",{weekday:"long",day:"numeric",month:"long",year:"numeric"});
  const time=e.d.toLocaleTimeString("tr-TR",{hour:"2-digit",minute:"2-digit"});
  document.getElementById("meta").textContent=when+" · "+time+" (İstanbul)"+(e.loc?" · "+e.loc:"");
  const tick=()=>{
    const diff=e.d.getTime()-Date.now();
    if(diff<=0){document.getElementById("cd").textContent="Maç başladı / oynanıyor";return;}
    const d=Math.floor(diff/86400000), h=Math.floor(diff/3600000)%24,
          m=Math.floor(diff/60000)%60, s=Math.floor(diff/1000)%60;
    document.getElementById("cd").textContent=(d>0?d+"g ":"")+String(h).padStart(2,"0")+":"+String(m).padStart(2,"0")+":"+String(s).padStart(2,"0")+" kaldı";
  };
  tick(); setInterval(tick,1000);
}).catch(()=>{document.getElementById("who").textContent="Maç bilgisi yüklenemedi";});
</script>
</body>
</html>"""
    with open(os.path.join(OUTDIR, "index.html"), "w") as f:
        f.write(html)
    print("done.")


if __name__ == "__main__":
    main()
