# -*- coding: utf-8 -*-
"""
CPU Zamanlayici, Deadlock Algilama ve Proses Yonetim Sistemi
Ana uygulama dosyasi

Bu uygulama, isletim sistemleri dersinde ogrenilen CPU zamanlama, 
deadlock yonetimi ve proses yonetimi kavramlarini pratik bir uygulama 
ile pekistirmek amaciyla gelistirilmistir.
"""

import sys
import os

# Python modul arama yoluna mevcut dizini ekle
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

# Henüz içe aktarmayı dene
try:
    # GUI ana penceresini içe aktar
    from gui.main_window import MainWindow
except Exception as e:
    print(f"Hata: {e}")
    input("Devam etmek için herhangi bir tuşa basın...")
    sys.exit(1)

def main():
    """Ana uygulama fonksiyonu"""
    # QApplication nesnesi olustur
    app = QApplication(sys.argv)
    app.setApplicationName("Isletim Sistemleri Proje")
    
    # Ana pencere olustur
    window = MainWindow()
    
    # Pencereyi goster
    window.show()
    
    # Uygulama dongusunu baslat
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()