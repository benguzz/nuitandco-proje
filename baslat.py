"""
baslat.py — "Aç" Düğmesi
-------------------------
Bu dosya bir cihazın açma düğmesi gibidir. İçinde karmaşık bir mantık
yoktur; sadece programı uyandırır ve çalıştırır.
"""

from uygulama import uygulama_olustur

# Hazır programı fabrikadan al
uygulama = uygulama_olustur()

if __name__ == '__main__':
    # Sadece "python baslat.py" yazınca çalışır
    uygulama.run(host='0.0.0.0', port=5000, debug=True)
