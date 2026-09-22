"""
uygulama/servisler/yapay_zeka_servisi.py — Tercüman
------------------------------------------------------
Bir tercüman gibidir. Ziyaretçinin sorusunu (ve elimizdeki ürün
kataloğunu) alır, Groq'un anlayacağı dile çevirir, Groq'a gönderir,
gelen yanıtı geri getirir. Bu projede TEK yapay zeka sağlayıcısı
kullanılır: Groq.
"""

from flask import current_app

try:
    from groq import Groq
except ImportError:  # groq paketi kurulu değilse demo modu yine çalışsın
    Groq = None


class YapayZekaServisHatasi(Exception):
    """Yapay zeka servisine ulaşılamadığında fırlatılan hata."""
    pass


class YapayZekaServisi:

    # -------------------------------------------------------------
    # 12.1 Akıllı Seçim — yanit_uret()
    # -------------------------------------------------------------
    def yanit_uret(self, kullanici_mesaji, sohbet_gecmisi=None, urun_katalogu=None):
        """Ziyaretçinin mesajını alır, Groq'a iletir, yanıtı döndürür.
        API anahtarı tanımlı değilse programı çökertmek yerine demo
        moduna geçer."""
        api_anahtari = current_app.config.get('GROQ_API_KEY', '')

        if not api_anahtari or Groq is None:
            return self._demo_yaniti_ver(kullanici_mesaji)

        try:
            return self._groq_cagir(kullanici_mesaji, sohbet_gecmisi or [], urun_katalogu or [])
        except Exception as hata:
            raise YapayZekaServisHatasi(f"Groq servisine ulaşılamadı: {hata}")

    # -------------------------------------------------------------
    # Sistem talimatını oluştur — asistanın kişiliği + ürün kataloğu
    # -------------------------------------------------------------
    def _sistem_talimati_olustur(self, urun_katalogu):
        business_context = current_app.config.get('BUSINESS_CONTEXT', '')

        if urun_katalogu:
            katalog_metni = "\n".join(
                f"- {u['isim']} | Kategori: {u['kategori']} | Uygun cilt tipi: {u['cilt_tipi']} "
                f"| Hedef sorun: {u.get('sorun_alani') or '-'} | Kullanım zamanı: "
                f"{u.get('kullanim_zamani') or '-'} | Açıklama: {u.get('aciklama') or '-'} "
                f"| Fiyat: {u.get('fiyat', '-')} TL"
                for u in urun_katalogu
            )
        else:
            katalog_metni = "(Ürün kataloğu şu anda boş — genel, ürün önermeyen bakım tavsiyeleri ver.)"

        return (
            f"{business_context}\n\n"
            "=== NUIT&CO. MEVCUT ÜRÜN KATALOĞU (SADECE BUNLARI ÖNER) ===\n"
            f"{katalog_metni}\n"
            "=== KATALOG SONU ===\n\n"
            "Kurallar:\n"
            "1) Rutin önerirken sadece yukarıdaki katalogdaki ürün isimlerini kullan.\n"
            "2) Cevabını kısa ve okunabilir tut; gerektiğinde sabah/akşam adımlarını "
            "madde madde listele.\n"
            "3) Ziyaretçinin cilt tipini veya derdini bilmiyorsan önce kısaca sor.\n"
            "4) Rutini verdikten sonra, kişiye özel danışmanlık için iletişim "
            "bilgilerini bırakmasını nazikçe öner."
        )

    # -------------------------------------------------------------
    # 12.2 Yapay Zekânın İçindeki Yetenekler (Metodlar)
    # -------------------------------------------------------------
    def _groq_cagir(self, kullanici_mesaji, sohbet_gecmisi, urun_katalogu):
        istemci = Groq(api_key=current_app.config.get('GROQ_API_KEY'))
        model = current_app.config.get('GROQ_MODEL', 'llama-3.3-70b-versatile')

        mesajlar = [{"role": "system", "content": self._sistem_talimati_olustur(urun_katalogu)}]

        # Önceki konuşma geçmişini ekle (varsa)
        for tur in sohbet_gecmisi[-10:]:
            rol = tur.get('rol') or tur.get('role')
            icerik = tur.get('icerik') or tur.get('content')
            if rol in ('user', 'assistant') and icerik:
                mesajlar.append({"role": rol, "content": icerik})

        mesajlar.append({"role": "user", "content": kullanici_mesaji})

        tamamlama = istemci.chat.completions.create(
            model=model,
            messages=mesajlar,
            temperature=0.6,
            max_tokens=700,
        )
        return tamamlama.choices[0].message.content.strip()

    # -------------------------------------------------------------
    # 12.3 Anahtar Yoksa Ne Olur? — Demo Modu
    # -------------------------------------------------------------
    def _demo_yaniti_ver(self, kullanici_mesaji):
        return (
            "Sistem demo modunda çalışıyor, lütfen .env dosyanızdaki GROQ_API_KEY "
            "değerini kontrol edin. (Örnek yanıt) Merhaba! Ben NUIT Asistan 🌿 Cilt "
            f"tipinizi ve en çok dert ettiğiniz konuyu (kuruluk, akne, leke, kırışıklık "
            f"gibi) öğrenirsem, elimizdeki NUIT&CO. ürünleriyle size özel bir sabah/akşam "
            f"rutini hazırlayabilirim. Sorunuz: \"{kullanici_mesaji}\""
        )


# Dışarıdan tek bir örnek üzerinden kullanılır
yapay_zeka_servisi = YapayZekaServisi()
