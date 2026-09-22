"""
uygulama/database.py — Arşiv Memuru
--------------------------------------
Bir arşiv memuru gibidir. Üç temel işi vardır: (1) yeni gelen müşteri
adaylarını arşive kaydetmek, (2) NUIT&CO. ürün kataloğunu saklamak ve
(3) istendiğinde tüm kayıtları geri getirmek. Veritabanıyla ilgili her
işlem yalnızca bu dosyada yapılır.
"""

import sqlite3
from datetime import datetime
from flask import current_app


def baglanti_al():
    yol = current_app.config.get('DATABASE_URL', 'nuitco_cilt_bakimi.db')
    baglanti = sqlite3.connect(yol)
    baglanti.row_factory = sqlite3.Row
    return baglanti


def veritabani_baslat(uygulama):
    """Tablolar yoksa oluşturur. Uygulama açılışında bir kez çağrılır."""
    with uygulama.app_context():
        baglanti = baglanti_al()
        imlec = baglanti.cursor()

        # Müşteri adayları (leadler) — cilt danışmanlığı talep edenler
        imlec.execute('''
            CREATE TABLE IF NOT EXISTS musteri_adaylari (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                isim TEXT NOT NULL,
                telefon TEXT,
                eposta TEXT,
                cilt_tipi TEXT,
                mesaj TEXT,
                onerilen_rutin TEXT,
                olusturulma_tarihi TEXT NOT NULL
            )
        ''')

        # Ürün kataloğu — asistanın önerebileceği TEK doğru kaynak
        imlec.execute('''
            CREATE TABLE IF NOT EXISTS urunler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                isim TEXT NOT NULL,
                kategori TEXT NOT NULL,
                cilt_tipi TEXT NOT NULL,
                sorun_alani TEXT,
                aciklama TEXT,
                kullanim_zamani TEXT,
                fiyat REAL,
                stokta INTEGER DEFAULT 1
            )
        ''')

        baglanti.commit()
        baglanti.close()


# ---------------------------------------------------------------------
# Müşteri Adayları (Leadler)
# ---------------------------------------------------------------------

def musteri_adayi_ekle(isim, telefon, eposta, cilt_tipi, mesaj, onerilen_rutin=None):
    baglanti = baglanti_al()
    imlec = baglanti.cursor()
    imlec.execute(
        '''INSERT INTO musteri_adaylari
           (isim, telefon, eposta, cilt_tipi, mesaj, onerilen_rutin, olusturulma_tarihi)
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (isim, telefon, eposta, cilt_tipi, mesaj, onerilen_rutin,
         datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    )
    baglanti.commit()  # değişikliği kalıcı yap
    baglanti.close()


def tum_adaylari_getir():
    """Tüm müşteri adaylarını en yeniden eskiye sıralı şekilde getirir."""
    baglanti = baglanti_al()
    imlec = baglanti.cursor()
    imlec.execute('SELECT * FROM musteri_adaylari ORDER BY olusturulma_tarihi DESC')
    satirlar = imlec.fetchall()
    baglanti.close()
    return [dict(satir) for satir in satirlar]


# ---------------------------------------------------------------------
# Ürün Kataloğu
# ---------------------------------------------------------------------

def tum_urunleri_getir(sadece_stoktakiler=True):
    baglanti = baglanti_al()
    imlec = baglanti.cursor()
    if sadece_stoktakiler:
        imlec.execute('SELECT * FROM urunler WHERE stokta = 1 ORDER BY kategori, isim')
    else:
        imlec.execute('SELECT * FROM urunler ORDER BY kategori, isim')
    satirlar = imlec.fetchall()
    baglanti.close()
    return [dict(satir) for satir in satirlar]


def urun_ekle(isim, kategori, cilt_tipi, sorun_alani, aciklama, kullanim_zamani, fiyat, stokta=1):
    baglanti = baglanti_al()
    imlec = baglanti.cursor()
    imlec.execute(
        '''INSERT INTO urunler
           (isim, kategori, cilt_tipi, sorun_alani, aciklama, kullanim_zamani, fiyat, stokta)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        (isim, kategori, cilt_tipi, sorun_alani, aciklama, kullanim_zamani, fiyat, stokta)
    )
    baglanti.commit()
    baglanti.close()


