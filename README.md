# NUIT&CO. — Kişisel Cilt Bakımı Asistanı (API)

Bu proje, SmartLead AI ile aynı mimaride (Flask + Groq API) çalışan, NUIT&CO.
markası için elinizdeki ürünlerle en uygun cilt bakım rutinini öneren bir
yapay zeka asistanıdır.

## Klasör Düzeni

```
nuitco_ai/
├── baslat.py                        ← Programı başlatan düğme
├── ayarlar.py                       ← Tüm ayarlar ve şifreler
├── gereksinimler.txt                ← Gerekli paketlerin listesi
├── .env.example                     ← Örnek gizli ayar dosyası (kopyalayıp .env yapın)
├── nuitco_cilt_bakimi.db            ← Veritabanı (ilk çalıştırmada otomatik oluşur)
│
└── uygulama/
    ├── __init__.py                  ← Parçaları birleştiren montaj hattı
    ├── database.py                  ← Veritabanı işlemleri (leadler + ürün kataloğu)
    ├── rotalar.py                   ← Adresleri yöneten trafik polisi
    ├── sablonlar/
    │   ├── index.html               ← Karşılama sayfası (sohbet + form)
    │   └── dashboard.html           ← Yönetim paneli
    └── servisler/
        └── yapay_zeka_servisi.py    ← Groq API bağlantısı (tercüman)
```

## Kurulum

```bash
cd nuitco_ai
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r gereksinimler.txt

cp .env.example .env
# .env dosyasını açıp GROQ_API_KEY değerinizi console.groq.com/keys adresinden
# aldığınız ücretsiz anahtarla doldurun.

python baslat.py
```

Tarayıcıda `http://localhost:5000` → karşılama sayfası (cilt bakımı sohbeti)
`http://localhost:5000/panel` → yönetim paneli (leadler + ürün kataloğu)

## Adres Listesi

| Adres | Ne işe yarar? | Tür |
|---|---|---|
| `/` | Karşılama sayfasını gösterir | Sayfa |
| `/panel` | Yönetim panelini gösterir | Sayfa |
| `/api/sohbet` (POST) | Yapay zekaya soru iletir, rutin önerisi döner | API |
| `/api/adaylar` (POST) | Yeni müşteri adayı (lead) kaydeder | API |
| `/api/adaylar` (GET) | Tüm müşteri adaylarını getirir | API |
| `/api/urunler` (GET) | Mevcut ürün kataloğunu getirir | API |
| `/saglik-durumu` (GET) | Sunucu çalışıyor mu kontrolü | API |

## Ürün Kataloğunu Güncelleme

Asistan **yalnızca** `uygulama/database.py` içindeki `urunler` tablosunda
tanımlı ürünleri önerir. Elinizdeki gerçek ürünleri eklemek için:

1. `uygulama/database.py` dosyasındaki `_ORNEK_KATALOG` listesini kendi
   ürünlerinizle güncelleyin (isim, kategori, cilt tipi, sorun alanı,
   açıklama, kullanım zamanı, fiyat), **veya**
2. Uygulama çalışırken `urun_ekle()` fonksiyonunu kullanarak veritabanına
   yeni ürün ekleyin.

Veritabanı dosyasını silip yeniden başlatırsanız katalog örnek verilerle
yeniden tohumlanır.

## Asistanın Kişiliğini Değiştirme

`ayarlar.py` içindeki `BUSINESS_CONTEXT` metnini değiştirerek asistanın
üslubunu, adını ve davranış kurallarını özelleştirebilirsiniz.

## Güvenlik

`.env` dosyasını **asla** GitHub'a veya herhangi bir yere yüklemeyin.
İçindeki `GROQ_API_KEY` anahtarı size özeldir; sızarsa başkaları sizin
adınıza yapay zeka kullanıp size fatura çıkarabilir. `.gitignore` dosyası
`.env`'i otomatik olarak gizler.

## Canlıya Alma

`gunicorn` ile üretim ortamında çalıştırabilirsiniz:

```bash
gunicorn baslat:uygulama --bind 0.0.0.0:$PORT
```

`.env` dosyasında `FLASK_ORTAMI=uretim` yaparak hata ayrıntılarını gizleyin.
