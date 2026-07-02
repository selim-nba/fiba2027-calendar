#!/usr/bin/env python3
"""Generate ICS calendars for FIBA 2027 World Cup from Wikipedia (auto-updating).
- calendar/turkiye.ics : Türkiye matches in European qualifiers (+ World Cup once Türkiye fixtures known)
- calendar/worldcup.ics: all 2027 FIBA Basketball World Cup tournament matches
Data source: English Wikipedia wikitext via the MediaWiki API.
"""
import json, re, sys, datetime, urllib.request, os
from zoneinfo import ZoneInfo

OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")
os.makedirs(OUTDIR, exist_ok=True)
IST = ZoneInfo("Europe/Istanbul")
UA = "Mozilla/5.0 (compatible; fiba2027-calendar-bot/1.0; +https://github.com/selim-nba/fiba2027-calendar)"

def wiki_wikitext(title):
    url = ("https://en.wikipedia.org/w/api.php?action=parse&prop=wikitext"
           "&format=json&redirects=1&page=" + urllib.parse.quote(title))
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=40) as r:
        d = json.load(r)
    if "parse" not in d:
        print(f"  !! no parse for {title}: {list(d)[:4]}", file=sys.stderr)
        return ""
    return d["parse"]["wikitext"]["*"]

# ---------- helpers ----------
MONTHS = {m: i for i, m in enumerate(
    "January February March April May June July August September October November December".split(), 1)}
def parse_date(s):
    m = re.match(r"(\d{1,2})\s+([A-Z][a-z]+)\s+(\d{4})", s)
    return datetime.date(int(m.group(3)), MONTHS[m.group(2)], int(m.group(1))) if m else None

