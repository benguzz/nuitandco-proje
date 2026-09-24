"""
ayarlar.py — Kontrol Paneli
----------------------------
Bir cihazın ayarlar menüsü gibidir. Şifreler, hangi yapay zekânın
kullanılacağı, veritabanı dosyasının adı gibi tüm ayarlar tek bir
yerde toplanır. Bir şeyi değiştirmek istediğinizde kodun içinde
kaybolmadan buradan ayarlarsınız.
"""

import os
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS # Bunu en üste ekle

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}}) # Bunu app = Flask() satırının hemen altına ekle

load_dotenv()  # .env dosyasındaki gizli ayarları oku


class Ayarlar:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'varsayilan-sifre-degistirin')
    DATABASE_URL = os.environ.get('DATABASE_URL', 'nuitco_cilt_bakimi.db')

    # --- Yapay Zeka Bağlantısı (Groq) ---
    AI_PROVIDER = os.environ.get('AI_PROVIDER', 'groq')
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
    GROQ_MODEL = os.environ.get('GROQ_MODEL', 'openai/gpt-oss-120b')

    CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', '*')

    # --- BUSINESS_CONTEXT — Yapay Zekânın Kişiliği ---
    # Bu ayar, yapay zekâya "sen kimsin, nasıl davranmalısın" talimatını verir.
    # Bu metni değiştirerek asistanın tüm davranışını şekillendirebilirsiniz.
    BUSINESS_CONTEXT = os.environ.get(
        'BUSINESS_CONTEXT',
        "Sen NUIT&CO. markasının kişisel cilt bakımı asistanısın. Adın 'NUIT Asistan'. "
        "Görevin, ziyaretçinin cilt tipini, cilt sorunlarını (akne, kuruluk, leke, "
        "kırışıklık, hassasiyet vb.) ve beklentilerini nazikçe sorup, SADECE sana "
        "verilen ürün kataloğundaki mevcut NUIT&CO. ürünleriyle kişiye özel bir cilt "
        "bakım rutini (sabah/akşam adımları) oluşturmaktır. Kataloğda olmayan hiçbir "
        "ürün önerme veya uydurma. Sıcak, samimi, güven veren ama profesyonel bir "
        "dille Türkçe konuş. Tıbbi teşhis koymazsın; ciddi cilt rahatsızıklıklarında "
        "bir dermatoloğa danışmalarını nazikçe hatırlatırsın. Rutini önerdikten sonra "
        "ziyaretçiyi kişiselleştirilmiş ücretsiz cilt bakım danışmanlığı için iletişim "
        "bilgilerini bırakmaya yönlendir."
    )


class GelistirmeAyarlari(Ayarlar):
    DEBUG = True


class UretimAyarlari(Ayarlar):
    DEBUG = False


ayar_secici = {
    'gelistirme': GelistirmeAyarlari,
    'uretim': UretimAyarlari,
}
