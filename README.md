# Akyıldız ATSA v2.0 - Model Uydu Analiz ve Simülasyon Sistemi

Akyıldız ATSA v2.0, model uyduların tasarım, test ve Ön Tasarım İnceleme (PDR) süreçlerini dijitalleştirmek amacıyla geliştirilmiş gelişmiş bir analiz yazılımıdır. Sistem; özgün 3D CAD modellerini (.STL) işleyerek aerodinamik, haberleşme, yapısal mukavemet ve enerji bütçesi simülasyonlarını dinamik olarak gerçekleştirir.

Bu proje, **Niğde Ömer Halisdemir Üniversitesi** bünyesindeki Ar-Ge çalışmaları ve model uydu yarışmaları standartları dikkate alınarak optimize edilmiştir.

---

## 🚀 Öne Çıkan Teknik Özellikler

* **Gelişmiş Kütle ve Denge Analizi:** Donanım ağırlıkları entegre edilmiş **1710.0 gramlık** gerçekçi uçuş kütlesi hesaplaması.
* **Aerodinamik İniş Simülasyonu:** 0.5m paraşüt çapı ile **9.64 m/s** terminal iniş hızı ve **2.07 G** paraşüt açılma şoku tahmini.
* **RF Link Bütçesi (Haberleşme):** 433 MHz frekansında, SX1278 LoRa modülü için serbest uzay yol kaybı (FSPL) ve **70.93 dB** güvenlik marjı analizi.
* **Yeni Nesil Görselleştirme:** Güç dağılımı için **Sankey Diyagramı** ve görev modlarına göre bileşen bazlı **Enerji Yoğunluk Haritası (Heatmap)**.

---

## 🛠️ Görev Yükü ve Donanım Mimarisi

Simülasyon, uydunun üzerinde fiziksel olarak yer alan şu komponent matrisine göre akım tüketimi ve ağırlık merkezi hesabı yapar:

| Birim Tipi | Seçilen Model | Açıklama |
| :--- | :--- | :--- |
| **İşlemci** | STM32F103C8T6 (Blue Pill) | Ana Kontrolcü |
| **Haberleşme** | SX 1278 LoRa Modülü | 433 MHz Telemetri |
| **Kamera** | ESP32-CAM | Görüntü Aktarımı |
| **Sensör Grubu** | BMP280 & MPU6050 | Sıcaklık, Basınç, Jiroskop |
| **Batarya** | 7.4 V 1000 mAh Li-Po | Ana Güç Kaynağı |
| **Eyleyici** | T-MOTOR MN4006 | Ayrılma/Mekanik Sürücü |

---

## 📦 Kurulum ve Çalıştırma

Projenin yerel bilgisayarınızda çalıştırılabilmesi için aşağıdaki adımları izleyin.

1. Projeyi bilgisayarınıza indirin:
   ```bash
   git clone [https://github.com/akkoyungulnisa/Aky-ld-z-Model-Uydu-Analiz.git](https://github.com/akkoyungulnisa/Aky-ld-z-Model-Uydu-Analiz.git)
   cd Aky-ld-z-Model-Uydu-Analiz