CITY_TZ = {
 'Farum':'Europe/Copenhagen','Tbilisi':'Asia/Tbilisi','Podgorica':'Europe/Podgorica','Belgrade':'Europe/Belgrade',
 'Istanbul':'Europe/Istanbul','Klaipėda':'Europe/Vilnius','Reykjavík':'Atlantic/Reykjavik','Limassol':'Asia/Nicosia',
 'Riga':'Europe/Riga','Vienna':'Europe/Vienna','Tallinn':'Europe/Tallinn','Matosinhos':'Europe/Lisbon',
 'Pitești':'Europe/Bucharest','Athens':'Europe/Athens','Fribourg':'Europe/Zurich','Osijek':'Europe/Zagreb',
 'Gdynia':'Europe/Warsaw','The Hague':'Europe/Amsterdam','Szombathely':'Europe/Budapest','Espoo':'Europe/Helsinki',
 'Koper':'Europe/Ljubljana','Stockholm':'Europe/Stockholm','La Laguna':'Atlantic/Canary','Oviedo':'Europe/Madrid',
 'Madrid':'Europe/Madrid','Thessaloniki':'Europe/Athens','Coimbra':'Europe/Lisbon','Oradea':'Europe/Bucharest',
 'Sarajevo':'Europe/Sarajevo','Tuzla':'Europe/Sarajevo','Kriens':'Europe/Zurich','Zenica':'Europe/Sarajevo',
 'Tortona':'Europe/Rome','London':'Europe/London','Newcastle upon Tyne':'Europe/London','Livorno':'Europe/Rome',
 'Manchester':'Europe/London','Bologna':'Europe/Rome','Neu-Ulm':'Europe/Berlin','Zagreb':'Europe/Zagreb',
 'Bonn':'Europe/Berlin','Bamberg':'Europe/Berlin','Almere':'Europe/Amsterdam','Kraków':'Europe/Warsaw',
 'Rouen':'Europe/Paris','Mons':'Europe/Brussels','Charleroi':'Europe/Brussels','Le Mans':'Europe/Paris',
 'Helsinki':'Europe/Helsinki','Antwerp':'Europe/Brussels','Székesfehérvár':'Europe/Budapest','Pau':'Europe/Paris',
 'Prague':'Europe/Prague','Gothenburg':'Europe/Stockholm','Jihlava':'Europe/Prague','Brno':'Europe/Prague',
 'Ljubljana':'Europe/Ljubljana','Graz':'Europe/Vienna','Doha':'Asia/Qatar','Lusail':'Asia/Qatar',
 'Al Rayyan':'Asia/Qatar','Al Wakrah':'Asia/Qatar','Düsseldorf':'Europe/Berlin','Hamburg':'Europe/Berlin',
 'Berlin':'Europe/Berlin','Munich':'Europe/Berlin','Mannheim':'Europe/Berlin','Frankfurt':'Europe/Berlin',
 'Cologne':'Europe/Berlin','Dortmund':'Europe/Berlin','Halle':'Europe/Berlin','Oldenburg':'Europe/Berlin',
 'Minsk':'Europe/Minsk','Wrocław':'Europe/Warsaw','Łódź':'Europe/Warsaw','Gdańsk':'Europe/Warsaw',
 'Katowice':'Europe/Warsaw','Lublin':'Europe/Warsaw','Bydgoszcz':'Europe/Warsaw','Tbilisi':'Asia/Tbilisi',
 'Yerevan':'Asia/Yerevan','Tbilisi':'Asia/Tbilisi','Tbilisi':'Asia/Tbilisi',
}
TR = {
 'Austria':'Avusturya','Belgium':'Belçika','Bosnia and Herzegovina':'Bosna-Hersek','Croatia':'Hırvatistan',
 'Cyprus':'Kıbrıs','Czech Republic':'Çekya','Denmark':'Danimarka','Estonia':'Estonya','Finland':'Finlandiya',
 'France':'Fransa','Georgia':'Gürcistan','Germany':'Almanya','Great Britain':'Büyük Britanya','Greece':'Yunanistan',
 'Hungary':'Macaristan','Iceland':'İzlanda','Israel':'İsrail','Italy':'İtalya','Latvia':'Letonya',
 'Lithuania':'Litvanya','Montenegro':'Karadağ','Netherlands':'Hollanda','Poland':'Polonya','Portugal':'Portekiz',
 'Romania':'Romanya','Serbia':'Sırbistan','Slovenia':'Slovenya','Spain':'İspanya','Sweden':'İsveç',
 'Switzerland':'İsviçre','Swizerland':'İsviçre','Turkey':'Türkiye','Ukraine':'Ukrayna','Qatar':'Katar',
 'United States':'ABD','USA':'ABD','Argentina':'Arjantin','Australia':'Avustralya','Brazil':'Brezilya',
 'Canada':'Kanada','China':'Çin','Egypt':'Mısır','Iran':'İran','Japan':'Japonya','Mexico':'Meksika',
 'New Zealand':'Yeni Zelanda','Nigeria':'Nijerya','Philippines':'Filipinler','Puerto Rico':'Porto Riko',
 'Senegal':'Senegal','South Sudan':'Güney Sudan','Angola':'Angola','Cape Verde':'Yeşil Burun Adaları',
 'Dominican Republic':'Dominik Cumhuriyeti','Georgia':'Gürcistan','Ivory Coast':'Fildişi Sahili',
 'Jordan':'Ürdün','Lebanon':'Lübnan','Mexico':'Meksika','Montenegro':'Karadağ','South Sudan':'Güney Sudan',
 'Tunisia':'Tunus','Venezuela':'Venezuela','Angola':'Angola',
}

