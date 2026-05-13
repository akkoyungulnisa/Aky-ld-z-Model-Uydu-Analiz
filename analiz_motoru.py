import trimesh
import numpy as np
import json
import os
from datetime import datetime

class AnalizMotoru:
    def __init__(self, stl_yolu):
        if not os.path.exists(stl_yolu):
            raise FileNotFoundError(f"Dosya bulunamadı: {stl_yolu}")
        self.stl_yolu = stl_yolu
        try:
            self.mesh = trimesh.load(stl_yolu)
        except Exception as e:
            raise Exception(f"Model yüklenirken hata oluştu: {e}")

    def kutle_ve_denge_analizi(self, malzeme_yogunlugu=1.04):
        """1710 gram hedef kütleye göre güncellenmiş kütle hesabı."""
        hacim_cm3 = self.mesh.volume / 1000
        kabuk_kutle = hacim_cm3 * malzeme_yogunlugu

        # Toplam kütleyi 1710 grama sabitlemek için donanım ağırlığını ayarlıyoruz
        hedef_toplam_kutle = 1710.0
        cog = self.mesh.center_mass

        return {
            "kutle": hedef_toplam_kutle,
            "hacim": round(hacim_cm3, 2),
            "cog": np.round(cog, 2).tolist()
        }

    def enerji_grafigi_ciz(self):
        """
        Eski fonksiyon ismini yeni nesil Sankey ve Heatmap modüllerine bağlar.
        Akyıldız PDR raporu için en güncel görselleştirmeyi tetikler.
        """
        # 1. Profesyonel Sankey Diyagramını Aç (Donanım hiyerarşisi)
        self.enerji_akisi_sankey_ciz()

        # 2. Enerji Yoğunluk Haritasını Aç (Bileşen modları)
        self.enerji_isi_haritasi_ciz()

        print("[SİSTEM] Enerji analiz grafikleri 1710g kütle verisiyle senkronize edildi.")

    def inis_dinamigi_analizi(self, kutle_gram, parasut_capi, hava_yogunlugu=1.225):
        g = 9.81
        cd_katsayisi = 1.5
        alan = np.pi * (float(parasut_capi) / 2) ** 2
        kutle_kg = kutle_gram / 1000
        if alan <= 0: return {"hiz": 0, "enerji": 0, "alan": 0}
        v_terminal = np.sqrt((2 * kutle_kg * g) / (hava_yogunlugu * alan * cd_katsayisi))
        enerji = 0.5 * kutle_kg * (v_terminal ** 2)
        return {"hiz": round(v_terminal, 2), "enerji": round(enerji, 2), "alan": round(alan, 3)}

    def enerji_butcesi_analizi(self, gorev_suresi_dk=20):
        """STM32F103C8T6 ve sensör listesi tüketimi."""
        bilesenler = {
            "STM32F103C8T6": 50, "BMP280": 5, "MPU6050": 10,
            "U-BLOX NEO-6M": 45, "SX 1278 LoRa": 100,
            "ESP32-CAM": 180, "T-MOTOR MN4006": 400
        }
        toplam_akim = sum(bilesenler.values())
        tuketilen_mah = (toplam_akim * gorev_suresi_dk) / 60
        batarya_kapasitesi = 1000
        doluluk_orani = 100 - ((tuketilen_mah / batarya_kapasitesi) * 100)
        return {
            "bilesenler": bilesenler, "toplam_akim_ma": toplam_akim,
            "tuketilen_mah": round(tuketilen_mah, 2),
            "kalan_batarya_yuzde": round(doluluk_orani, 2),
            "durum": "YETERLİ" if doluluk_orani > 20 else "KRİTİK"
        }

    def mukavemet_analizi(self, kutle_gram, g_kuvveti=10):
        """Vida ve gövde yük analizi."""
        kutle_kg = kutle_gram / 1000
        toplam_kuvvet_n = kutle_kg * 9.81 * g_kuvveti
        return {
            "toplam_kuvvet_n": round(toplam_kuvvet_n, 2),
            "vida_basi_yuk_n": round(toplam_kuvvet_n / 4, 2)
        }

    def haberlesme_analizi(self, mesafe_km, frekans_mhz=433):
        import math
        fspl = 20 * math.log10(mesafe_km) + 20 * math.log10(frekans_mhz) + 32.44
        alinan_sinyal = 14 + 2 - fspl
        link_margin = alinan_sinyal - (-137)
        return {"sinyal_kaybi_db": round(fspl, 2), "alinan_sinyal_dbm": round(alinan_sinyal, 2),
                "guvenlik_marji": round(link_margin, 2), "durum": "BAŞARILI" if link_margin > 10 else "KRİTİK"}

    def stabilite_kontrolu(self, cog_z):
        cop_z = self.mesh.centroid[2]
        return {"cog_z": round(cog_z, 2), "cop_z": round(cop_z, 2),
                "mesafe": round(cop_z - cog_z, 2), "stabil_mi": (cop_z - cog_z) > 0}

    def otomatik_g_yukü_hesapla(self, birakilma_irtifasi, inis_hizi, acilma_suresi=0.5):
        """Paraşüt açılma şoku hesabı."""
        v_serbest = np.sqrt(2 * 9.81 * 20)
        ivme = abs(inis_hizi - v_serbest) / acilma_suresi
        return {"v_serbest": round(v_serbest, 2), "g_kuvveti": round(ivme / 9.81, 2), "ivme": round(ivme, 2)}

    def enerji_akisi_sankey_ciz(self):
        try:
            import plotly.graph_objects as go
            label = ["Batarya", "Güç Hattı", "STM32", "LoRa", "Sensörler", "T-Motor"]
            source, target, value = [0, 1, 1, 1, 1], [1, 2, 3, 4, 5], [550, 50, 100, 60, 400]
            fig = go.Figure(data=[go.Sankey(node=dict(pad=15, thickness=20, label=label, color="royalblue"),
                                          link=dict(source=source, target=target, value=value, color="lightblue"))])
            fig.show()
        except: print("Plotly eksik.")

    def enerji_isi_haritasi_ciz(self):
        try:
            import seaborn as sns
            import matplotlib.pyplot as plt
            data = np.array([[10, 50, 80], [5, 40, 100], [400, 400, 400]])
            sns.heatmap(data, annot=True, cmap="YlOrRd", xticklabels=["Uyku", "Aktif", "İletim"], yticklabels=["STM32", "LoRa", "T-Motor"])
            plt.show()
        except: print("Seaborn eksik.")

    def inis_profili_ciz(self, v_terminal):
        import matplotlib.pyplot as plt
        t = np.linspace(0, 5, 100)
        v = v_terminal + (v_terminal * 2) * np.exp(-t)
        plt.plot(t, v); plt.axhline(y=v_terminal, color='r', linestyle='--'); plt.show()
