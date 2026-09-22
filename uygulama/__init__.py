"""
uygulama/__init__.py — Montaj Hattı
-------------------------------------
Bir otomobil fabrikasındaki montaj hattı gibidir. Tek tek parçaları
(ayarlar, veritabanı, sayfalar, yapay zeka) alır, hepsini bir araya
getirir ve çalışan bir bütün üretir. Bu dosyanın ürettiği "araba",
baslat.py'nin çalıştırdığı programdır.
"""

import os
from flask import Flask
from flask_cors import CORS

from ayarlar import ayar_secici


def uygulama_olustur(ayar_adi=None):
    uygulama = Flask(__name__, template_folder='sablonlar', static_folder='sablonlar')

    # 1) Ayarları yükle (geliştirme mi, üretim mi?)
    ayar_adi = ayar_adi or os.environ.get('FLASK_ORTAMI', 'gelistirme')
    secilen_ayar = ayar_secici.get(ayar_adi, ayar_secici['gelistirme'])
    uygulama.config.from_object(secilen_ayar)

    # 2) Dış sitelerin bağlanmasına izin ver (CORS)
    CORS(uygulama, origins=uygulama.config.get('CORS_ALLOWED_ORIGINS', '*'),
         methods=['GET', 'POST', 'OPTIONS'])

    # 3) Veritabanı tablolarını hazırla (yoksa oluştur) ve ürün kataloğunu tohumla
    from uygulama.database import veritabani_baslat, urun_katalogunu_tohumla
    with uygulama.app_context():
        veritabani_baslat(uygulama)
        urun_katalogunu_tohumla(uygulama)

    # 4) Adresleri (rotaları) sisteme tanıt
    from uygulama.rotalar import api_arayuzu, sayfa_arayuzu
    uygulama.register_blueprint(api_arayuzu, url_prefix='/api')
    uygulama.register_blueprint(sayfa_arayuzu)

    return uygulama