# Country name -> ISO 3166-1 alpha-2 (for flag emoji); English names as found in Wikipedia id fields
NAME_ISO = {
 'Austria':'AT','Belgium':'BE','Bosnia and Herzegovina':'BA','Croatia':'HR','Cyprus':'CY',
 'Czech Republic':'CZ','Denmark':'DK','Estonia':'EE','Finland':'FI','France':'FR','Georgia':'GE',
 'Germany':'DE','Great Britain':'GB','Greece':'GR','Hungary':'HU','Iceland':'IS','Israel':'IL',
 'Italy':'IT','Latvia':'LV','Lithuania':'LT','Montenegro':'ME','Netherlands':'NL','Poland':'PL',
 'Portugal':'PT','Romania':'RO','Serbia':'RS','Slovenia':'SI','Spain':'ES','Sweden':'SE',
 'Switzerland':'CH','Swizerland':'CH','Turkey':'TR','Ukraine':'UA','Qatar':'QA','United States':'US',
 'USA':'US','Argentina':'AR','Australia':'AU','Brazil':'BR','Canada':'CA','China':'CN','Egypt':'EG',
 'Iran':'IR','Japan':'JP','Mexico':'MX','New Zealand':'NZ','Nigeria':'NG','Philippines':'PH',
 'Puerto Rico':'PR','Senegal':'SN','South Sudan':'SS','Angola':'AO','Cape Verde':'CV',
 'Dominican Republic':'DO','Ivory Coast':'CI','Jordan':'JO','Lebanon':'LB','Tunisia':'TN',
 'Venezuela':'VE',
}
def flag(name):
    iso = NAME_ISO.get(name)
    if not iso or len(iso) != 2:
        return ""
    return chr(0x1F1E6 + (ord(iso[0]) - ord('A'))) + chr(0x1F1E6 + (ord(iso[1]) - ord('A')))
def flag_matchup(idstr):
    """Return 'flagA flagB' for an id like 'Turkey v Spain'."""
    if ' v ' not in idstr:
        return ''
    a, b = idstr.split(' v ', 1)
    return flag(a.strip()) + ' ' + flag(b.strip())
def tr(n): return TR.get(n, n)
def tr_matchup(s):
    if " v " in s:
        a, b = s.split(" v ", 1)
        return f"{tr(a.strip())} - {tr(b.strip())}"
    return s
def tr_matchup_flag(idstr):
    if ' v ' not in idstr:
        return idstr
    a, b = idstr.split(' v ', 1); a=a.strip(); b=b.strip()
    return f"{flag(a)} {tr(a)} - {flag(b)} {tr(b)}"

def esc(s): return str(s).replace("\\","\\\\").replace("\n","\\n").replace(",","\\,").replace(";","\\;")

# ---------- parser ----------
def strip_wm(s):
    s = s.replace("\r", " ")  # neutralize CR before any ICS value is assembled
    s = re.sub(r"''+", "", s)
    s = re.sub(r"\[\[([^\]|]*\|)?([^\]]*)\]\]", r"\2", s)
    s = re.sub(r"\{\{refn[^}]*\}\}", "", s)
    s = re.sub(r"\{\{[A-Za-z0-9\- ]*\|", "", s)
    return s.replace("}}", "").strip()

def field(t, key):
    m = re.search(r"\|" + key + r"=(.*)", t)
    if not m: return ""
    return strip_wm(m.group(1).split("\n")[0])

def parse_blocks(wikitext, group_round_prefix=""):
    """Return list of matches from {{basketballbox collapsible|...}} blocks."""
    lines = wikitext.split("\n")
    out = []; cur_group = None; cur_round = None
    i = 0; n = len(lines)
    while i < n:
        ln = lines[i]
        if ln.startswith("===First round") or ln.startswith("===Second round") or ln.startswith("===Group stage") or ln.startswith("===Final round") or ln.startswith("===Knockout"):
            cur_round = ln.strip("= ").strip()
        if re.match(r"^====+Group [A-Z0-9]====+", ln) or re.match(r"^====+Group [A-Z0-9] ", ln):
            mm = re.search(r"Group ([A-Z0-9])", ln); cur_group = mm.group(1) if mm else cur_group
        if "{{basketballbox collapsible" in ln or "{{basketballbox" in ln:
            j = i; buf = []
            while j < n:
                buf.append(lines[j])
                if j > i and "".join(buf).count("}}") >= "".join(buf).count("{{"):
                    break
                j += 1
            t = "\n".join(buf)
            mid = field(t, "id").strip('" ')
            date = field(t, "date"); tm = field(t, "time")
            sa = re.sub(r"[^0-9]", "", field(t, "scoreA")); sb = re.sub(r"[^0-9]", "", field(t, "scoreB"))
            loc = field(t, "location"); arena = field(t, "arena")
            rep = re.search(r"FIBA game\|(\d+)", t)
            out.append({"group": cur_group, "round": cur_round, "id": mid, "date": date, "time": tm,
                        "scoreA": sa, "scoreB": sb, "loc": loc, "arena": arena,
                        "fid": rep.group(1) if rep else ""})
            i = j + 1; continue
        i += 1
    return out

