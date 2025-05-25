# -*- coding: utf-8 -*-
"""
Ana Pencere
CPU Zamanlayici, Deadlock Algilama ve Proses Yonetim Sistemi icin ana GUI penceresi.
(Daha Şık ve Modern Tasarım Uygulanmış Versiyon)
"""

# gui/main_window.py dosyasının başındaki importlar

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget,
                             QStatusBar, QLabel, QAction, QMessageBox,
                             QStyleFactory, QWidget)
# Qt ile birlikte QSize'ı da QtCore'den import edin
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPalette, QColor, QFont, QPixmap
import sys




# Sekme modulleri (Bu dosyaların var olduğu varsayılıyor)
# Gerçek uygulamada bu importların doğru çalıştığından emin olun
try:
    from gui.cpu_tab import CPUSchedulerTab
    from gui.deadlock_tab import DeadlockManagerTab
    from gui.process_tab import ProcessManagerTab
except ImportError:
    # Eğer modüller bulunamazsa, yer tutucu QWidget'lar kullan
    print("Uyarı: Sekme modülleri (gui/cpu_tab.py, gui/deadlock_tab.py, gui/process_tab.py) bulunamadı. Yer tutucular kullanılıyor.")
    CPUSchedulerTab = QWidget
    DeadlockManagerTab = QWidget
    ProcessManagerTab = QWidget # ProcessManagerTab'ı da QWidget olarak tanımla

class MainWindow(QMainWindow):
    """Ana uygulama penceresi (Yeniden Tasarlanmış)"""

    def __init__(self):
        """Ana pencereyi baslat"""
        super().__init__()

        # --- Renk Paleti ve Stil Tanımlamaları ---
        self.PRIMARY_COLOR = "#007AFF" # Daha canlı bir mavi (iOS tarzı)
        self.PRIMARY_LIGHT = "#E9F5FF" # Çok açık mavi (hover, arka plan)
        self.PRIMARY_DARK = "#0056B3"  # Koyu mavi (pressed)
        self.SECONDARY_COLOR = "#F8F9FA" # Açık gri arka plan
        self.BORDER_COLOR = "#DEE2E6"  # Daha belirgin sınır rengi
        self.TEXT_COLOR_DARK = "#212529" # Koyu gri metin
        self.TEXT_COLOR_LIGHT = "#FFFFFF" # Beyaz metin
        self.HEADER_BACKGROUND = "#343A40" # Koyu gri başlık arka planı
        self.STATUS_BAR_BACKGROUND = "#343A40" # Koyu gri durum çubuğu
        self.MENU_BAR_BACKGROUND = "#343A40"   # Koyu gri menü çubuğu
        self.DANGER_COLOR = "#DC3545" # Kırmızı (örneğin, işlem sonlandırma butonu için)
        self.DANGER_HOVER = "#C82333"

        self.setup_style()

        # --- Pencere Özellikleri ---
        self.setWindowTitle("İşletim Sistemleri Yönetim Paneli") # Daha açıklayıcı başlık
        self.setGeometry(50, 50, 1300, 850) # Biraz daha büyük ve farklı başlangıç konumu
        # self.setWindowIcon(QIcon('path/to/your/icon.png')) # Uygulama ikonu ekleyebilirsiniz

        # --- Ana Arka Plan ---
        # Palette veya ana QSS ile ayarlanabilir
        self.setStyleSheet(f"QMainWindow {{ background-color: {self.SECONDARY_COLOR}; }}")

