
 🖥️ İşletim Sistemleri Yönetim Uygulaması

**CPU Zamanlayıcı | Deadlock Yönetimi | Proses İzleme ve Kontrol Sistemi**  
Geliştirici: Mehmet Karataş  
Lisans: MIT  
Versiyon: v1.0



📌 Proje Özeti

Bu proje, işletim sistemleri dersinde öğrenilen teorik kavramların gerçek zamanlı bir masaüstü uygulama üzerinden simülasyon ve analiz edilmesini amaçlar. Uygulama; CPU zamanlama algoritmalarını test etme, deadlock (kilitlenme) senaryoları oluşturma/algılama ve aktif sistem proseslerini izleyip yönetme yeteneklerine sahiptir.



📁 Proje Yapısı


<img width="308" alt="image" src="https://github.com/user-attachments/assets/3c256d0b-f1e5-40eb-8bd8-7f5e55f1f808" />



 ⚙️ Kurulum ve Başlatma

✅ Gereksinimler

* Python 3.6 veya üzeri
* Gerekli Python kütüphaneleri:

  * PyQt5
  * matplotlib
  * psutil
  * numpy
  * networkx

🔧 Ortam Kurulumu


# Sanal ortam oluşturun
python -m venv venv

# Ortamı aktif edin (Windows)
venv\Scripts\activate

# Gerekli kütüphaneleri yükleyin
pip install -r requirements.txt


▶️ Uygulamayı Başlatma


python src/main.py


Uygulama açıldığında üç ana sekme görünecektir:

* CPU Zamanlayıcı
* Deadlock Yönetimi
* Proses Yönetimi


## 🧠 Modül Açıklamaları

### 1️⃣ CPU Zamanlayıcı

📌 *Desteklenen Algoritmalar:*
FCFS, SJF, SRTF, Round Robin`, Priority

🔹 Proses ekle (varış zamanı, işlem süresi, öncelik)
🔹 Algoritmayı seç → Gantt şeması + metrikler
🔹 Tüm algoritmaları karşılaştır (grafiksel)

🖼️ Örnek Arayüz:

<img width="1260" alt="CPU Zamanlayıcı" src="https://github.com/user-attachments/assets/b0c9d847-a7ce-432e-9546-4ce656539389" />



2️⃣ Deadlock Yönetimi

🧩 *İki Alt Sistem:*

* Deadlock Algılama (Resource Allocation Graph)
* Banker's Algoritması (Güvenli durum kontrolü)

🔸 Kaynak ve proses ekleyin
🔸 Kaynak tahsis ve talep oluşturun
🔸 Deadlock kontrolü yapın
🔸 Banker's ile güvenli durum kontrolü

🖼️ Örnek Arayüz:
<img width="1260" alt="Deadlock Yönetimi" src="https://github.com/user-attachments/assets/6cf229c0-cd96-4c55-bdec-342b142b2411" />


3️⃣ Proses Yönetimi

🔍 *Gerçek Zamanlı İzleme:*
Sistemdeki proseslerin CPU ve bellek kullanımını grafiklerle izler

🔧 *Kontrol İşlemleri:*

* Proses başlatma (`notepad.exe` vb.)
* Proses durdurma
* İzleme başlatma/durdurma
* Öncelik değiştirme

📊 *Canlı grafikler:*

* CPU Kullanımı
* Bellek Kullanımı

🖼️ Örnek Arayüz:
<img width="1260" alt="prosses Yönetimi" src="https://github.com/user-attachments/assets/73436d74-20cd-46ab-b0a7-c22a68fd3ebc" />


🧪 Kullanım Senaryosu

**Senaryo: Zamanlama Algoritması Karşılaştırması**

1. 3 proses ekleyin: P1(0,5,1), P2(1,3,2), P3(2,8,3)
2. FCFS ve SJF algoritmalarını çalıştırın
3. Gantt şeması ve ortalama süreleri karşılaştırın
4. Tüm algoritmaları karşılaştır sekmesine geçin

**Senaryo: Deadlock Testi**

1. R1(1) ve R2(1) kaynaklarını tanımlayın
2. P1 ve P2 proseslerini tanımlayın
3. R1 → P1, R2 → P2 tahsis edin
4. P1 → R2, P2 → R1 talep ettirin
5. Deadlock kontrolü yapın



## 💡 Ekstra Bilgiler

### Performans İpuçları

* Proses izleme aralığını artırmak sistemi rahatlatır
* Deadlock grafikleri büyük sistemlerde daha yavaş olabilir

### Sorun Giderme

* ImportError: pip install -r requirements.txt komutunu tekrar çalıştır
* Grafik gözükmüyorsa: pip install matplotlib --upgrade
* PermissionError: Uygulamayı yönetici olarak çalıştırın


## 📚 Kaynaklar

* Operating System Concepts - Silberschatz et al.
* [https://docs.python.org/](https://docs.python.org/)
* [https://matplotlib.org/](https://matplotlib.org/)
* [https://networkx.org/](https://networkx.org/)
* [https://psutil.readthedocs.io/](https://psutil.readthedocs.io/)



