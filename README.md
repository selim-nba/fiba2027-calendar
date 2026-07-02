# FIBA 2027 — Türkiye A Milli Takımı Takvim Aboneliği

Wikipedia (FIBA kaynaklı) verisinden **her gün otomatik** üretilen `.ics` takvimler.
GitHub Actions günlük çalışır; fikstür/tarih/saat netleştikçe takvim kendini günceller.
Sen bir kere abone olursun, gerisi otomatik — yeni maçlar ekstra iş olmadan takvimine düşer.

🌐 **Açılış sayfası:** <https://selim-nba.github.io/fiba2027-calendar/>

## Takvimler

| Dosya | İçerik | Abone URL |
|---|---|---|
| `turkiye.ics` | Türkiye A Milli Takımı'nın **tüm** maçları: Avrupa Elemeleri + Dünya Kupası | `webcal://selim-nba.github.io/fiba2027-calendar/turkiye.ics` |
| `worldcup.ics` | 2027 FIBA Dünya Kupası — tüm turnuva maçları | `webcal://selim-nba.github.io/fiba2027-calendar/worldcup.ics` |

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

1. **Veri kaynağı:** İngilizce Wikipedia MediaWiki API'si (FIBA kaynaklı):
   - `2027 FIBA Basketball World Cup qualification (Europe)`
   - `2027 FIBA Basketball World Cup`
2. **Ayrıştırma:** regex ile `{{basketballbox collapsible|...}}` şablonlarından tarih/saat/takım/salon/FIBA-id çıkarılır (LLM/eval yok — saf deterministik kod).
3. **Dönüşüm:** yerel salon saat dilimi → UTC → ICS; Türkçe takım adları + bayrak emojisi eklenir.
4. **Yayın:** `docs/*.ics` GitHub Pages'ten `text/calendar` olarak sunulur.
5. **Zamanlama:** `.github/workflows/update-calendar.yml` her gün (cron) + `main`'e push'ta çalışır.

`turkiye.ics` her iki makaledeki "Turkey" maçlarını birleştirir; 2. tur / Dünya Kupası fikstürü Wikipedia'ya düştüğü gün otomatik eklenir.

## Güvenlik / sağlamlık

- GitHub Action'ları commit SHA'larına sabitlendi (tedarik zinciri). Dependabot güncel tutar (`.github/dependabot.yml`).
- Workflow izinleri minimum (`contents: write`); `pull_request` tetikleyicisi yok; repo'da secret yok.
- Açılış sayfasında XSS sink yok (`innerHTML`/`eval`/`document.write` = 0); ICS değer kaçışı CR dahil sağlamlaştırıldı.
- Fetch hatasında eski ICS silinmez: Wikipedia geçici kapalıysa son iyi dosya korunur, Action kırmızı vermez.

## Yerel çalıştırma

```bash
python3 generate.py        # docs/*.ics + docs/index.html üretir (sadece stdlib)
```

## Kredi

Yapan: [Selim Yoruk](https://www.linkedin.com/in/selimyoruk/) 🇹🇷
Veri kaynağı: [Wikipedia / FIBA](https://en.wikipedia.org/wiki/2027_FIBA_Basketball_World_Cup_qualification_(Europe))