def tz_for(city):
    if not city: return None
    tz = CITY_TZ.get(city)
    if not tz and ", " in city:
        tz = CITY_TZ.get(city.split(",")[0].strip())
    return ZoneInfo(tz) if tz else None

def build_ics(matches, path, calname, caldesc):
    L = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//FIBA 2027 Calendar//TR//",
         "CALSCALE:GREGORIAN", "METHOD:PUBLISH", f"X-WR-CALNAME:{esc(calname)}",
         "X-WR-TIMEZONE:Europe/Istanbul", f"X-WR-CALDESC:{esc(caldesc)}"]
    uc = 0
    for m in matches:
        d = parse_date(m["date"])
        if not d: continue
        is_ph = bool(m["id"]) and bool(re.fullmatch(r"[A-Z][0-9] v [A-Z][0-9]|Group [A-Z][0-9]", m["id"]))
        grp = m["group"] or "?"
        rnd = ""
        if m["round"]:
            if "First" in m["round"]: rnd = "1. Tur"
            elif "Second" in m["round"]: rnd = "2. Tur"
            elif "Group stage" in m["round"]: rnd = "Grup Aşaması"
            elif "Final" in m["round"]: rnd = "Final Aşaması"
            else: rnd = m["round"]
        played = bool(m["scoreA"] and m["scoreB"])
        city = m["loc"]; tz = tz_for(city)
        tm = m["time"]; has_time = bool(re.match(r"\d{1,2}:\d{2}", tm or "")) and tz
        if is_ph:
            summary = f"🏀 FIBA 2027 · {rnd or 'Maç'} · Grup {grp}"
        else:
            summary = f"🏀 {tr_matchup_flag(m['id'])} · Grup {grp}"
            if played: summary += f"  {m['scoreA']}-{m['scoreB']}"
        dp = [caldesc]
        if rnd: dp.append(f"Tur: {rnd}")
        dp.append(f"Grup: {grp}")
        if not is_ph:
            dp.append(f"Maç: {tr_matchup_flag(m['id'])}" + (f"  {m['scoreA']}-{m['scoreB']} (oynandı)" if played else ""))
        if m["arena"]: dp.append(f"Salon: {m['arena']}")
        if city: dp.append(f"Şehir: {city}")
        if has_time:
            ldt = datetime.datetime.combine(d, datetime.time(int(tm.split(":")[0]), int(tm.split(":")[1])), tz)
            dp += [f"Başlangıç (yerel): {tm}", f"Başlangıç (İstanbul): {ldt.astimezone(IST).strftime('%H:%M')}"]
        if m["fid"]: dp.append(f"FIBA: https://www.fiba.basketball/en/games/{m['fid']}")
        desc = "\\n".join(esc(x) for x in dp)
        uc += 1
        L += ["BEGIN:VEVENT", f"UID:fiba2027-{uc}@selim-nba"]
        if has_time:
            u = ldt.astimezone(ZoneInfo("UTC"))
            L += [f"DTSTART:{u.strftime('%Y%m%dT%H%M%SZ')}",
                  f"DTEND:{(u + datetime.timedelta(hours=2, minutes=15)).strftime('%Y%m%dT%H%M%SZ')}"]
        else:
            L += [f"DTSTART;VALUE=DATE:{d.strftime('%Y%m%d')}",
                  f"DTEND;VALUE=DATE:{(d + datetime.timedelta(days=1)).strftime('%Y%m%d')}"]
        loc = ", ".join(x for x in [m["arena"], city] if x)
        L += [f"SUMMARY:{esc(summary)}", f"DESCRIPTION:{desc}"]
        if loc: L.append(f"LOCATION:{esc(loc)}")
        L += ["STATUS:CONFIRMED", "TRANSP:OPAQUE", "END:VEVENT"]
    L.append("END:VCALENDAR")
    with open(path, "w") as f:
        f.write("\r\n".join(L) + "\r\n")
    return uc

