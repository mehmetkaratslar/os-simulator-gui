# -*- coding: utf-8 -*-
"""
Proses Yonetim Sekmesi
Sistemdeki prosesleri izleme ve yonetme arayuzu.
"""

import sys
import os
import psutil
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
                           QGroupBox, QSpinBox, QFormLayout, QTabWidget,
                           QMessageBox, QHeaderView, QLineEdit, QMenu, QProgressBar,
                           QScrollArea)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont, QIcon, QCursor, QBrush, QLinearGradient
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from process_manager.monitor import ProcessMonitor
from process_manager.controller import ProcessController

class ProcessManagerTab(QWidget):
    """Proses yonetim sekmesi"""
    
    def __init__(self):
        """Proses yonetim sekmesini baslat"""
        super().__init__()
        
        # Proses izleyici ve kontrol
        self.monitor = ProcessMonitor()
        self.controller = ProcessController()
        
        # Izlenen prosesler ve guncelleme zamanlayicisi
        self.monitoring_active = False
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_process_list)
        
        # Renk paleti
        self.colors = {
            "primary": "#3498db",      # Mavi
            "secondary": "#2ecc71",    # Yeşil
            "accent": "#e74c3c",       # Kırmızı
            "warning": "#f39c12",      # Turuncu
            "info": "#9b59b6",         # Mor
            "light": "#ecf0f1",        # Açık gri
            "light_alt": "#f5f5f5",    # Daha açık gri
            "dark": "#34495e",         # Koyu lacivert 
            "dark_alt": "#2c3e50",     # Daha koyu lacivert
            "success": "#27ae60",      # Koyu yeşil
            "error": "#c0392b",        # Koyu kırmızı
            "table_header": "#2c3e50", # Tablo başlığı
            "table_alt": "#f9f9f9",    # Tablo alternatif satır
            "low_usage": "#e8f5e9",    # Düşük kullanım (açık yeşil)
            "medium_usage": "#fff8e1", # Orta kullanım (açık sarı)
            "high_usage": "#ffebee"    # Yüksek kullanım (açık kırmızı)
        }
        
        # Arayuzu olustur
        self.init_ui()
    
    def init_ui(self):
        """Kullanici arayuzunu olusturur"""
        # Ana duzen
        main_layout = QVBoxLayout()
        
        # Baslik
        title_label = QLabel("Gerçek Zamanlı Proses Yönetim Sistemi")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"""
            color: {self.colors['dark']};
            font-size: 20px;
            font-weight: bold;
            margin: 12px 0;
            padding: 10px;
            background: linear-gradient(to right, {self.colors['primary']} 0%, {self.colors['secondary']} 100%);
            color: white;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        """)
        main_layout.addWidget(title_label)
        
        # Ust panel: Proses baslatma ve izleme kontrolleri
        top_panel = QHBoxLayout()
        
        # Sol: Proses baslatma
        start_group = QGroupBox("Proses Başlat")
        start_group.setStyleSheet(f"""
            QGroupBox {{
                background: linear-gradient(to bottom, {self.colors['light']} 0%, {self.colors['light_alt']} 100%);
                border: 2px solid {self.colors['secondary']};
                border-radius: 8px;
                margin-top: 20px;
                font-weight: bold;
                padding: 10px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 5px 10px;
                background-color: {self.colors['secondary']};
                color: white;
                border-radius: 5px;
            }}
        """)
        start_layout = QFormLayout()
        
        self.command_edit = QLineEdit()
        if sys.platform.startswith('win'):
            self.command_edit.setPlaceholderText("Örn: notepad.exe")
        else:
            self.command_edit.setPlaceholderText("Örn: gedit")
        self.command_edit.setStyleSheet(f"""
            QLineEdit {{
                border: 2px solid #d1d5db;
                padding: 8px;
                border-radius: 6px;
                background-color: white;
                font-size: 14px;
                transition: all 0.3s ease;
            }}
            QLineEdit:focus {{
                border: 2px solid {self.colors['secondary']};
                box-shadow: 0 0 5px rgba(46, 204, 113, 0.3);
            }}
        """)
        command_label = QLabel("Komut:")
        command_label.setStyleSheet(f"font-weight: bold; color: {self.colors['dark']}; font-size: 14px;")
        start_layout.addRow(command_label, self.command_edit)
        
        self.start_button = QPushButton("Prosesi Başlat")
        self.start_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['secondary']};
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                border: none;
                transition: all 0.3s ease;
            }}
            QPushButton:hover {{
                background-color: #27ae60;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
            }}
            QPushButton:pressed {{
                background-color: #1e8449;
                transform: scale(0.98);
            }}
        """)
        self.start_button.clicked.connect(self.start_process)
        start_layout.addRow(self.start_button)
        
        start_group.setLayout(start_layout)
        
        # Orta: Izleme kontrolleri
        monitoring_group = QGroupBox("İzleme Kontrolleri")
        monitoring_group.setStyleSheet(f"""
            QGroupBox {{
                background: linear-gradient(to bottom, {self.colors['light']} 0%, {self.colors['light_alt']} 100%);
                border: 2px solid {self.colors['primary']};
                border-radius: 8px;
                margin-top: 20px;
                font-weight: bold;
                padding: 10px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 5px 10px;
                background-color: {self.colors['primary']};
                color: white;
                border-radius: 5px;
            }}
        """)
        monitoring_layout = QVBoxLayout()
        
        monitoring_buttons = QHBoxLayout()
        
        self.start_monitoring_button = QPushButton("İzlemeyi Başlat")
        self.start_monitoring_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['primary']};
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                border: none;
                transition: all 0.3s ease;
            }}
            QPushButton:hover {{
                background-color: #2980b9;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
            }}
            QPushButton:pressed {{
                background-color: #1c5a85;
                transform: scale(0.98);
            }}
        """)
        self.start_monitoring_button.clicked.connect(self.start_monitoring)
        monitoring_buttons.addWidget(self.start_monitoring_button)
        
        self.stop_monitoring_button = QPushButton("İzlemeyi Durdur")
        self.stop_monitoring_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['accent']};
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                border: none;
                transition: all 0.3s ease;
            }}
            QPushButton:hover {{
                background-color: {self.colors['error']};
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
            }}
            QPushButton:pressed {{
                background-color: #96281f;
                transform: scale(0.98);
            }}
            QPushButton:disabled {{
                background-color: #d1d5db;
                color: #6b7280;
            }}
        """)
        self.stop_monitoring_button.clicked.connect(self.stop_monitoring)
        self.stop_monitoring_button.setEnabled(False)
        monitoring_buttons.addWidget(self.stop_monitoring_button)
        
        monitoring_layout.addLayout(monitoring_buttons)
        
        self.monitoring_status_label = QLabel("İzleme durduruldu")
        self.monitoring_status_label.setStyleSheet(f"""
            color: {self.colors['dark']};
            padding: 8px;
            border-radius: 5px;
            font-weight: bold;
            font-size: 14px;
            background-color: #f3f4f6;
            border: 1px solid #d1d5db;
            text-align: center;
            margin-top: 8px;
            transition: all 0.3s ease;
        """)
        self.monitoring_status_label.setAlignment(Qt.AlignCenter)
        monitoring_layout.addWidget(self.monitoring_status_label)
        
        monitoring_group.setLayout(monitoring_layout)
        
        # Sag: Guncelleme araligi
        refresh_group = QGroupBox("Güncelleme Aralığı")
        refresh_group.setStyleSheet(f"""
            QGroupBox {{
                background: linear-gradient(to bottom, {self.colors['light']} 0%, {self.colors['light_alt']} 100%);
                border: 2px solid {self.colors['info']};
                border-radius: 8px;
                margin-top: 20px;
                font-weight: bold;
                padding: 10px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 5px 10px;
                background-color: {self.colors['info']};
                color: white;
                border-radius: 5px;
            }}
        """)
        refresh_layout = QFormLayout()
        
        self.refresh_interval_spin = QSpinBox()
        self.refresh_interval_spin.setRange(1, 10)
        self.refresh_interval_spin.setValue(2)
        self.refresh_interval_spin.setSuffix(" saniye")
        self.refresh_interval_spin.setStyleSheet(f"""
            QSpinBox {{
                border: 2px solid #d1d5db;
                padding: 8px;
                border-radius: 6px;
                background-color: white;
                font-size: 14px;
                transition: all 0.3s ease;
            }}
            QSpinBox:focus {{
                border: 2px solid {self.colors['info']};
                box-shadow: 0 0 5px rgba(155, 89, 182, 0.3);
            }}
        """)
        interval_label = QLabel("Aralık:")
        interval_label.setStyleSheet(f"font-weight: bold; color: {self.colors['dark']}; font-size: 14px;")
        refresh_layout.addRow(interval_label, self.refresh_interval_spin)
        
        self.refresh_button = QPushButton("Şimdi Güncelle")
        self.refresh_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['info']};
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                border: none;
                transition: all 0.3s ease;
            }}
            QPushButton:hover {{
                background-color: #8e44ad;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
            }}
            QPushButton:pressed {{
                background-color: #6c3483;
                transform: scale(0.98);
            }}
        """)
        self.refresh_button.clicked.connect(self.refresh_now)
        refresh_layout.addRow(self.refresh_button)
        
        refresh_group.setLayout(refresh_layout)
        
        # Top panele gruplari ekle
        top_panel.addWidget(start_group)
        top_panel.addWidget(monitoring_group)
        top_panel.addWidget(refresh_group)
        
        # Orta panel: Proses listesi
        mid_panel = QVBoxLayout()
        
        # Proses tablosu bilgi
        table_panel = QHBoxLayout()
        
        table_label = QLabel("Sistem Prosesleri:")
        table_label.setStyleSheet(f"""
            color: {self.colors['dark']};
            font-weight: bold;
            font-size: 16px;
        """)
        table_panel.addWidget(table_label)
        
        table_info = QLabel("Sağ tıklayarak prosesleri izlemeye alabilir veya kontrolünü yapabilirsiniz")
        table_info.setStyleSheet(f"""
            color: {self.colors['dark_alt']};
            font-style: italic;
            padding: 2px 5px;
            font-size: 13px;
        """)
        table_info.setAlignment(Qt.AlignRight)
        table_panel.addWidget(table_info)
        
        mid_panel.addLayout(table_panel)
        
        # Tablo renkleri ve stili
        table_style = f"""
            QTableWidget {{
                border: 2px solid #d1d5db;
                border-radius: 8px;
                alternate-background-color: {self.colors['table_alt']};
                gridline-color: #d1d5db;
                selection-background-color: {self.colors['primary']};
                selection-color: white;
                background-color: white;
                padding: 5px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }}
            QTableWidget QHeaderView::section {{
                background: linear-gradient(to bottom, {self.colors['table_header']} 0%, {self.colors['dark_alt']} 100%);
                color: black;
                padding: 8px;
                font-weight: bold;
                font-size: 14px;
                border: none;
                border-right: 1px solid #d1d5db;
            }}
            QTableWidget::item {{
                padding: 6px;
                font-size: 13px;
            }}
            QTableWidget::item:selected {{
                background-color: {self.colors['primary']};
                color: white;
            }}
        """
        
        # Proses tablosu
        self.process_table = QTableWidget(0, 5)
        self.process_table.setHorizontalHeaderLabels(["PID", "Ad", "Durum", "CPU %", "Bellek %"])
        self.process_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.process_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.process_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.process_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.process_table.customContextMenuRequested.connect(self.show_process_context_menu)
        self.process_table.setStyleSheet(table_style)
        self.process_table.setAlternatingRowColors(True)
        
        mid_panel.addWidget(self.process_table)
        
        # Sistem bilgileri 
        system_info_label = QLabel("Genel Sistem Bilgileri")
        system_info_label.setAlignment(Qt.AlignCenter)
        system_info_label.setStyleSheet(f"""
            color: {self.colors['dark']};
            font-size: 18px;
            font-weight: bold;
            font-family: 'Segoe UI', sans-serif;
            margin: 10px 0 8px 0;
            padding: 8px 15px;
            background: linear-gradient(90deg, {self.colors['primary']}20 0%, {self.colors['secondary']}20 100%);
            border-radius: 8px;
            border: 1px solid {self.colors['primary']}30;
            box-shadow: 0 3px 8px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        """)
        system_info_label.setMinimumHeight(40)  # Ensure consistent height
        mid_panel.addWidget(system_info_label)

        # CPU ve Bellek kullanım çubukları
        system_usage_layout = QHBoxLayout()
        system_usage_layout.setSpacing(10)  # Add spacing between CPU and Memory groups

        # CPU kullanımı
        cpu_group = QGroupBox("CPU Kullanımı")
        cpu_group.setStyleSheet(f"""
            QGroupBox {{
                background: linear-gradient(145deg, {self.colors['light']} 0%, #e6f0fa 85%, #ffffff 100%);
                border: 1px solid {self.colors['primary']}40;
                border-radius: 12px;
                margin-top: 8px;
                font-weight: bold;
                padding: 15px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08), 0 2px 4px rgba(0, 0, 0, 0.05);
                transition: all 0.3s ease;
            }}
            QGroupBox:hover {{
                background: linear-gradient(145deg, {self.colors['light']} 0%, #d0e7ff 75%, #f0f8ff 100%);
                box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12), 0 3px 6px rgba(0, 0, 0, 0.08);
                border: 1px solid {self.colors['primary']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 15px;
                padding: 6px 12px;
                background: linear-gradient(90deg, {self.colors['primary']} 0%, {self.colors['primary']}80 100%);
                color: white;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                margin-bottom: 12px;
            }}
        """)
        cpu_layout = QVBoxLayout()

        self.cpu_progress = QProgressBar()
        self.cpu_progress.setRange(0, 100)
        self.cpu_progress.setValue(0)
        self.cpu_progress.setFormat("%p%")
        self.cpu_progress.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {self.colors['primary']}30;
                border-radius: 8px;
                text-align: center;
                height: 30px;
                background-color: #f5f7fa;
                font-size: 14px;
                font-weight: bold;
                color: {self.colors['dark']};
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            }}
            QProgressBar::chunk {{
                background: linear-gradient(90deg, {self.colors['primary']} 0%, {self.colors['primary']}80 100%);
                border-radius: 6px;
            }}
            QProgressBar::text {{
                padding-bottom: 4px;  /* Lower the percentage text */
            }}
        """)
        cpu_layout.addWidget(self.cpu_progress)

        self.cpu_label = QLabel("CPU: 0.0%")
        self.cpu_label.setAlignment(Qt.AlignCenter)
        self.cpu_label.setStyleSheet(f"""
            color: {self.colors['dark']};
            font-weight: bold;
            font-size: 14px;
            margin-top: 5px;
        """)
        cpu_layout.addWidget(self.cpu_label)

        cpu_group.setLayout(cpu_layout)
        system_usage_layout.addWidget(cpu_group)

        # Bellek kullanımı
        memory_group = QGroupBox("Bellek Kullanımı")
        memory_group.setStyleSheet(f"""
            QGroupBox {{
                background: linear-gradient(145deg, {self.colors['light']} 0%, #e6f9e6 85%, #ffffff 100%);
                border: 1px solid {self.colors['secondary']}40;
                border-radius: 12px;
                margin-top: 8px;
                font-weight: bold;
                padding: 15px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08), 0 2px 4px rgba(0, 0, 0, 0.05);
                transition: all 0.3s ease;
            }}
            QGroupBox:hover {{
                background: linear-gradient(145deg, {self.colors['light']} 0%, #c9f0c9 75%, #f0fff0 100%);
                box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12), 0 3px 6px rgba(0, 0, 0, 0.08);
                border: 1px solid {self.colors['secondary']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 15px;
                padding: 6px 12px;
                background: linear-gradient(90deg, {self.colors['secondary']} 0%, {self.colors['secondary']}80 100%);
                color: white;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                margin-bottom: 12px;
            }}
        """)
        memory_layout = QVBoxLayout()

        self.memory_progress = QProgressBar()
        self.memory_progress.setRange(0, 100)
        self.memory_progress.setValue(0)
        self.memory_progress.setFormat("%p%")
        self.memory_progress.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {self.colors['secondary']}30;
                border-radius: 8px;
                text-align: center;
                height: 30px;
                background-color: #f5f7fa;
                font-size: 14px;
                font-weight: bold;
                color: {self.colors['dark']};
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            }}
            QProgressBar::chunk {{
                background: linear-gradient(90deg, {self.colors['secondary']} 0%, {self.colors['secondary']}80 100%);
                border-radius: 6px;
            }}
            QProgressBar::text {{
                padding-bottom: 4px;  /* Lower the percentage text */
            }}
        """)
        memory_layout.addWidget(self.memory_progress)

        self.memory_label = QLabel("Bellek: 0.0 GB / 0.0 GB")
        self.memory_label.setAlignment(Qt.AlignCenter)
        self.memory_label.setStyleSheet(f"""
            color: {self.colors['dark']};
            font-weight: bold;
            font-size: 14px;
            margin-top: 5px;
        """)
        memory_layout.addWidget(self.memory_label)

        memory_group.setLayout(memory_layout)
        system_usage_layout.addWidget(memory_group)

        mid_panel.addLayout(system_usage_layout)

        # Alt panel: Izlenen proseslerin grafikleri
        bottom_panel = QTabWidget()
        bottom_panel.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 2px solid {self.colors['primary']};
                background: white;
                border-radius: 8px;
                padding: 10px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }}
            QTabBar::tab {{
                background: #e5e7eb;
                color: {self.colors['dark']};
                padding: 10px 20px;
                margin-right: 4px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                border: 2px solid #d1d5db;
                font-weight: bold;
                font-size: 14px;
                transition: all 0.3s ease;
            }}
            QTabBar::tab:selected {{
                background: {self.colors['primary']};
                color: white;
                border-bottom: 2px solid {self.colors['primary']};
                border-top: 3px solid {self.colors['dark']};
            }}
            QTabBar::tab:hover:!selected {{
                background: #dbeafe;
                color: {self.colors['primary']};
                border-color: {self.colors['primary']};
            }}
        """)
        
        # CPU kullanımı sekmesi
        self.cpu_tab = QWidget()
        cpu_tab_layout = QVBoxLayout()
        
        cpu_chart_title = QLabel("CPU Kullanımı Zaman Serisi")
        cpu_chart_title.setAlignment(Qt.AlignCenter)
        cpu_chart_title.setStyleSheet(f"""
            color: {self.colors['dark']};
            font-size: 16px;
            font-weight: bold;
            margin: 10px 0;
            padding: 5px;
            background-color: {self.colors['light']};
            border-radius: 5px;
            border-left: 4px solid {self.colors['primary']};
        """)
        cpu_tab_layout.addWidget(cpu_chart_title)
        
        # CPU grafiği için canvas ve toolbar oluştur
        self.cpu_canvas = FigureCanvas(self.monitor.visualize_cpu_usage())
        self.cpu_canvas.setStyleSheet("""
            background-color: white;
            border-radius: 8px;
            padding: 10px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        """)
        
        # Navigation toolbar ekle
        cpu_toolbar = NavigationToolbar(self.cpu_canvas, self)
        cpu_toolbar.setStyleSheet("""
            QToolBar {
                background-color: #f3f4f6;
                border: 1px solid #d1d5db;
                border-radius: 5px;
                padding: 5px;
            }
            QToolButton {
                background-color: transparent;
                border: none;
                padding: 5px;
            }
            QToolButton:hover {
                background-color: #e5e7eb;
                border-radius: 3px;
            }
        """)
        cpu_tab_layout.addWidget(cpu_toolbar)
        cpu_tab_layout.addWidget(self.cpu_canvas, stretch=1)  # Stretch to fill available space
        
        cpu_chart_info = QLabel("Bu grafik, izlenen proseslerin zaman içerisindeki CPU kullanımlarını gösterir.")
        cpu_chart_info.setStyleSheet(f"""
            color: {self.colors['dark']};
            font-style: italic;
            padding: 8px;
            background-color: #f9fafb;
            border-radius: 5px;
            border-left: 4px solid {self.colors['primary']};
            font-size: 13px;
            margin-top: 10px;
        """)
        cpu_chart_info.setWordWrap(True)
        cpu_tab_layout.addWidget(cpu_chart_info)
        
        self.cpu_tab.setLayout(cpu_tab_layout)
        
        # Bellek kullanımı sekmesi
        self.memory_tab = QWidget()
        memory_tab_layout = QVBoxLayout()
        
        memory_chart_title = QLabel("Bellek Kullanımı Zaman Serisi")
        memory_chart_title.setAlignment(Qt.AlignCenter)
        memory_chart_title.setStyleSheet(f"""
            color: {self.colors['dark']};
            font-size: 16px;
            font-weight: bold;
            margin: 10px 0;
            padding: 5px;
            background-color: {self.colors['light']};
            border-radius: 5px;
            border-left: 4px solid {self.colors['secondary']};
        """)
        memory_tab_layout.addWidget(memory_chart_title)
        
        # Bellek grafiği için canvas ve toolbar oluştur
        self.memory_canvas = FigureCanvas(self.monitor.visualize_memory_usage())
        self.memory_canvas.setStyleSheet("""
            background-color: white;
            border-radius: 8px;
            padding: 10px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        """)
        
        # Navigation toolbar ekle
        memory_toolbar = NavigationToolbar(self.memory_canvas, self)
        memory_toolbar.setStyleSheet("""
            QToolBar {
                background-color: #f3f4f6;
                border: 1px solid #d1d5db;
                border-radius: 5px;
                padding: 5px;
            }
            QToolButton {
                background-color: transparent;
                border: none;
                padding: 5px;
            }
            QToolButton:hover {
                background-color: #e5e7eb;
                border-radius: 3px;
            }
        """)
        memory_tab_layout.addWidget(memory_toolbar)
        memory_tab_layout.addWidget(self.memory_canvas, stretch=1)  # Stretch to fill available space
        
        memory_chart_info = QLabel("Bu grafik, izlenen proseslerin zaman içerisindeki bellek kullanımlarını gösterir.")
        memory_chart_info.setStyleSheet(f"""
            color: {self.colors['dark']};
            font-style: italic;
            padding: 8px;
            background-color: #f9fafb;
            border-radius: 5px;
            border-left: 4px solid {self.colors['secondary']};
            font-size: 13px;
            margin-top: 10px;
        """)
        memory_chart_info.setWordWrap(True)
        memory_tab_layout.addWidget(memory_chart_info)
        
        self.memory_tab.setLayout(memory_tab_layout)
        
        # Sekmeleri alt panele ekle
        bottom_panel.addTab(self.cpu_tab, "CPU Kullanımı")
        bottom_panel.addTab(self.memory_tab, "Bellek Kullanımı")
        
        # Ana düzene panelleri ekle
        main_layout.addLayout(top_panel)
        main_layout.addLayout(mid_panel, 2)  # Orta panel daha fazla yer kaplasın
        main_layout.addWidget(bottom_panel, 3)  # Alt panel daha fazla yer kaplasın
        
        # Ana düzeni pencereye uygula
        self.setLayout(main_layout)
        
        # İlk proses listesini yükle
        self.update_process_list()
        self.update_system_info()
    
    def start_process(self):
        """Yeni bir proses başlatır"""
        command = self.command_edit.text()
        
        if not command:
            self.show_message("Hata", "Lütfen bir komut girin.", QMessageBox.Warning)
            return
        
        # Prosesi başlat
        success, result = self.controller.start_process(command)
        
        if success:
            # Başarılı mesajı göster
            self.show_message("Başarılı", f"Proses başlatıldı (PID: {result}).", QMessageBox.Information)
            
            # Listeyi güncelle
            self.update_process_list()
            
            # İzleme başlatılmışsa, yeni prosesi izlemeye al
            if self.monitoring_active:
                self.monitor.add_process(result)
                self.update_charts()
        else:
            # Hata mesajı göster
            self.show_message("Hata", f"Proses başlatılamadı: {result}", QMessageBox.Warning)
    
    def start_monitoring(self):
        """Proses izlemeyi başlatır"""
        interval = self.refresh_interval_spin.value()
        
        # İzlemeyi başlat
        self.monitor.start_monitoring(interval)
        self.monitoring_active = True
        
        # Zamanlayıcıyı başlat
        self.update_timer.start(interval * 1000)
        
        # Arayüz durumunu güncelle
        self.start_monitoring_button.setEnabled(False)
        self.stop_monitoring_button.setEnabled(True)
        self.monitoring_status_label.setText(f"İzleme aktif ({interval} saniye aralıkla)")
        self.monitoring_status_label.setStyleSheet(f"""
            color: white;
            padding: 8px;
            border-radius: 5px;
            font-weight: bold;
            font-size: 14px;
            background-color: {self.colors['success']};
            text-align: center;
            margin-top: 8px;
            transition: all 0.3s ease;
        """)
        
        # Grafikleri güncelle
        self.update_charts()
    
    def stop_monitoring(self):
        """Proses izlemeyi durdurur"""
        # İzlemeyi durdur
        self.monitor.stop_monitoring()
        self.monitoring_active = False
        
        # Zamanlayıcıyı durdur
        self.update_timer.stop()
        
        # Arayüz durumunu güncelle
        self.start_monitoring_button.setEnabled(True)
        self.stop_monitoring_button.setEnabled(False)
        self.monitoring_status_label.setText("İzleme durduruldu")
        self.monitoring_status_label.setStyleSheet(f"""
            color: white;
            padding: 8px;
            border-radius: 5px;
            font-weight: bold;
            font-size: 14px;
            background-color: {self.colors['accent']};
            text-align: center;
            margin-top: 8px;
            transition: all 0.3s ease;
        """)
    
    def start_monitoring_if_needed(self):
        """Sekme görünür olduğunda, eğer izleme aktif değilse başlatır"""
        if not self.monitoring_active:
            self.start_monitoring()
    
    def refresh_now(self):
        """Proses listesini ve grafikleri hemen günceller"""
        self.update_process_list()
        self.update_charts()
        self.update_system_info()
        
        # Kullanıcıya bildirim
        self.show_status_message("Veriler güncellendi", "info")
    
    def update_system_info(self):
        """Sistem CPU ve bellek bilgilerini günceller"""
        # CPU kullanımı
        cpu_percent = psutil.cpu_percent()
        self.cpu_progress.setValue(int(cpu_percent))
        self.cpu_label.setText(f"CPU: {cpu_percent:.1f}%")
        
        # CPU ilerleme çubuğunu renklendirme
        if cpu_percent < 30:
            style = f"""
                QProgressBar::chunk {{
                    background-color: {self.colors['secondary']};
                }}
            """
        elif cpu_percent < 70:
            style = f"""
                QProgressBar::chunk {{
                    background-color: {self.colors['warning']};
                }}
            """
        else:
            style = f"""
                QProgressBar::chunk {{
                    background-color: {self.colors['accent']};
                }}
            """
        self.cpu_progress.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid #d1d5db;
                border-radius: 5px;
                text-align: center;
                height: 25px;
                background-color: white;
                font-size: 14px;
                font-weight: bold;
            }}
            {style}
        """)
        
        # Bellek kullanımı
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        total_gb = memory.total / (1024 ** 3)
        used_gb = memory.used / (1024 ** 3)
        
        self.memory_progress.setValue(int(memory_percent))
        self.memory_label.setText(f"Bellek: {used_gb:.1f} GB / {total_gb:.1f} GB")
        
        # Bellek ilerleme çubuğunu renklendirme
        if memory_percent < 30:
            style = f"""
                QProgressBar::chunk {{
                    background-color: {self.colors['secondary']};
                }}
            """
        elif memory_percent < 70:
            style = f"""
                QProgressBar::chunk {{
                    background-color: {self.colors['warning']};
                }}
            """
        else:
            style = f"""
                QProgressBar::chunk {{
                    background-color: {self.colors['accent']};
                }}
            """
        self.memory_progress.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid #d1d5db;
                border-radius: 5px;
                text-align: center;
                height: 25px;
                background-color: white;
                font-size: 14px;
                font-weight: bold;
            }}
            {style}
        """)
    
    def update_process_list(self):
        """Proses listesini günceller"""
        # Sistemdeki prosesleri al
        system_processes = self.monitor.get_system_processes(sort_by='cpu_percent', limit=50)
        
        # Tabloyu temizle
        self.process_table.setRowCount(0)
        
        # Proses verilerini tabloya ekle
        for i, proc in enumerate(system_processes):
            row_position = self.process_table.rowCount()
            self.process_table.insertRow(row_position)
            
            # PID
            pid_item = QTableWidgetItem(str(proc['pid']))
            pid_item.setData(Qt.UserRole, proc['pid'])  # PID'yi veri olarak sakla
            self.process_table.setItem(row_position, 0, pid_item)
            
            # Ad
            name_item = QTableWidgetItem(proc['name'])
            self.process_table.setItem(row_position, 1, name_item)
            
            # Durum
            status_item = QTableWidgetItem(proc['status'])
            
            # Duruma göre renklendirme
            if proc['status'] == 'running':
                status_item.setBackground(QColor(self.colors['low_usage']))
                status_item.setForeground(QColor(self.colors['success']))
                status_item.setText('Çalışıyor')
            elif proc['status'] == 'sleeping':
                status_item.setBackground(QColor(self.colors['light_alt']))
                status_item.setText('Uyuyor')
            elif proc['status'] == 'stopped':
                status_item.setBackground(QColor(self.colors['medium_usage']))
                status_item.setForeground(QColor(self.colors['warning']))
                status_item.setText('Durduruldu')
            else:
                status_item.setBackground(QColor(self.colors['high_usage']))
                status_item.setForeground(QColor(self.colors['accent']))
                
            self.process_table.setItem(row_position, 2, status_item)
            
            # CPU %
            cpu_value = proc['cpu_percent']
            cpu_item = QTableWidgetItem(f"{cpu_value:.1f}")
            
            # Yüksek CPU kullanımı için renklendirme
            if cpu_value > 50:
                cpu_item.setBackground(QColor(self.colors['high_usage']))
                cpu_item.setForeground(QColor(self.colors['accent']))
                cpu_item.setFont(QFont("", -1, QFont.Bold))
            elif cpu_value > 20:
                cpu_item.setBackground(QColor(self.colors['medium_usage']))
                cpu_item.setForeground(QColor(self.colors['warning']))
            else:
                cpu_item.setBackground(QColor(self.colors['low_usage']))
                
            self.process_table.setItem(row_position, 3, cpu_item)
            
            # Bellek %
            memory_value = proc['memory_percent']
            memory_item = QTableWidgetItem(f"{memory_value:.1f}")
            
            # Yüksek bellek kullanımı için renklendirme
            if memory_value > 10:
                memory_item.setBackground(QColor(self.colors['medium_usage']))
                memory_item.setForeground(QColor(self.colors['warning']))
            elif memory_value > 5:
                memory_item.setBackground(QColor(self.colors['low_usage']))
                memory_item.setForeground(QColor(self.colors['dark']))
            
            self.process_table.setItem(row_position, 4, memory_item)
            
            # İzlenen prosesleri vurgula
            if self.monitoring_active and proc['pid'] in self.monitor.monitored_processes:
                for col in range(5):
                    item = self.process_table.item(row_position, col)
                    item.setFont(QFont("", -1, QFont.Bold))
                    # Monitör edilen satırı hafif bir renk değişimiyle belirt
                    item.setBackground(QColor("#e3f2fd"))  # Açık mavi arka plan
        
        # Sistem bilgilerini güncelle
        self.update_system_info()
    
    def update_charts(self):
        """CPU ve bellek kullanım grafiklerini günceller"""
        if self.monitoring_active:
            # CPU grafiğini güncelle
            self.cpu_canvas.figure = self.monitor.visualize_cpu_usage()
            self.cpu_canvas.draw()
            
            # Bellek grafiğini güncelle
            self.memory_canvas.figure = self.monitor.visualize_memory_usage()
            self.memory_canvas.draw()
    
    def show_process_context_menu(self, position):
        """
        Proses tablosunda sağ tıklama menüsünü gösterir
        
        Parametreler:
        position (QPoint): Fare konumu
        """
        # Seçili satırı al
        selected_rows = self.process_table.selectionModel().selectedRows()
        
        if not selected_rows:
            return
        
        # Seçili satırdaki PID'yi al
        pid_item = self.process_table.item(selected_rows[0].row(), 0)
        pid = pid_item.data(Qt.UserRole)
        
        # Sağ tıklama menüsü oluştur
        context_menu = QMenu(self)
        context_menu.setStyleSheet(f"""
            QMenu {{
                background-color: white;
                border: 2px solid #d1d5db;
                border-radius: 6px;
                padding: 5px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }}
            QMenu::item {{
                padding: 8px 30px;
                color: {self.colors['dark']};
                font-size: 14px;
            }}
            QMenu::item:selected {{
                background-color: {self.colors['primary']};
                color: white;
                border-radius: 4px;
            }}
            QMenu::separator {{
                height: 1px;
                background-color: #d1d5db;
                margin: 5px 0;
            }}
        """)
        
        # İzleme durumuna göre menü öğelerini ekle
        if pid in self.monitor.monitored_processes:
            remove_action = context_menu.addAction("İzlemeyi Durdur")
            remove_action.setIcon(QIcon())
            remove_action.triggered.connect(lambda: self.remove_from_monitoring(pid))
        else:
            add_action = context_menu.addAction("İzlemeye Al")
            add_action.setIcon(QIcon())
            add_action.triggered.connect(lambda: self.add_to_monitoring(pid))
        
        # Proses kontrolü için menü öğelerini ekle
        context_menu.addSeparator()
        
        stop_action = context_menu.addAction("Durdur")
        stop_action.setIcon(QIcon())
        stop_action.triggered.connect(lambda: self.stop_process(pid))
        
        context_menu.addSeparator()
        
        priority_menu = context_menu.addMenu("Öncelik Değiştir")
        priority_menu.setStyleSheet(f"""
            QMenu {{
                background-color: white;
                border: 2px solid #d1d5db;
                border-radius: 6px;
                padding: 5px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }}
            QMenu::item {{
                padding: 8px 30px;
                color: {self.colors['dark']};
                font-size: 14px;
            }}
            QMenu::item:selected {{
                background-color: {self.colors['primary']};
                color: white;
                border-radius: 4px;
            }}
        """)
        
        low_action = priority_menu.addAction("Düşük")
        low_action.triggered.connect(lambda: self.change_priority(pid, "low"))
        
        normal_action = priority_menu.addAction("Normal")
        normal_action.triggered.connect(lambda: self.change_priority(pid, "normal"))
        
        high_action = priority_menu.addAction("Yüksek")
        high_action.triggered.connect(lambda: self.change_priority(pid, "high"))
        
        # Detaylı bilgi
        context_menu.addSeparator()
        
        info_action = context_menu.addAction("Detaylı Bilgi")
        info_action.triggered.connect(lambda: self.show_process_info(pid))
        
        # Menüyü göster
        context_menu.exec_(QCursor.pos())
    
    def add_to_monitoring(self, pid):
        """
        Bir prosesi izlemeye alır
        
        Parametreler:
        pid (int): Proses ID
        """
        if not self.monitoring_active:
            # İzleme aktif değilse başlat
            self.start_monitoring()
        
        # Prosesi izlemeye al
        success = self.monitor.add_process(pid)
        
        if success:
            # Listeyi ve grafikleri güncelle
            self.update_process_list()
            self.update_charts()
            
            # Başarılı mesajı göster
            self.show_message("Başarılı", f"Proses {pid} izlemeye alındı.", QMessageBox.Information)
        else:
            # Hata mesajı göster
            self.show_message("Hata", f"Proses {pid} izlemeye alınamadı.", QMessageBox.Warning)
    
    def remove_from_monitoring(self, pid):
        """
        Bir prosesi izlemeden çıkarır
        
        Parametreler:
        pid (int): Proses ID
        """
        # Prosesi izlemeden çıkar
        self.monitor.remove_process(pid)
        
        # Listeyi ve grafikleri güncelle
        self.update_process_list()
        self.update_charts()
        
        # Başarılı mesajı göster
        self.show_message("Başarılı", f"Proses {pid} izlemeden çıkarıldı.", QMessageBox.Information)
    
    def stop_process(self, pid):
        """
        Bir prosesi durdurur
        
        Parametreler:
        pid (int): Proses ID
        """
        # Onay mesajı göster
        reply = QMessageBox.question(
            self, 
            "Proses Durdurma", 
            f"Proses {pid} durdurmak istediğinizden emin misiniz?",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Prosesi durdur
            success, message = self.controller.stop_process(pid)
            
            if success:
                # İzleniyorsa, izlemeden çıkar
                if pid in self.monitor.monitored_processes:
                    self.monitor.remove_process(pid)
                
                # Listeyi ve grafikleri güncelle
                self.update_process_list()
                self.update_charts()
                
                # Başarılı mesajı göster
                self.show_message("Başarılı", message, QMessageBox.Information)
            else:
                # Hata mesajı göster
                self.show_message("Hata", message, QMessageBox.Warning)
    
    def change_priority(self, pid, priority):
        """
        Bir prosesin önceliğini değiştirir
        
        Parametreler:
        pid (int): Proses ID
        priority (str): Yeni öncelik ('low', 'normal', 'high')
        """
        # Prosesi önceliğini değiştir
        success, message = self.controller.change_priority(pid, priority)
        
        if success:
            # Listeyi güncelle
            self.update_process_list()
            
            # Başarılı mesajı göster
            self.show_message("Başarılı", message, QMessageBox.Information)
        else:
            # Hata mesajı göster
            self.show_message("Hata", message, QMessageBox.Warning)
    
    def show_process_info(self, pid):
        """
        Bir proses hakkında detaylı bilgileri gösterir
        
        Parametreler:
        pid (int): Proses ID
        """
        # Proses bilgilerini al
        process_info = self.controller.get_process_info(pid)
        
        if process_info:
            # Bilgileri biçimlendir
            info_text = f"""
            <div style="background-color: {self.colors['light']}; padding: 20px; border-radius: 8px; border: 2px solid #d1d5db; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);">
                <h2 style="color: {self.colors['primary']}; text-align: center; margin: 0 0 15px 0;">Proses Detayları (PID: {pid})</h2>
                <hr style="border: 0; height: 1px; background-color: #d1d5db; margin: 15px 0;">
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; grid-gap: 15px;">
                    <div style="background-color: white; padding: 15px; border-radius: 6px; border: 1px solid #e5e7eb;">
                        <p><b style="color: {self.colors['dark']};">Ad:</b> {process_info['name']}</p>
                        <p><b style="color: {self.colors['dark']};">Durum:</b> <span style="color: {self.get_status_color(process_info['status'])};">{process_info['status']}</span></p>
                        <p><b style="color: {self.colors['dark']};">Kullanıcı:</b> {process_info['username']}</p>
                        <p><b style="color: {self.colors['dark']};">CPU Kullanımı:</b> <span style="color: {self.get_usage_color(process_info['cpu_percent'])};">{process_info['cpu_percent']:.2f}%</span></p>
                    </div>
                    
                    <div style="background-color: white; padding: 15px; border-radius: 6px; border: 1px solid #e5e7eb;">
                        <p><b style="color: {self.colors['dark']};">Bellek Kullanımı:</b> <span style="color: {self.get_usage_color(process_info['memory_percent'])};">{process_info['memory_percent']:.2f}%</span></p>
                        <p><b style="color: {self.colors['dark']};">Öncelik:</b> {process_info['priority']}</p>
                        <p><b style="color: {self.colors['dark']};">Başlangıç Zamanı:</b> {process_info['create_time']}</p>
                        <p><b style="color: {self.colors['dark']};">İş Parçacığı Sayısı:</b> {process_info['num_threads']}</p>
                    </div>
                </div>
                
                <div style="background-color: white; margin-top: 15px; padding: 15px; border-radius: 6px; border: 1px solid #e5e7eb;">
                    <p><b style="color: {self.colors['dark']};">Komut Satırı:</b></p>
                    <p style="background-color: #f3f4f6; padding: 8px; border-radius: 5px; font-family: monospace; overflow-x: auto; max-width: 100%; word-wrap: break-word;">
                        {" ".join(process_info['cmdline'] if process_info['cmdline'] else ["N/A"])}
                    </p>
                </div>
            </div>
            """
            
            # Bilgi iletişim kutusunu göster
            info_box = QMessageBox(self)
            info_box.setIcon(QMessageBox.Information)
            info_box.setWindowTitle(f"Proses {pid} Bilgileri")
            info_box.setText(info_text)
            info_box.setStyleSheet(f"""
                QMessageBox {{
                    background-color: white;
                }}
                QPushButton {{
                    background-color: {self.colors['primary']};
                    color: white;
                    padding: 8px 20px;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 14px;
                    min-width: 100px;
                    transition: all 0.3s ease;
                }}
                QPushButton:hover {{
                    background-color: #2980b9;
                    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
                }}
            """)
            info_box.exec_()
        else:
            # Hata mesajı göster
            self.show_message("Hata", f"Proses {pid} bilgileri alınamadı.", QMessageBox.Warning)
    
    def get_status_color(self, status):
        """Proses durumuna göre renk döndürür"""
        if status == 'running':
            return self.colors['success']
        elif status == 'sleeping':
            return self.colors['primary']
        elif status == 'stopped':
            return self.colors['warning']
        else:
            return self.colors['accent']
    
    def get_usage_color(self, usage):
        """Kullanım değerine göre renk döndürür"""
        if usage < 20:
            return self.colors['success']
        elif usage < 50:
            return self.colors['warning']
        else:
            return self.colors['accent']
    
    def show_message(self, title, message, icon=QMessageBox.Information):
        """
        Özelleştirilmiş mesaj kutusu gösterir
        
        Parametreler:
        title (str): Başlık
        message (str): Mesaj
        icon (QMessageBox.Icon): İkon tipi
        """
        msg_box = QMessageBox(self)
        msg_box.setIcon(icon)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        
        # İkon tipine göre stil belirle
        if icon == QMessageBox.Warning or icon == QMessageBox.Critical:
            button_color = self.colors['accent']
        else:
            button_color = self.colors['primary']
        
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: white;
                border: 2px solid #d1d5db;
                border-radius: 8px;
                padding: 10px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }}
            QPushButton {{
                background-color: {button_color};
                color: white;
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
                min-width: 100px;
                transition: all 0.3s ease;
            }}
            QPushButton:hover {{
                background-color: {"#c0392b" if button_color == self.colors['accent'] else "#2980b9"};
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
            }}
        """)
        
        msg_box.exec_()
    
    def show_status_message(self, message, type="info"):
        """
        Durumu günceller ve geçici bir mesaj gösterir
        
        Parametreler:
        message (str): Gösterilecek mesaj
        type (str): Mesaj tipi ('info', 'success', 'warning', 'error')
        """
        # Üst pencereyi bul
        main_window = self.window()
        if hasattr(main_window, 'status_label'):
            status_label = main_window.status_label
            
            # Mesaj tipine göre stili ayarla
            if type == "success":
                style = f"color: {self.colors['secondary']}; font-weight: bold;"
            elif type == "warning":
                style = f"color: {self.colors['warning']}; font-weight: bold;"
            elif type == "error":
                style = f"color: {self.colors['accent']}; font-weight: bold;"
            else:  # info
                style = f"color: {self.colors['primary']}; font-weight: bold;"
            
            # Durumu güncelle
            status_label.setStyleSheet(style)
            status_label.setText(message)