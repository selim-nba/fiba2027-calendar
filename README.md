# FIBA 2027 — Türkiye A Milli Takımı Takvim Aboneliği

FIBA'nın otoriter fikstür verisinden **her gün otomatik** üretilen `.ics` takvimler.
GitHub Actions günlük çalışır; fikstür/tarih/saat netleştikçe takvim kendini günceller.
Sen bir kere abone olursun, gerisi otomatik — yeni maçlar ekstra iş olmadan takvimine düşer.

🌐 **Açılış sayfası:** <https://selim-nba.github.io/fiba2027-calendar/>

## Takvimler

| Dosya | İçerik | Abone URL |
|---|---|---|
| `turkiye.ics` | Türkiye A Milli Takımı'nın **tüm** maçları: Avrupa Elemeleri + Dünya Kupası | `webcal://selim-nba.github.io/fiba2027-calendar/turkiye.ics` |
| `worldcup.ics` | 2027 FIBA Dünya Kupası — tüm turnuva maçları | `webcal://selim-nba.github.io/fiba2027-calendar/worldcup.ics` |
| `turkiye-u17.ics` | Türkiye **U17** Milli Takımı — 2026 FIBA U17 Dünya Kupası (İstanbul) maçları | `webcal://selim-nba.github.io/fiba2027-calendar/turkiye-u17.ics` |

Açılış sayfasında tek tıkla ekleme butonları var: 📅 Google · 🍎 Apple Takvim · 🟦 Outlook · ⬇️ .ics indir,
artıca en üstte 📤 **Paylaş** ve sayfada **sıradaki maç + canlı geri sayım** widget'ı.

## Abone ol

**Tek tık (önerilen):** açılış sayfasındaki butonlar.

**Elle:**
- **Google Calendar:** Ayarlar → Takvim ekle → URL'den → `webcal://selim-nba.github.io/fiba2027-calendar/turkiye.ics`
- **Apple Takvim:** yukarıdaki `webcal://` linkine tıkla (Takvim uygulaması abone eder).
- **Outlook:** Takvim ekle → Web'den abone ol → `https://selim-nba.github.io/fiba2027-calendar/turkiye.ics`

> Abonelik (URL) kullandığında takvim otomatik güncellenir. `.ics indir` ise tek seferlik import'tur (güncellemez).

## Nasıl çalışıyor

1. **Veri kaynağı:** FIBA resmî oyunlar sayfasındaki gömülü oyunlar JSON'u (otoriter tarih/saat/salon):
   - Avrupa Elemeleri: `fiba-basketball-world-cup-2027-european-qualifiers`
   - Dünya Kupası: `fiba-basketball-world-cup-2027` (fikstür yayınlandığında otomatik devreye girer)
2. **Ayrıştırma:** regex ile oyun başına `gameId`/`teamA`/`teamB`/`gameDateTimeUTC`/`ianaTimeZone`/`round`/`group` çıkarılır (LLM/eval yok — saf deterministik kod).
3. **Dönüşüm:** `gameDateTimeUTC` doğrudan `DTSTART` (UTC), `ianaTimeZone` ile yerel + İstanbul saat gösterimi; Türkçe takım adları + bayrak emojisi eklenir.
4. **Yayın:** `docs/*.ics` GitHub Pages'ten `text/calendar` olarak sunulur.
5. **Zamanlama:** `.github/workflows/update-calendar.yml` her gün (cron) + `main`'e push'ta çalışır.

`turkiye.ics`, FIBA'daki tüm Türkiye maçlarını birleştirir (Avrupa Elemeleri + Dünya Kupası fikstürü yayınlandığında otomatik eklenir). Eski Wikipedia kaynağındaki tarih hataları (ör. Türkiye-İsviçre 5 Tem Pazar → 6 Tem Pazartesi) FIBA otoriter verisiyle düzeltildi.

## Güvenlik / sağlamlık

- GitHub Action'ları commit SHA'larına sabitlendi (tedarik zinciri). Dependabot güncel tutar (`.github/dependabot.yml`).
- Workflow izinleri minimum (`contents: write`); `pull_request` tetikleyicisi yok; repo'da secret yok.
- Açılış sayfasında XSS sink yok (`innerHTML`/`eval`/`document.write` = 0); ICS değer kaçışı CR dahil sağlamlaştırıldı.
- Fetch hatasında eski ICS silinmez: FIBA geçici erişilemezse son iyi dosya korunur, Action kırmızı vermez.

## Yerel çalıştırma

```bash
python3 generate.py        # docs/*.ics + docs/index.html üretir (sadece stdlib)
```

## Kredi

Yapan: [Selim Yoruk](https://www.linkedin.com/in/selimyoruk/) 🇹🇷
Veri kaynağı: [FIBA Basketball World Cup 2027 European Qualifiers](https://www.fiba.basketball/en/events/fiba-basketball-world-cup-2027-european-qualifiers/games)
