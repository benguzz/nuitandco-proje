"""
uygulama/rotalar.py — Trafik Polisi
--------------------------------------
Gelen her isteğe bakar ve "sen sohbet istiyorsun, yapay zeka
servisine git" ya da "sen kayıt yapmak istiyorsun, arşiv memuruna
git" diye doğru yöne yönlendirir. Kendisi yemek pişirmez (yapay
zeka çalıştırmaz) veya arşivlemez (veritabanı işlemez); sadece
yönlendirir.

Adres Listesi
-------------
/                    → Karşılama sayfasını gösterir        (Sayfa)
/panel               → Yönetim panelini gösterir           (Sayfa)
/api/sohbet          → Yapay zekaya soru iletir             (API)
/api/adaylar (POST)  → Yeni müşteri adayı kaydeder          (API)
/api/adaylar (GET)   → Tüm müşteri adaylarını getirir       (API)
/api/api/urunler (GET)   → Ürün kataloğunu getirir              (API)
/saglik-durumu       → Sunucu çalışıyor mu? kontrolü        (API)
"""

from flask import Blueprint, jsonify, request, render_template

from uygulama.database import (
    musteri_adayi_ekle,
    tum_adaylari_getir,
    tum_urunleri_getir,
)
from uygulama.servisler.yapay_zeka_servisi import yapay_zeka_servisi, YapayZekaServisHatasi

api_arayuzu = Blueprint('api_arayuzu', __name__)
sayfa_arayuzu = Blueprint('sayfa_arayuzu', __name__)


# ---------------------------------------------------------------------
# Sayfalar (Frontend)
# ---------------------------------------------------------------------

@sayfa_arayuzu.route('/')
def karsilama_sayfasi():
    return render_template('index.html')


@sayfa_arayuzu.route('/panel')
def yonetim_paneli():
    return render_template('dashboard.html')


# ---------------------------------------------------------------------
# 11.2 Sohbet Adresi — Nasıl Çalışır?
# ---------------------------------------------------------------------

@api_arayuzu.route('/sohbet', methods=['POST'])
def sohbet_et():
    veri = request.json or {}              # gelen mesajı al
    mesaj = veri.get('mesaj')               # içinden soruyu çıkar
    gecmis = veri.get('gecmis', [])         # önceki konuşmalar

    if not mesaj:                           # mesaj boşsa hata ver
        return jsonify({'basari': False, 'hata': 'Mesaj boş olamaz.'}), 400

    try:
        urun_katalogu = tum_urunleri_getir()
        # Yapay zeka servisine soruyu ve mevcut ürün kataloğunu ilet, yanıtı al
        yanit = yapay_zeka_servisi.yanit_uret(mesaj, gecmis, urun_katalogu)
        return jsonify({'basari': True, 'cevap': yanit})
    except YapayZekaServisHatasi as e:
        # Bir sorun olursa kibar bir hata döndür
        return jsonify({'basari': False, 'hata': str(e)}), 503


# ---------------------------------------------------------------------
# Müşteri Adayları (Leadler)
# ---------------------------------------------------------------------

@api_arayuzu.route('/adaylar', methods=['POST'])
def aday_kaydet():
    veri = request.json or {}
    isim = veri.get('isim')
    telefon = veri.get('telefon')
    eposta = veri.get('eposta')
    cilt_tipi = veri.get('cilt_tipi')
    mesaj = veri.get('mesaj')
    onerilen_rutin = veri.get('onerilen_rutin')

    if not isim or (not telefon and not eposta):
        return jsonify({
            'basari': False,
            'hata': 'İsim ve en az bir iletişim bilgisi (telefon veya e-posta) gereklidir.'
        }), 400

    musteri_adayi_ekle(isim, telefon, eposta, cilt_tipi, mesaj, onerilen_rutin)
    return jsonify({'basari': True, 'mesaj': 'Kaydınız alındı, teşekkürler!'})


@api_arayuzu.route('/adaylar', methods=['GET'])
def aday_listele():
    adaylar = tum_adaylari_getir()
    return jsonify({'basari': True, 'toplam': len(adaylar), 'adaylar': adaylar})


# ---------------------------------------------------------------------
# Ürün Kataloğu
# ---------------------------------------------------------------------

@api_arayuzu.route('/urunler', methods=['GET'])
def urun_listele():
    urunler = tum_urunleri_getir(sadece_stoktakiler=False)
    return jsonify({'basari': True, 'toplam': len(urunler), 'urunler': urunler})


# ---------------------------------------------------------------------
# Sağlık Kontrolü
# ---------------------------------------------------------------------

@sayfa_arayuzu.route('/saglik-durumu', methods=['GET'])
def saglik_durumu():
    return jsonify({'basari': True, 'durum': 'calisiyor'})