# Elinizdeki gerçek ürünler farklıysa bu listeyi güncelleyin —
# asistan yalnızca burada (veya panelde) tanımlı ürünleri önerecektir.
_ORNEK_KATALOG = [
    dict(isim="Nazik Temizleme Jeli", kategori="Temizleyici", cilt_tipi="Tüm cilt tipleri",
         sorun_alani="Günlük temizlik", kullanim_zamani="Sabah, Akşam",
         aciklama="Cildi kurutmadan arındıran, pH dengeli günlük temizleyici jel.", fiyat=349.0),
    dict(isim="Gül Suyu Tonik", kategori="Tonik", cilt_tipi="Kuru, Hassas",
         sorun_alani="Nem dengesi, kızarıklık", kullanim_zamani="Sabah, Akşam",
         aciklama="Cildi yatıştıran, nem dengesini destekleyen alkolsüz tonik.", fiyat=299.0),
    dict(isim="Niasinamid Serum %10", kategori="Serum", cilt_tipi="Yağlı, Karma",
         sorun_alani="Gözenek, akne eğilimi, parlaklık kontrolü", kullanim_zamani="Sabah, Akşam",
         aciklama="Gözenekleri sıkılaştırır, sebum üretimini dengeler.", fiyat=449.0),
    dict(isim="Hyaluronik Asit Yoğun Nem Serumu", kategori="Serum", cilt_tipi="Kuru, Susuz",
         sorun_alani="Nem eksikliği, donukluk", kullanim_zamani="Sabah, Akşam",
         aciklama="Çok katmanlı hyaluronik asit ile yoğun ve kalıcı nemlendirme sağlar.", fiyat=479.0),
    dict(isim="C Vitamini Aydınlatıcı Serum", kategori="Serum", cilt_tipi="Donuk, Lekeli cilt",
         sorun_alani="Leke, ton eşitsizliği, donukluk", kullanim_zamani="Sabah",
         aciklama="Cilt tonunu eşitler, aydınlık ve canlı bir görünüm kazandırır.", fiyat=499.0),
    dict(isim="Retinol Gece Bakım Kremi %0.3", kategori="Gece Kremi", cilt_tipi="Olgunlaşan cilt",
         sorun_alani="İnce çizgi, kırışıklık, yaşlanma karşıtı bakım", kullanim_zamani="Akşam",
         aciklama="Cilt yenilenmesini destekler, ince çizgilerin görünümünü azaltır.", fiyat=599.0),
    dict(isim="Hafif Jel Nemlendirici", kategori="Nemlendirici", cilt_tipi="Yağlı, Karma",
         sorun_alani="Yağlanma, gözenek tıkanıklığı", kullanim_zamani="Sabah, Akşam",
         aciklama="Yağ oranı düşük, hızlı emilen, mat bitişli nemlendirici jel.", fiyat=379.0),
    dict(isim="Zengin Besleyici Krem", kategori="Nemlendirici", cilt_tipi="Kuru",
         sorun_alani="Nem eksikliği, gerginlik hissi", kullanim_zamani="Akşam",
         aciklama="Yoğun kıvamlı, besleyici, bariyer onarımını destekleyen krem.", fiyat=429.0),
    dict(isim="SPF50 Güneş Koruyucu Fluid", kategori="Güneş Koruyucu", cilt_tipi="Tüm cilt tipleri",
         sorun_alani="Güneş koruması, erken yaşlanma önleme", kullanim_zamani="Sabah",
         aciklama="Yağsız, beyaz iz bırakmayan, günlük kullanıma uygun geniş spektrumlu SPF50.", fiyat=399.0),
    dict(isim="Salisilik Asit Nokta Bakım Jeli", kategori="Akne Bakımı", cilt_tipi="Sivilce eğilimli",
         sorun_alani="Aktif sivilce, akne izleri", kullanim_zamani="Akşam",
         aciklama="Sivilce bölgelerine lokal uygulanan, arındırıcı nokta bakım jeli.", fiyat=329.0),
    dict(isim="Onarıcı Gece Maskesi", kategori="Maske", cilt_tipi="Yorgun, stresli cilt",
         sorun_alani="Canlılık kaybı, yorgun cilt görünümü", kullanim_zamani="Haftada 2-3, Akşam",
         aciklama="Uyku boyunca cildi onarır, sabah dinç ve parlak bir görünüm bırakır.", fiyat=459.0),
    dict(isim="Göz Çevresi Bakım Kremi", kategori="Göz Bakımı", cilt_tipi="Tüm cilt tipleri",
         sorun_alani="İnce çizgi, şişkinlik, koyu halka", kullanim_zamani="Sabah, Akşam",
         aciklama="Göz çevresindeki hassas bölgeyi nemlendirir, şişkinlik görünümünü azaltır.", fiyat=389.0),
]


def urun_katalogunu_tohumla(uygulama):
    """Ürün tablosu boşsa örnek NUIT&CO. kataloğuyla doldurur.
    Gerçek ürünlerinizi eklemek için urun_ekle() fonksiyonunu kullanın
    ya da bu dosyadaki _ORNEK_KATALOG listesini güncelleyin."""
    with uygulama.app_context():
        baglanti = baglanti_al()
        imlec = baglanti.cursor()
        imlec.execute('SELECT COUNT(*) AS adet FROM urunler')
        adet = imlec.fetchone()['adet']
        baglanti.close()

        if adet == 0:
            for urun in _ORNEK_KATALOG:
                urun_ekle(**urun)