# gui/main_window.py dosyasında __init__ metodu içinde

        # --- Sekme Widget'ı ---
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setMovable(False)
        self.tabs.setDocumentMode(False)
        # Qt.QSize yerine doğrudan QSize kullanın
        self.tabs.setIconSize(QSize(20, 20)) # İkonlar için boyut

        tab_style = f"""
        QTabWidget::pane {{
            border: 1px solid {self.BORDER_COLOR};
            background: {self.TEXT_COLOR_LIGHT}; /* Beyaz iç alan */
            border-radius: 5px;
            margin: 0px; /* Pane etrafında boşluk yok */
            padding: 10px; /* İçeriğe dolgu */
        }}
        QTabWidget::tab-bar {{
            alignment: left;
            left: 10px; /* Sekmeleri biraz sağa kaydır */
        }}
        QTabBar::tab {{
            background: {self.SECONDARY_COLOR}; /* Sekme arka planı */
            color: {self.TEXT_COLOR_DARK};
            border: 1px solid {self.BORDER_COLOR};
            border-bottom: none; /* Alt kenarlığı kaldır */
            padding: 10px 20px;
            margin-right: 4px; /* Sekmeler arası boşluk */
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            font-size: 14px; /* Biraz daha küçük font */
            font-weight: 500; /* Normalden biraz kalın */
            min-width: 150px; /* Daha geniş sekmeler */
            min-height: 35px;
        }}
        QTabBar::tab:selected {{
            background: {self.TEXT_COLOR_LIGHT}; /* Seçili sekme arka planı (pane ile aynı) */
            color: {self.PRIMARY_COLOR}; /* Seçili sekme metin rengi */
            border: 1px solid {self.BORDER_COLOR};
            border-bottom: 2px solid {self.PRIMARY_COLOR}; /* Seçili olduğunu gösteren alt çizgi */
            font-weight: 600; /* Seçili sekme daha kalın */
            margin-bottom: -1px; /* Pane ile birleşmesi için */
        }}
        QTabBar::tab:hover:!selected {{
            background: {self.PRIMARY_LIGHT};
            color: {self.PRIMARY_DARK};
            border: 1px solid {self.BORDER_COLOR}; /* Hover durumunda kenarlık kalsın */
            border-bottom: none;
        }}
        QTabBar::tab:disabled {{
            background: #EAEAEA; /* Disabled tab background */
            color: #999999;      /* Disabled tab text color */
        }}
        """
        self.tabs.setStyleSheet(tab_style)

        # --- Sekmeleri Oluştur ---
        # Not: Bu sekmelerin içeriği orijinal kodunuzdaki gibi varsayılıyor
        # ve stilleri de genel QSS'den etkilenecek.
        self.cpu_tab = CPUSchedulerTab()
        self.deadlock_tab = DeadlockManagerTab()
        self.process_tab = ProcessManagerTab() # Bu değişkenin adının process_tab olması gerekiyordu

        # --- Sekmeleri Ekle (İkonlarla birlikte) ---
        # İkonları projenize eklemeniz veya uygun Qt ikonlarını kullanmanız gerekir.
        # Örnek olarak Qt'nin standart ikonları kullanılabilir veya dosya yolları verilebilir.
        # self.tabs.addTab(self.cpu_tab, QIcon.fromTheme("cpu"), "CPU Zamanlayıcı") # Örnek: Tema ikonu
        # self.tabs.addTab(self.deadlock_tab, QIcon.fromTheme("dialog-error"), "Deadlock Yönetimi") # Örnek: Tema ikonu
        # self.tabs.addTab(self.process_tab, QIcon.fromTheme("system-run"), "Proses Yönetimi") # Örnek: Tema ikonu
        # Eğer ikon yoksa:
        self.tabs.addTab(self.cpu_tab, "CPU Zamanlayıcı")
        self.tabs.addTab(self.deadlock_tab, "Deadlock Yönetimi")
        self.tabs.addTab(self.process_tab, "Proses Yönetimi")

        # Ana widget olarak sekmeleri ayarla
        self.setCentralWidget(self.tabs)

        # --- Durum Çubuğu ---
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: {self.STATUS_BAR_BACKGROUND};
                color: {self.TEXT_COLOR_LIGHT};
                font-size: 13px;
                font-weight: 500;
                padding: 5px 10px; /* Daha ince durum çubuğu */
                border: none;
                border-top: 1px solid #495057; /* Üstte hafif ayrım çizgisi */
            }}
            QStatusBar::item {{
                border: none; /* Bölümler arası kenarlığı kaldır */
            }}
        """)
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("Hazır")
        # Font ayarı QSS içinde yapıldığı için burada gereksiz olabilir
        # self.status_label.setFont(QFont("Segoe UI", 10)) # Biraz daha küçük font
        self.status_bar.addWidget(self.status_label) # Kalıcı mesaj olarak ekle

        # --- Menü Çubuğu ---
        self.create_menu_bar() # Menü oluşturma fonksiyonunu çağır

        # Başlangıç durumu
        self.status_label.setText("Uygulama başarıyla başlatıldı.")

        # --- Genel Stil Sayfası (Uygulamanın Geri Kalanı İçin) ---
        self.setStyleSheet(self.centralWidget().styleSheet() + f"""
            /* Ana Pencereye de arka plan verelim */
            QMainWindow {{
                background-color: {self.SECONDARY_COLOR};
            }}

            /* Grup Kutuları */
            QGroupBox {{
                background-color: {self.TEXT_COLOR_LIGHT}; /* Beyaz arka plan */
                border: 1px solid {self.BORDER_COLOR};
                border-radius: 8px;
                margin-top: 25px; /* Başlık için yer aç */
                padding: 15px; /* İçerik için dolgu */
                font-size: 16px; /* Başlık font boyutu */
                font-weight: 600;
                color: {self.TEXT_COLOR_DARK};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left; /* Başlığı sola al */
                left: 15px;
                top: 8px; /* Dikeyde ortala */
                padding: 5px 10px;
                background-color: {self.PRIMARY_COLOR}; /* Başlık arka planı */
                border-radius: 4px;
                color: {self.TEXT_COLOR_LIGHT}; /* Başlık metni */
                font-size: 14px; /* Başlık fontu biraz daha küçük */
                font-weight: 600;
            }}

            /* Butonlar */
            QPushButton {{
                background-color: {self.PRIMARY_COLOR};
                color: {self.TEXT_COLOR_LIGHT};
                padding: 10px 20px; /* Daha büyük butonlar */
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
                border: none;
                min-height: 35px;
                /* Geçiş efekti (basit fade) */
                /* transition: background-color 0.2s ease-in-out; */ /* QSS bunu doğrudan desteklemez */
            }}
            QPushButton:hover {{
                background-color: {self.PRIMARY_DARK}; /* Hover rengi */
                /* cursor: pointer; */ /* QSS'de cursor doğrudan yok */
            }}
            QPushButton:pressed {{
                background-color: {self.PRIMARY_DARK}; /* Pressed için de aynı koyu renk */
                /* Varsa hafif içe gölge eklenebilir */
            }}
            QPushButton:disabled {{
                background-color: #ADB5BD; /* Gri */
                color: #F8F9FA;
            }}
             /* Özel Buton Stili (Örnek: Sonlandırma Butonu) */
            QPushButton#killButton {{ /* process_tab.py içinde objeye bu isim verilmeli */
                 background-color: {self.DANGER_COLOR};
            }}
             QPushButton#killButton:hover {{
                 background-color: {self.DANGER_HOVER};
            }}


            /* Giriş Alanları */
            QLineEdit, QSpinBox, QComboBox {{
                border: 1px solid {self.BORDER_COLOR};
                padding: 8px 12px; /* Daha ferah padding */
                border-radius: 6px;
                background-color: {self.TEXT_COLOR_LIGHT};
                font-size: 14px;
                color: {self.TEXT_COLOR_DARK};
                min-height: 35px; /* Butonlarla aynı yükseklik */
            }}
            QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
                border: 1px solid {self.PRIMARY_COLOR}; /* Odaklanınca belirginleş */
                /* Hafif bir gölge eklenebilir ama QSS ile zor */
                /* background-color: #FDFEFE; */ /* Çok hafif renk değişimi */
            }}
             QComboBox::drop-down {{
                 border: none; /* Açılır ok etrafındaki kenarlığı kaldır */
                 width: 20px;
             }}
             QComboBox::down-arrow {{
                 /* İsteğe bağlı olarak özel bir ok resmi eklenebilir */
                 /* image: url(path/to/arrow.png); */
             }}


            /* Tablolar */
            QTableWidget {{
                alternate-background-color: {self.PRIMARY_LIGHT}; /* Alternatif satır rengi */
                background-color: {self.TEXT_COLOR_LIGHT};
                gridline-color: {self.BORDER_COLOR}; /* Izgara çizgisi */
                selection-background-color: {self.PRIMARY_COLOR}; /* Seçim arka planı */
                selection-color: {self.TEXT_COLOR_LIGHT}; /* Seçim metni */
                border: 1px solid {self.BORDER_COLOR};
                border-radius: 6px;
                font-size: 13px; /* Tablo içi font biraz daha küçük */
            }}
            QTableWidget QHeaderView::section {{
                background-color: {self.HEADER_BACKGROUND}; /* Başlık arka planı */
                color: {self.TEXT_COLOR_LIGHT};
                padding: 10px; /* Başlık padding */
                font-size: 14px;
                font-weight: 600;
                border: none;
                border-bottom: 1px solid {self.BORDER_COLOR}; /* Başlık alt çizgisi */
                 border-right: 1px solid {self.BORDER_COLOR}; /* Dikey ayırıcılar */
             }}
             QTableWidget QHeaderView::section:last {{
                 border-right: none; /* Son başlıkta sağ kenarlık olmasın */
             }}
             QTableWidget::item {{
                 padding: 8px; /* Hücre içi boşluk */
             }}

            /* Etiketler */
            QLabel {{
                color: {self.TEXT_COLOR_DARK};
                font-size: 14px;
                background-color: transparent; /* Arka planı şeffaf yap */
            }}
            QLabel#errorLabel {{ /* Hata mesajları için özel stil (QLabel'e bu isim verilmeli) */
                 color: {self.DANGER_COLOR};
                 font-weight: bold;
             }}
        """)

        # Sekme değişimi sinyalini bağla
        self.tabs.currentChanged.connect(self.tab_changed)

    def setup_style(self):
        """Renk teması ve stili ayarlar (QSS ağırlıklı)"""
        QApplication.setStyle(QStyleFactory.create('Fusion')) # Temel olarak Fusion iyi

        # QPalette yerine QSS kullandığımız için burası büyük ölçüde gereksizleşiyor
        # Ancak bazı temel renkleri ayarlamakta fayda var
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(self.SECONDARY_COLOR))
        palette.setColor(QPalette.WindowText, QColor(self.TEXT_COLOR_DARK))
        palette.setColor(QPalette.Base, QColor(self.TEXT_COLOR_LIGHT))
        palette.setColor(QPalette.AlternateBase, QColor(self.PRIMARY_LIGHT))
        palette.setColor(QPalette.ToolTipBase, QColor(self.TEXT_COLOR_LIGHT))
        palette.setColor(QPalette.ToolTipText, QColor(self.TEXT_COLOR_DARK))
        palette.setColor(QPalette.Text, QColor(self.TEXT_COLOR_DARK))
        palette.setColor(QPalette.Button, QColor(self.PRIMARY_LIGHT)) # Buton arka planı QSS ile ezilecek
        palette.setColor(QPalette.ButtonText, QColor(self.TEXT_COLOR_DARK)) # QSS ile ezilecek
        palette.setColor(QPalette.BrightText, QColor(self.DANGER_COLOR)) # Dikkat çekici metinler için kullanılabilir
        palette.setColor(QPalette.Highlight, QColor(self.PRIMARY_COLOR)) # Seçim rengi
        palette.setColor(QPalette.HighlightedText, QColor(self.TEXT_COLOR_LIGHT)) # Seçili metin rengi
        palette.setColor(QPalette.Link, QColor(self.PRIMARY_DARK))

        QApplication.setPalette(palette)

        # Genel font ayarı
        font = QFont("Segoe UI", 10) # Varsayılan fontu ayarla
        QApplication.setFont(font)


    def create_menu_bar(self):
        """Menu çubuğunu modern bir stille oluşturur"""
        menu_style = f"""
        QMenuBar {{
            background-color: {self.MENU_BAR_BACKGROUND};
            color: {self.TEXT_COLOR_LIGHT}; /* Metin rengi beyaz */
            padding: 6px 10px; /* Daha ince menü */
            font-size: 13px; /* Biraz daha küçük font */
            font-weight: 500;
            border: none;
            /* Alt border eklenebilir */
            /* border-bottom: 1px solid #495057; */
        }}
        QMenuBar::item {{
            background-color: transparent;
            padding: 6px 12px;
            color: {self.TEXT_COLOR_LIGHT}; /* Öğe metni beyaz */
             border-radius: 4px; /* Hafif köşe yuvarlama */
             margin-right: 5px; /* Menü elemanları arası boşluk */
        }}
        QMenuBar::item:selected {{ /* Üzerine gelince veya açılınca */
            background-color: #495057; /* Hafif koyu gri */
        }}
        QMenuBar::item:pressed {{ /* Tıklanınca */
             background-color: #5A6268;
         }}
        QMenu {{
            background-color: {self.TEXT_COLOR_LIGHT}; /* Açılır menü arka planı */
            border: 1px solid {self.BORDER_COLOR};
            padding: 8px; /* İç boşluk */
            font-size: 13px; /* Menü içi font */
             border-radius: 4px; /* Köşe yuvarlama */
         }}
         QMenu::item {{
             padding: 8px 25px; /* Öğe içi boşluk (sağda ikon için yer) */
             color: {self.TEXT_COLOR_DARK}; /* Öğe metin rengi */
             background-color: transparent;
             border-radius: 4px; /* Öğeler için de yuvarlama */
         }}
         QMenu::item:selected {{
             background-color: {self.PRIMARY_LIGHT}; /* Seçili öğe arka planı */
             color: {self.PRIMARY_DARK}; /* Seçili öğe metni */
         }}
         QMenu::separator {{
             height: 1px;
             background: {self.BORDER_COLOR};
             margin: 5px 0px; /* Ayraç etrafı boşluk */
         }}
        """
        self.menuBar().setStyleSheet(menu_style)

        menu_bar = self.menuBar()

        # Dosya Menüsü
        file_menu = menu_bar.addMenu("Dosya")
        # exit_icon = QIcon.fromTheme("application-exit") # Örnek ikon
        # exit_action = QAction(exit_icon, "Çıkış", self)
        exit_action = QAction("Çıkış", self) # İkonsuz versiyon
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Uygulamayı Kapatır") # Durum çubuğunda açıklama
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Yardım Menüsü
        help_menu = menu_bar.addMenu("Yardım")
        # about_icon = QIcon.fromTheme("help-about") # Örnek ikon
        # about_action = QAction(about_icon, "Hakkında", self)
        about_action = QAction("Hakkında", self) # İkonsuz versiyon
        about_action.setStatusTip("Uygulama Hakkında Bilgi") # Durum çubuğunda açıklama
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def tab_changed(self, index):
        """
        Sekme degistiginde cagrilir
        Parametreler: index (int): Yeni sekme indeksi
        """
        tab_names = ["CPU Zamanlayıcı", "Deadlock Yönetimi", "Proses Yönetimi"]
        if 0 <= index < len(tab_names):
            self.status_label.setText(f"Aktif Sekme: {tab_names[index]}")

            # ProcessManagerTab sınıfının var olup olmadığını ve metodun varlığını kontrol et
            if index == 2 and isinstance(self.process_tab, QWidget) and hasattr(self.process_tab, 'start_monitoring_if_needed'):
                 try:
                     # Proses izlemeyi başlat (eğer başlatılmadıysa)
                     self.process_tab.start_monitoring_if_needed()
                 except AttributeError:
                     print("Uyarı: 'process_tab' nesnesinde 'start_monitoring_if_needed' metodu bulunamadı.")
                 except Exception as e:
                     print(f"Hata: Proses izleme başlatılırken sorun oluştu: {e}")
            # Diğer sekmelere geçildiğinde izlemeyi durdurmak isteyebilirsiniz (opsiyonel)
            elif hasattr(self.process_tab, 'stop_monitoring'):
                 try:
                     # Başka sekmeye geçince izlemeyi durdurabiliriz (isteğe bağlı)
                     # self.process_tab.stop_monitoring()
                     pass # Şimdilik durdurmuyoruz
                 except AttributeError:
                     # Metod yoksa veya nesne QWidget ise hata vermeden geç
                     pass
                 except Exception as e:
                     print(f"Hata: Proses izleme durdurulurken sorun oluştu: {e}")

        else:
             self.status_label.setText("Bilinmeyen sekme")

    def closeEvent(self, event):
        """
        Pencere kapatilmadan once cagrilir
        Parametreler: event (QCloseEvent): Kapatma olayi
        """
        # ProcessManagerTab sınıfının var olup olmadığını ve metodun varlığını kontrol et
        if isinstance(self.process_tab, QWidget) and hasattr(self.process_tab, 'stop_monitoring'):
            try:
                # Proses izlemeyi durdur
                print("Proses izleme durduruluyor...")
                self.process_tab.stop_monitoring()
            except AttributeError:
                 print("Uyarı: 'process_tab' nesnesinde 'stop_monitoring' metodu bulunamadı.")
            except Exception as e:
                 print(f"Hata: Proses izleme kapatılırken sorun oluştu: {e}")
        else:
             print("Uyarı: Proses sekmesi veya 'stop_monitoring' metodu bulunamadığı için izleme durdurulamadı.")

        print("Uygulama kapatılıyor.")
        event.accept()

    def show_about_dialog(self):
        """Hakkinda iletisim kutusunu modern stille gosterir"""
        # Geliştirici adı gibi bilgileri dinamik veya sabit olarak ayarlayabilirsiniz
        developer_name = "Mehmet KARATAŞ"
        app_version = "1.1 (Revize Tasarım)"

        about_text = f"""
        <div style="font-family: Segoe UI, sans-serif; text-align: center;">
            <h2 style="color: {self.PRIMARY_COLOR}; margin-bottom: 5px;">İşletim Sistemleri Yönetim Paneli</h2>
            <p style="font-size: 12px; color: #6C757D; margin-top: 0px;">Versiyon: {app_version}</p>
            <hr style="border: none; border-top: 1px solid {self.BORDER_COLOR}; margin: 15px 0;">

            <p style="font-size: 14px; color: {self.TEXT_COLOR_DARK}; line-height: 1.6;">
                Bu uygulama, işletim sistemleri dersi kapsamında öğrenilen temel kavramları
                (CPU zamanlama algoritmaları, deadlock (kilitlenme) tespiti ve önlenmesi,
                proses yönetimi) görselleştirmek ve simüle etmek amacıyla geliştirilmiştir.
            </p>

            <p style="margin-top: 20px; font-weight: 500; color: {self.TEXT_COLOR_DARK}; font-size: 14px;">
                Geliştirici: <strong style="color: {self.PRIMARY_DARK};">{developer_name}</strong>
            </p>

            <p style="margin-top: 10px; font-size: 12px; color: #6C757D;">
                © 2025 - Tüm Hakları Saklıdır (varsa)
            </p>
        </div>
        """

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Hakkında")
        msg_box.setTextFormat(Qt.RichText) # HTML içeriği için RichText
        msg_box.setText(about_text)
        # msg_box.setIconPixmap(QPixmap('path/to/your/logo.png').scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)) # Özel ikon ekle
        msg_box.setIcon(QMessageBox.Information) # Standart bilgi ikonu
        msg_box.setStandardButtons(QMessageBox.Ok)

        # İletişim kutusu ve içindeki buton için stil
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: {self.TEXT_COLOR_LIGHT};
                border: 1px solid {self.BORDER_COLOR};
                border-radius: 8px;
                font-family: Segoe UI, sans-serif; /* Fontu ayarla */
            }}
            QLabel#qt_msgbox_label {{ /* Metin etiketini hedefle */
                color: {self.TEXT_COLOR_DARK};
                font-size: 14px;
                padding: 10px;
            }}
            QLabel#qt_msgboxex_icon_label {{ /* İkon etiketini hedefle */
                 /* İkon boyutunu veya konumunu ayarlamak için kullanılabilir */
                 padding-right: 10px;
            }}

            QPushButton {{
                background-color: {self.PRIMARY_COLOR};
                color: white;
                padding: 8px 25px; /* Daha geniş buton */
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
                border: none;
                min-width: 100px; /* Minimum genişlik */
                min-height: 30px;
            }}
            QPushButton:hover {{
                background-color: {self.PRIMARY_DARK};
            }}
            QPushButton:pressed {{
                background-color: {self.PRIMARY_DARK};
            }}
        """)

        msg_box.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # # Yazı tiplerini yükle (Eğer özel font kullanıyorsanız)
    # QFontDatabase.addApplicationFont("path/to/your/font.ttf")

    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())