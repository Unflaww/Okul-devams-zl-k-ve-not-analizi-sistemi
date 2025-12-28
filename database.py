from pymongo import MongoClient

class VeritabaniYonetici:
    def __init__(self):
        try:
            self.client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
            self.db = self.client["OkulSistemi"]
            self.ogrenciler = self.db["Ogrenciler"]
            self.client.server_info()
            self.hazirlik_verisi_ekle()
        except Exception as e:
            print(f"HATA: MongoDB bağlantısı kurulamadı: {e}")

    def hazirlik_verisi_ekle(self):
        self.ogrenciler.update_many({}, {"$unset": {"danisman": ""}})
        if not self.ogrenci_bul("123"):
            self.yeni_ogrenci_kaydet("EROL", "BEKİL", "123")

    def ogrenci_bul(self, numara):
        return self.ogrenciler.find_one({"numara": str(numara)})

    def yeni_ogrenci_kaydet(self, ad, soyad, numara):
        if not self.ogrenci_bul(numara):
            yeni_kayit = {
                "ad": ad.upper(), "soyad": soyad.upper(), "numara": str(numara),
                "dersler": [
                    {"ad": "Yazılım Mimarisi", "vize": 0, "final": 0, "devam": 0},
                    {"ad": "Veri Yapıları", "vize": 0, "final": 0, "devam": 0},
                    {"ad": "Görsel Programlama", "vize": 0, "final": 0, "devam": 0},
                    {"ad": "Web Tasarımı", "vize": 0, "final": 0, "devam": 0},
                    {"ad": "İşletim Sistemleri", "vize": 0, "final": 0, "devam": 0}
                ]
            }
            self.ogrenciler.insert_one(yeni_kayit)
            return True
        return False

    def ogrenci_guncelle(self, numara, yeni_dersler):
        return self.ogrenciler.update_one({"numara": str(numara)}, {"$set": {"dersler": yeni_dersler}})

    def ogrenci_sil(self, numara):
        return self.ogrenciler.delete_one({"numara": str(numara)})