def fetch_wt(title, attempts=2):
    """Fetch Wikipedia wikitext with a tiny retry. Returns (ok, text)."""
    last = None
    for a in range(attempts):
        try:
            return True, wiki_wikitext(title)
        except Exception as e:  # network / HTTP / JSON errors
            last = e
            print(f"  !! fetch attempt {a+1} failed for {title!r}: {e}", file=sys.stderr)
    return False, ""

def write_if_better(path, matches, calname, caldesc):
    """Write ICS only when we have real data; never wipe a good file on a bad fetch.

    Policy: overwrite when the new calendar has events, OR when no prior file exists.
    A transient empty/failed result keeps the last known-good file so subscribers
    never lose their calendar because Wikipedia was briefly unavailable.
    """
    if not matches:
        if os.path.exists(path):
            print(f"  ~ kept existing {os.path.basename(path)} (no new matches; preserving last-good file)")
            return 0
        # first run with legitimately 0 events (e.g. WC fixtures not published yet)
    return build_ics(matches, path, calname, caldesc)

def main():
    eq_ok, eq = fetch_wt("2027 FIBA Basketball World Cup qualification (Europe)")
    eqm = parse_blocks(eq) if eq_ok else []
    tur_eq = [m for m in eqm if m["id"] and "Turkey" in m["id"]]

    wc_ok, wc = fetch_wt("2027 FIBA Basketball World Cup")
    wcm = parse_blocks(wc) if wc_ok else []
    tur_wc = [m for m in wcm if m["id"] and "Turkey" in m["id"]]

    # Single Türkiye calendar: qualifiers + World Cup (when fixtures are published).
    # WC is best-effort: a transient WC fetch failure must not drop qualifier matches.
    turkiye = sorted(tur_eq + tur_wc, key=lambda m: (parse_date(m["date"]) or datetime.date.max, m["id"]))
    if eq_ok or tur_wc:
        n1 = write_if_better(os.path.join(OUTDIR, "turkiye.ics"), turkiye,
                             "FIBA 2027 - Türkiye A Milli Takımı",
                             "FIBA 2027 Türkiye A Milli Takımı maçları: Avrupa Elemeleri + Dünya Kupası (otomatik güncellenir)")
        print(f"  turkiye.ics: {n1} events (elemeler: {len(tur_eq)}, dünya kupası: {len(tur_wc)})")
    else:
        print("  ~ turkiye.ics: both fetches failed; kept last-good file")

    # Bonus: full World Cup tournament calendar (all teams)
    if wc_ok:
        n2 = write_if_better(os.path.join(OUTDIR, "worldcup.ics"), wcm,
                             "FIBA 2027 Dünya Kupası",
                             "FIBA Basketbol 2027 Dünya Kupası - tüm turnuva maçları (otomatik güncellenir)")
        print(f"  worldcup.ics: {n2} events")
    else:
        print("  ~ worldcup.ics: fetch failed; kept last-good file")

    # Landing page (static, self-contained; JS reads turkiye.ics to show next match)
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
    <div class="flag">🇹🇷</div>
    <h1>FIBA 2027 — Türkiye A Milli Takımı</h1>
    <p class="sub">Avrupa Elemeleri + Dünya Kupası · takvimden takip</p>
  <button class="share" id="shareBtn">🔗 Arkadaşlarınla paylaş</button>
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
  document.getElementById("g"+n).href = "https://calendar.google.com/calendar?cid=" + encodeURIComponent(https);
  document.getElementById("a"+n).href = webcal;
  document.getElementById("o"+n).href = webcal;
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
    import urllib.parse  # noqa: placed here so it's available to wiki_wikitext
    main()
