# FIBA 2027 Takvim Aboneliği

Wikipedia (FIBA kaynaklı) verisinden her gün otomatik üretilen `.ics` takvimler.
GitHub Actions günlük çalışır, maçlar/tarihler netleştikçe takvim kendini günceller —
sen bir şey yapmazsın, abone olduğun takvim Google Calendar'da otomatik yenilenir.

## Takvimler

| Takvim | İçerik |
|---|---|
| `turkiye.ics` | Türkiye A Milli Takımı'nın **tüm** maçları: Avrupa Elemeleri + Dünya Kupası (fikstür yayınlandıkça) |
| `worldcup.ics` | 2027 FIBA Dünya Kupası turnuva maçları (fikstür yayınlandıkça dolar) |

## Google Calendar'a abone ol

1. calendar.google.com → Dişli ⚙ → Ayarlar → **Takvim ekle** → **URL'den**
2. Aşağıdaki adresten birini yapıştır:

```
https://selim-nba.github.io/fiba2027-calendar/turkiye.ics
https://selim-nba.github.io/fiba2027-calendar/worldcup.ics
```

> Google abone takvimleri birkaç saatte bir yeniler. Daha hızlı istersen tek tek
> "Senkronize et" diyebilirsin; veya telefon uygulamasında yenile.

## Notlar

- Saatler maçın oynandığı salonun yerel saatine göre UTC'ye çevrilir; takvimde
  İstanbul saatinde gösterilir (yaz/kış saati otomatik).
- Elemeler 2. tur maçları (Türkiye gruptan çıkarsa) ve Dünya Kupası fikstürü
  henüz belli değil; Wikipedia'ya düştükçe Action otomatik ekler.
- Tek seferlik static import yerine **abonelik (URL)** kullandığımız için sonradan
  belli olacak maçlar ekstra iş olmadan takvimde görünür.

## Yerel çalıştırma

```bash
python3 generate.py      # calendar/*.ics üretir
```
