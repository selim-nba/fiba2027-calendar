#!/usr/bin/env python3
"""Generate ICS calendars for FIBA 2027 World Cup from Wikipedia (auto-updating).
- calendar/turkiye.ics : Türkiye matches in European qualifiers (+ World Cup once Türkiye fixtures known)
- calendar/worldcup.ics: all 2027 FIBA Basketball World Cup tournament matches
Data source: English Wikipedia wikitext via the MediaWiki API.
"""
import json, re, sys, datetime, urllib.request, os
from zoneinfo import ZoneInfo

OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "calendar")
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
def tr(n): return TR.get(n, n)
def tr_matchup(s):
    if " v " in s:
        a, b = s.split(" v ", 1)
        return f"{tr(a.strip())} - {tr(b.strip())}"
    return s
def esc(s): return str(s).replace("\\","\\\\").replace("\n","\\n").replace(",","\\,").replace(";","\\;")

# ---------- parser ----------
def strip_wm(s):
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
            summary = f"🏀 {tr_matchup(m['id'])} · Grup {grp}"
            if played: summary += f"  {m['scoreA']}-{m['scoreB']}"
        dp = [caldesc]
        if rnd: dp.append(f"Tur: {rnd}")
        dp.append(f"Grup: {grp}")
        if not is_ph:
            dp.append(f"Maç: {tr_matchup(m['id'])}" + (f"  {m['scoreA']}-{m['scoreB']} (oynandı)" if played else ""))
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

def main():
    print("Fetching European qualifiers article ...")
    eq = wiki_wikitext("2027 FIBA Basketball World Cup qualification (Europe)")
    eqm = parse_blocks(eq)
    tur = [m for m in eqm if m["id"] and "Turkey" in m["id"]]
    n1 = build_ics(tur, os.path.join(OUTDIR, "turkiye.ics"),
                   "FIBA 2027 Elemeler - Türkiye",
                   "FIBA 2027 Dünya Kupası Avrupa Elemeleri - Türkiye A Milli Takım (otomatik güncellenir)")
    print(f"  turkiye.ics: {n1} events (from {len(eqm)} total qualifier matches)")

    print("Fetching World Cup tournament article ...")
    wc = wiki_wikitext("2027 FIBA Basketball World Cup")
    wcm = parse_blocks(wc)
    n2 = build_ics(wcm, os.path.join(OUTDIR, "worldcup.ics"),
                   "FIBA 2027 Dünya Kupası",
                   "FIBA Basketbol 2027 Dünya Kupası - turnuva maçları (otomatik güncellenir)")
    print(f"  worldcup.ics: {n2} events")

    # combined index for humans
    with open(os.path.join(OUTDIR, "index.html"), "w") as f:
        f.write("<!doctype html><html lang=tr><head><meta charset=utf-8><title>FIBA 2027 Takvim</title></head>"
                "<body style='font:16px system-ui;max-width:680px;margin:2rem auto;line-height:1.6'>"
                "<h1>FIBA 2027 Takvim Aboneliği</h1>"
                "<p>Google Calendar → Dişli → Ayarlar → Takvim ekle → URL ile → aşağıdaki adresi yapıştır.</p>"
                "<p><b>Türkiye (elemeler):</b><br><code id=u1></code></p>"
                "<p><b>Dünya Kupası (turnuva):</b><br><code id=u2></code></p>"
                "<script>var b=location.origin+location.pathname.replace(/index.html$/, '');"
                "document.getElementById('u1').textContent=b+'turkiye.ics';"
                "document.getElementById('u2').textContent=b+'worldcup.ics';</script>"
                "</body></html>")
    print("done.")

if __name__ == "__main__":
    import urllib.parse  # noqa: placed here so it's available to wiki_wikitext
    main()
