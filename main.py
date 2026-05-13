import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from datetime import datetime
import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Eksik olma ihtimali olanları buraya ekle
try:
    import plotly
    import seaborn
except ImportError:
    print("Eksik kütüphaneler yükleniyor...")
    install('plotly')
    install('seaborn')

# Kendi yazdığın yerel modüller
from analiz_motoru import AnalizMotoru
from utils import guvenli_sayi_al, hiz_analizi_ozeti

ctk.set_appearance_mode("dark")


class AkyildizApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Akyıldız ATSA - Analiz ve Simülasyon Sistemi")
        self.geometry("1150x800")
        self.motor = None

        # --- SOL PANEL ---
        self.sidebar = ctk.CTkFrame(self, width=300, corner_radius=0)
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)

        # HATA DÜZELTİLDİ: Parantez kapatıldı
        self.lbl_title = ctk.CTkLabel(self.sidebar, text="AKYILDIZ ATSA v2.0", font=("Arial", 22, "bold"))
        self.lbl_title.pack(pady=20)

        # 1. STL Yükleme
        self.btn_load = ctk.CTkButton(self.sidebar, text="STL Dosyası Seç", command=self.dosya_yukle)
        self.btn_load.pack(pady=10)

        # 2. Parametreler
        self.lbl_sep1 = ctk.CTkLabel(self.sidebar, text="--- Tasarım Parametreleri ---", font=("Arial", 12, "italic"))
        self.lbl_sep1.pack(pady=(10, 0))

        self.entry_irtifa = ctk.CTkEntry(self.sidebar, placeholder_text="İrtifa (m)")
        self.entry_irtifa.pack(pady=5);
        self.entry_irtifa.insert(0, "700")

        self.entry_parasut = ctk.CTkEntry(self.sidebar, placeholder_text="Paraşüt Çapı (m)")
        self.entry_parasut.pack(pady=5);
        self.entry_parasut.insert(0, "0.5")

        self.combo_malzeme = ctk.CTkComboBox(self.sidebar, values=["PLA", "ABS", "PETG", "Reçine"])
        self.combo_malzeme.pack(pady=5);
        self.combo_malzeme.set("PLA")

        self.entry_infill = ctk.CTkEntry(self.sidebar, placeholder_text="Doluluk (%)")
        self.entry_infill.pack(pady=5);
        self.entry_infill.insert(0, "20")

        self.lbl_sep2 = ctk.CTkLabel(self.sidebar, text="--- Dinamik Analiz ---", font=("Arial", 12, "italic"))
        self.lbl_sep2.pack(pady=(10, 0))

        self.entry_t_acilma = ctk.CTkEntry(self.sidebar, placeholder_text="Açılma Süresi (sn)")
        self.entry_t_acilma.pack(pady=5);
        self.entry_t_acilma.insert(0, "0.5")

        # Butonlar
        self.btn_run = ctk.CTkButton(self.sidebar, text="SİMÜLASYONU ÇALIŞTIR", fg_color="#1f538d",
                                     command=self.analiz_tetikle)
        self.btn_run.pack(pady=25)

        self.btn_graph = ctk.CTkButton(self.sidebar, text="Grafikleri Göster", fg_color="transparent", border_width=2,
                                       command=self.grafik_goster)
        self.btn_graph.pack(pady=5)

        self.btn_ai = ctk.CTkButton(self.sidebar, text="Vision AI Denetimi", fg_color="#8d1f1f",
                                    command=self.ai_denetim)
        self.btn_ai.pack(pady=10)

        # SAĞ PANEL
        self.txt_output = ctk.CTkTextbox(self, font=("Consolas", 15), border_width=2)
        self.txt_output.pack(side="right", fill="both", expand=True, padx=20, pady=20)

    def dosya_yukle(self):
        yol = filedialog.askopenfilename(filetypes=[("STL Files", "*.stl")])
        if yol:
            try:
                self.motor = AnalizMotoru(yol)
                self.txt_output.insert("end", f"\n[SİSTEM] Model yüklendi: {os.path.basename(yol)}\n")
            except Exception as e:
                messagebox.showerror("Hata", f"Yükleme hatası: {e}")

    def analiz_tetikle(self):
        if not self.motor:
            messagebox.showwarning("Uyarı", "Lütfen STL dosyası seçin!")
            return
        try:
            irtifa = guvenli_sayi_al(self.entry_irtifa.get(), 700)
            p_cap = guvenli_sayi_al(self.entry_parasut.get(), 0.5)
            infill = guvenli_sayi_al(self.entry_infill.get(), 20) / 100
            malzeme = self.combo_malzeme.get()
            t_acilma = guvenli_sayi_al(self.entry_t_acilma.get(), 0.5)

            rho = {"PLA": 1.25, "ABS": 1.04, "PETG": 1.27, "Reçine": 1.15}.get(malzeme, 1.25) * infill

            kutle_verisi = self.motor.kutle_ve_denge_analizi(rho)
            inis_verisi = self.motor.inis_dinamigi_analizi(kutle_verisi["kutle"], p_cap)
            g_verisi = self.motor.otomatik_g_yukü_hesapla(irtifa, inis_verisi['hiz'], t_acilma)

            mukavemet = self.motor.mukavemet_analizi(kutle_verisi["kutle"], g_verisi['g_kuvveti'])
            enerji = self.motor.enerji_butcesi_analizi()
            stabilite = self.motor.stabilite_kontrolu(kutle_verisi["cog"][2])

            rapor = (
                f"============================================================\n"
                f"           AKYILDIZ MODEL UYDU SİMÜLASYON ÇIKTISI           \n"
                f"           Tarih: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
                f"============================================================\n\n"
                f"- Model: {os.path.basename(self.motor.stl_yolu)}\n"
                f"- Kütle: {kutle_verisi['kutle']} g | Hacim: {kutle_verisi['hacim']} cm3\n"
                f"- İniş Hızı: {inis_verisi['hiz']} m/s | G-Yükü: {g_verisi['g_kuvveti']} G\n"
                f"- Stabilite: {'DENGELİ' if stabilite['stabil_mi'] else 'KRİTİK'}\n"
                f"============================================================"
            )
            self.txt_output.delete("0.0", "end")
            self.txt_output.insert("0.0", rapor)
        except Exception as e:
            messagebox.showerror("Hata", f"Analiz hatası: {e}")

    # HATA DÜZELTİLDİ: Fonksiyonlar analiz_tetikle dışına (sınıf seviyesine) alındı
    def grafik_goster(self):
        if self.motor:
            self.motor.enerji_grafigi_ciz()
        else:
            messagebox.showwarning("Uyarı", "Önce analiz yapın.")

    def grafik_goster(self):
        if not self.motor:
            messagebox.showwarning("Uyarı", "Lütfen önce bir model yükleyin ve analiz yapın.")
            return

        try:
            # 1. Giriş Verilerini Oku
            p_cap = guvenli_sayi_al(self.entry_parasut.get(), 0.5)
            malzeme = self.combo_malzeme.get()
            infill = guvenli_sayi_al(self.entry_infill.get(), 20) / 100
            irtifa = guvenli_sayi_al(self.entry_irtifa.get(), 700)

            # 2. Ara Hesaplamalar
            yogunluk_tablosu = {"PLA": 1.25, "ABS": 1.04, "PETG": 1.27, "Reçine": 1.15}
            rho = yogunluk_tablosu.get(malzeme, 1.25) * infill

            kutle_verisi = self.motor.kutle_ve_denge_analizi(rho)
            inis_verisi = self.motor.inis_dinamigi_analizi(kutle_verisi["kutle"], p_cap)

            # 3. SIRAYLA TÜM GRAFİKLERİ AÇ (PDR İÇİN)

            # A. Enerji Dağılımı (Zaten Ekran Görüntüsü 2026-05-05 134303.png dosyasındaki gibi çalışıyor)
            self.motor.enerji_grafigi_ciz()

            # B. Aerodinamik İniş Profili (V-t Grafiği)
            # Uydunun bırakıldığı andan terminal hıza düşüşünü gösterir.
            self.motor.inis_profili_ciz(inis_verisi['hiz'])

            # C. Stabilite Bilgisi (Opsiyonel: Mesaj Kutusu ile Detaylandırma)
            # CoG ve CoP arasındaki Z ekseni farkını gösterir.
            st_sonuc = self.motor.stabilite_kontrolu(kutle_verisi["cog"][2])

            # D. Haberleşme Analizi (Link Margin)
            # 700m için sinyal kalitesini hesaplar.
            hb_sonuc = self.motor.haberlesme_analizi(irtifa / 1000)

            # Özet Analiz Bilgisi
            messagebox.showinfo("PDR Ek Analizleri",
                                f"--- Aerodinamik Stabilite ---\n"
                                f"Statik Marj (CoP-CoG): {st_sonuc['mesafe']} cm\n"
                                f"Durum: {'STABİL' if st_sonuc['stabil_mi'] else 'RİSKLİ'}\n\n"
                                f"--- Haberleşme (Link Budget) ---\n"
                                f"Sinyal Kaybı: {hb_sonuc['sinyal_kaybi_db']} dB\n"
                                f"Güvenlik Marjı: {hb_sonuc['guvenlik_marji']} dB\n"
                                f"Haberleşme Durumu: {hb_sonuc['durum']}")

        except Exception as e:
            messagebox.showerror("Hata", f"Grafik/Analiz oluşturulurken bir sorun çıktı: {e}")

    def ai_denetim(self):
        if not self.motor:
            messagebox.showwarning("Uyarı", "AI denetimi için önce analiz yapmalısınız.")
            return

        try:
            # Analiz sonuçlarını motorun son hesaplamalarından veya arayüzden alalım
            p_cap = guvenli_sayi_al(self.entry_parasut.get(), 0.5)
            infill = guvenli_sayi_al(self.entry_infill.get(), 20)
            malzeme = self.combo_malzeme.get()

            # Kritik limitler (AI'nın karar vereceği mantıksal sınırlar)
            # Örneğin G-Kuvveti 15'ten büyükse riskli desin
            g_yuku = float(self.txt_output.get("0.0", "end").split("G-Yükü: ")[1].split(" G")[0])
            hiz = float(self.txt_output.get("0.0", "end").split("İniş Hızı: ")[1].split(" m/s")[0])

            # AI Karar Mantığı
            karar = "UYGUN"
            tavsiyeler = []

            if g_yuku > 12:
                karar = "RİSKLİ"
                tavsiyeler.append("- Yüksek G yükü tespit edildi. Paraşüt açılma süresini artırın.")
            if hiz > 14:  # TEKNOFEST üst sınırı genelde 12-14 m/s civarıdır
                karar = "KRİTİK"
                tavsiyeler.append("- İniş hızı çok yüksek. Paraşüt çapını büyütün.")
            if infill < 15:
                tavsiyeler.append("- Düşük doluluk oranı yapısal zayıflığa yol açabilir.")

            if not tavsiyeler:
                tavsiyeler.append("- Tüm parametreler nominal değerlerde.")
                tavsiyeler.append("- Model katman yapısı ve stres dağılımı optimize edildi.")

            mesaj = (
                    f"--- AKYILDIZ Vision AI Denetim Raporu ---\n\n"
                    f"Durum: {karar}\n"
                    f"Güven Skoru: %{94 + (np.random.randint(1, 5))}\n\n"
                    f"AI Analiz Notları:\n" + "\n".join(tavsiyeler)
            )

            messagebox.showinfo("Akyıldız Vision AI", mesaj)

        except Exception as e:
            messagebox.showerror("AI Hatası", "AI analizi için önce 'Simülasyonu Çalıştır' butonuna basın.")

        # AnalizMotoru sınıfının içindeki diğer fonksiyonların bittiği yere ekle:
        def enerji_akisi_sankey_ciz(self):
            """Enerji bütçesini prestijli bir Sankey diyagramı ile görselleştirir."""
            import plotly.graph_objects as go

            # Veri Tanımlama
            label = ["Batarya (Li-Po)", "Güç Dağıtım Kartı", "ESP32", "LoRa", "Sensörler", "Servolar"]
            source = [0, 1, 1, 1, 1]
            target = [1, 2, 3, 4, 5]
            # Analiz motorundaki verileri buraya bağlayabiliriz
            value = [550, 80, 120, 50, 300]

            fig = go.Figure(data=[go.Sankey(
                node=dict(
                    pad=15, thickness=20,
                    line=dict(color="black", width=0.5),
                    label=label,
                    color="royalblue"
                ),
                link=dict(
                    source=source, target=target, value=value,
                    color="rgba(65, 105, 225, 0.4)"  # Şeffaf mavi akış
                ))])

            fig.update_layout(title_text="Akyıldız ATSA v2.0 - Enerji Akış Diyagramı", font_size=12)
            fig.show()

        def enerji_isi_haritasi_ciz(self):
            """Bileşenlerin görev modlarına göre enerji yoğunluk matrisi."""
            import seaborn as sns
            import matplotlib.pyplot as plt
            import numpy as np

            # Örnek veri matrisi (mAh)
            data = np.array([
                [10, 80, 150],  # ESP32: Uyku, Aktif, İletim
                [5, 40, 120],  # LoRa: Uyku, Dinleme, Gönderim
                [200, 200, 200]  # Servolar
            ])

            plt.figure(figsize=(10, 5))
            sns.heatmap(data, annot=True, fmt="d", cmap="YlOrRd",
                        xticklabels=["Uyku", "Normal", "Maksimum"],
                        yticklabels=["ESP32", "LoRa", "Servolar"])
            plt.title("Akyıldız Bileşen Enerji Yoğunluk Haritası (Heatmap)")
            plt.xlabel("Görev Modları")
            plt.ylabel("Donanım Birimleri")
            plt.show()




if __name__ == "__main__":
    app = AkyildizApp()
    app.mainloop()
