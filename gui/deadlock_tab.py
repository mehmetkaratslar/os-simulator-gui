# -*- coding: utf-8 -*-
"""
Deadlock Yonetim Sekmesi
Kaynak tahsis grafi ve Banker's algoritmasi ile deadlock yonetimi.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTableWidget, QTableWidgetItem,
                           QGroupBox, QSpinBox, QFormLayout, QTabWidget,
                           QMessageBox, QHeaderView, QLineEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from deadlock_manager.detector import DeadlockDetector
from deadlock_manager.bankers import BankersAlgorithm

class DeadlockManagerTab(QWidget):
    """Deadlock yonetim sekmesi"""
    
    def __init__(self):
        """Deadlock yonetim sekmesini baslat"""
        super().__init__()
        
        # Deadlock algilayici ve Banker's algoritmasi
        self.detector = DeadlockDetector()
        self.bankers = BankersAlgorithm()
        
        # Renk paleti
        self.colors = {
            "primary": "#FF00FFFF",    # Mavi
            "secondary": "#2ecc71",  # Yeşil
            "accent": "#F42710FF",     # Kırmızı
            "warning": "#F99B05FF",    # Turuncu
            "info": "#9b59b6",       # Mor
            "light": "#ecf0f1",      # Açık gri
            "dark": "#34495e",       # Koyu lacivert
            "table_header": "#2c3e50", # Koyu mavi
            "table_alt": "#f9f9f9"   # Açık beyaz
        }
        
        # Arayuzu olustur
        self.init_ui()
    
    def init_ui(self):
        """Kullanici arayuzunu olusturur"""
        # Ana duzen
        main_layout = QVBoxLayout()
        
        # Baslik
        title_label = QLabel("Deadlock Algilama ve Yonetim Sistemi")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(
            "color: {}; font-size: 18px; font-weight: bold; margin: 10px 0; padding: 5px; background-color: {}; border-radius: 5px; border-bottom: 3px solid {};".format(self.colors['dark'], self.colors['light'], self.colors['primary'])
        )
        main_layout.addWidget(title_label)
        
        # Ust kisim: Deadlock Algilama ve Banker's Algoritmasi sekmeleri
        top_tabs = QTabWidget()
        top_tabs.setStyleSheet(
            "QTabWidget::pane {{ border: 1px solid {}; background: {}; border-radius: 5px; }} QTabBar::tab {{ background: #e0e0e0; color: {}; padding: 8px 15px; margin-right: 2px; border-top-left-radius: 4px; border-top-right-radius: 4px; border: 1px solid #cccccc; font-weight: bold; }} QTabBar::tab:selected {{ background: {}; color: white; border-bottom-color: {}; }} QTabBar::tab:hover:!selected {{ background: #e8f6fe; }}".format(self.colors['primary'], self.colors['light'], self.colors['dark'], self.colors['primary'], self.colors['primary'])
        )
        
        # 1. Sekme: Deadlock Algilama
        self.detection_tab = QWidget()
        detection_layout = QVBoxLayout()
        
        # Bilgi etiketi
        info_label = QLabel("""
        <b>Deadlock Algilama Modulu:</b> Kaynak tahsis grafi kullanarak deadlock durumlarini tespit eder.
        Prosesler ve kaynaklar ekleyerek, aralarindaki tahsis ve talep iliskilerini modelleyebilirsiniz.
        """)
        info_label.setStyleSheet(
            "color: {}; padding: 8px; background-color: #f8f9fa; border-radius: 5px; border-left: 5px solid {}; margin-bottom: 10px;".format(self.colors['dark'], self.colors['info'])
        )
        info_label.setWordWrap(True)
        detection_layout.addWidget(info_label)
        
        # Kaynak ve proses ekleme paneli
        resource_process_panel = QHBoxLayout()
        
        # Kaynak ekleme formu
        resource_form_group = QGroupBox("Kaynak Ekle")
        resource_form_group.setStyleSheet(
            "QGroupBox {{ background-color: {}; border: 1px solid {}; border-radius: 5px; margin-top: 15px; font-weight: bold; }} QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 5px; color: {}; }}".format(self.colors['light'], self.colors['secondary'], self.colors['secondary'])
        )
        resource_form_layout = QFormLayout()
        
        self.resource_id_spin = QSpinBox()
        self.resource_id_spin.setRange(1, 100)
        self.resource_id_spin.setStyleSheet(
            "QSpinBox {{ border: 1px solid #bdc3c7; padding: 5px; border-radius: 3px; background-color: white; }} QSpinBox:focus {{ border: 1px solid {}; }}".format(self.colors['secondary'])
        )
        resource_id_label = QLabel("Kaynak ID:")
        resource_id_label.setStyleSheet("font-weight: bold; color: {};".format(self.colors['dark']))
        resource_form_layout.addRow(resource_id_label, self.resource_id_spin)
        
        self.resource_instances_spin = QSpinBox()
        self.resource_instances_spin.setRange(1, 100)
        self.resource_instances_spin.setStyleSheet(
            "QSpinBox {{ border: 1px solid #bdc3c7; padding: 5px; border-radius: 3px; background-color: white; }} QSpinBox:focus {{ border: 1px solid {}; }}".format(self.colors['secondary'])
        )
        resource_instances_label = QLabel("Ornek Sayisi:")
        resource_instances_label.setStyleSheet("font-weight: bold; color: {};".format(self.colors['dark']))
        resource_form_layout.addRow(resource_instances_label, self.resource_instances_spin)
        
        self.add_resource_button = QPushButton("Kaynak Ekle")
        self.add_resource_button.setStyleSheet(
            "QPushButton {{ background-color: {}; color: white; padding: 8px 15px; border-radius: 4px; font-weight: bold; border: none; }} QPushButton:hover {{ background-color: #27ae60; }} QPushButton:pressed {{ background-color: #1e8449; }}".format(self.colors['secondary'])
        )
        self.add_resource_button.clicked.connect(self.add_resource)
        resource_form_layout.addRow(self.add_resource_button)
        
        resource_form_group.setLayout(resource_form_layout)
        
        # Proses ekleme formu
        process_form_group = QGroupBox("Proses Ekle")
        process_form_group.setStyleSheet(
            "QGroupBox {{ background-color: {}; border: 1px solid {}; border-radius: 5px; margin-top: 15px; font-weight: bold; }} QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 5px; color: {}; }}".format(self.colors['light'], self.colors['primary'], self.colors['primary'])
        )
        process_form_layout = QFormLayout()
        
        self.process_id_spin = QSpinBox()
        self.process_id_spin.setRange(1, 100)
        self.process_id_spin.setStyleSheet(
            "QSpinBox {{ border: 1px solid #bdc3c7; padding: 5px; border-radius: 3px; background-color: white; }} QSpinBox:focus {{ border: 1px solid {}; }}".format(self.colors['primary'])
        )
        process_id_label = QLabel("Proses ID:")
        process_id_label.setStyleSheet("font-weight: bold; color: {};".format(self.colors['dark']))
        process_form_layout.addRow(process_id_label, self.process_id_spin)
        
        self.add_process_button = QPushButton("Proses Ekle")
        self.add_process_button.setStyleSheet(
            "QPushButton {{ background-color: {}; color: white; padding: 8px 15px; border-radius: 4px; font-weight: bold; border: none; }} QPushButton:hover {{ background-color: #2980b9; }} QPushButton:pressed {{ background-color: #1c5a85; }}".format(self.colors['primary'])
        )
        self.add_process_button.clicked.connect(self.add_process)
        process_form_layout.addRow(self.add_process_button)
        
        process_form_group.setLayout(process_form_layout)
        
        # Kaynak ve proses formlarini panele ekle
        resource_process_panel.addWidget(resource_form_group)
        resource_process_panel.addWidget(process_form_group)
        
        # Kaynak tahsisi ve talebi paneli
        allocation_request_panel = QHBoxLayout()
        
        # Kaynak tahsisi formu
        allocation_form_group = QGroupBox("Kaynak Tahsisi")
        allocation_form_group.setStyleSheet(
            "QGroupBox {{ background-color: {}; border: 1px solid {}; border-radius: 5px; margin-top: 15px; font-weight: bold; }} QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 5px; color: {}; }}".format(self.colors['light'], self.colors['primary'], self.colors['primary'])
        )
        allocation_form_layout = QFormLayout()
        
        self.allocation_process_spin = QSpinBox()
        self.allocation_process_spin.setRange(1, 100)
        self.allocation_process_spin.setStyleSheet(
            "QSpinBox {{ border: 1px solid #bdc3c7; padding: 5px; border-radius: 3px; background-color: white; }} QSpinBox:focus {{ border: 1px solid {}; }}".format(self.colors['primary'])
        )
        allocation_process_label = QLabel("Proses ID:")
        allocation_process_label.setStyleSheet("font-weight: bold; color: {};".format(self.colors['dark']))
        allocation_form_layout.addRow(allocation_process_label, self.allocation_process_spin)
        
        self.allocation_resource_spin = QSpinBox()
        self.allocation_resource_spin.setRange(1, 100)
        self.allocation_resource_spin.setStyleSheet(
            "QSpinBox {{ border: 1px solid #bdc3c7; padding: 5px; border-radius: 3px; background-color: white; }} QSpinBox:focus {{ border: 1px solid {}; }}".format(self.colors['primary'])
        )
        allocation_resource_label = QLabel("Kaynak ID:")
        allocation_resource_label.setStyleSheet("font-weight: bold; color: {};".format(self.colors['dark']))
        allocation_form_layout.addRow(allocation_resource_label, self.allocation_resource_spin)
        
        self.allocation_instances_spin = QSpinBox()
        self.allocation_instances_spin.setRange(1, 100)
        self.allocation_instances_spin.setStyleSheet(
            "QSpinBox {{ border: 1px solid #bdc3c7; padding: 5px; border-radius: 3px; background-color: white; }} QSpinBox:focus {{ border: 1px solid {}; }}".format(self.colors['primary'])
        )
        allocation_instances_label = QLabel("Ornek Sayisi:")
        allocation_instances_label.setStyleSheet("font-weight: bold; color: {};".format(self.colors['dark']))
        allocation_form_layout.addRow(allocation_instances_label, self.allocation_instances_spin)
        
        self.allocate_button = QPushButton("Tahsis Et")
        self.allocate_button.setStyleSheet(
            "QPushButton {{ background-color: {}; color: white; padding: 8px 15px; border-radius: 4px; font-weight: bold; border: none; }} QPushButton:hover {{ background-color: #2980b9; }} QPushButton:pressed {{ background-color: #1c5a85; }}".format(self.colors['primary'])
        )
        self.allocate_button.clicked.connect(self.allocate_resource)
        allocation_form_layout.addRow(self.allocate_button)
        
        allocation_form_group.setLayout(allocation_form_layout)
        
        # Kaynak talebi formu
        request_form_group = QGroupBox("Kaynak Talebi")
        request_form_group.setStyleSheet(
            "QGroupBox {{ background-color: {}; border: 1px solid {}; border-radius: 5px; margin-top: 15px; font-weight: bold; }} QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 5px; color: {}; }}".format(self.colors['light'], self.colors['warning'], self.colors['warning'])
        )
        request_form_layout = QFormLayout()
        
        self.request_process_spin = QSpinBox()
        self.request_process_spin.setRange(1, 100)
        self.request_process_spin.setStyleSheet(
            "QSpinBox {{ border: 1px solid #bdc3c7; padding: 5px; border-radius: 3px; background-color: white; }} QSpinBox:focus {{ border: 1px solid {}; }}".format(self.colors['warning'])
        )
        request_process_label = QLabel("Proses ID:")
        request_process_label.setStyleSheet("font-weight: bold; color: {};".format(self.colors['dark']))
        request_form_layout.addRow(request_process_label, self.request_process_spin)
        
        self.request_resource_spin = QSpinBox()
        self.request_resource_spin.setRange(1, 100)
        self.request_resource_spin.setStyleSheet(
            "QSpinBox {{ border: 1px solid #bdc3c7; padding: 5px; border-radius: 3px; background-color: white; }} QSpinBox:focus {{ border: 1px solid {}; }}".format(self.colors['warning'])
        )
        request_resource_label = QLabel("Kaynak ID:")
        request_resource_label.setStyleSheet("font-weight: bold; color: {};".format(self.colors['dark']))
        request_form_layout.addRow(request_resource_label, self.request_resource_spin)
        
        self.request_instances_spin = QSpinBox()
        self.request_instances_spin.setRange(1, 100)
        self.request_instances_spin.setStyleSheet(
            "QSpinBox {{ border: 1px solid #bdc3c7; padding: 5px; border-radius: 3px; background-color: white; }} QSpinBox:focus {{ border: 1px solid {}; }}".format(self.colors['warning'])
        )
        request_instances_label = QLabel("Ornek Sayisi:")
        request_instances_label.setStyleSheet("font-weight: bold; color: {};".format(self.colors['dark']))
        request_form_layout.addRow(request_instances_label, self.request_instances_spin)
        
        self.request_button = QPushButton("Talep Et")
        self.request_button.setStyleSheet(
            "QPushButton {{ background-color: {}; color: white; padding: 8px 15px; border-radius: 4px; font-weight: bold; border: none; }} QPushButton:hover {{ background-color: #e67e22; }} QPushButton:pressed {{ background-color: #d35400; }}".format(self.colors['warning'])
        )
        self.request_button.clicked.connect(self.request_resource)
        request_form_layout.addRow(self.request_button)
        
        request_form_group.setLayout(request_form_layout)
        
        # Kaynak serbest birakma formu
        release_form_group = QGroupBox("Kaynak Serbest Birakma")
        release_form_group.setStyleSheet(
            "QGroupBox {{ background-color: {}; border: 1px solid {}; border-radius: 5px; margin-top: 15px; font-weight: bold; }} QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 5px; color: {}; }}".format(self.colors['light'], self.colors['secondary'], self.colors['secondary'])
        )
        release_form_layout = QFormLayout()
        
        self.release_process_spin = QSpinBox()
        self.release_process_spin.setRange(1, 100)
        self.release_process_spin.setStyleSheet(
            "QSpinBox {{ border: 1px solid #bdc3c7; padding: 5px; border-radius: 3px; background-color: white; }} QSpinBox:focus {{ border: 1px solid {}; }}".format(self.colors['secondary'])
        )
        release_process_label = QLabel("Proses ID:")
        release_process_label.setStyleSheet("font-weight: bold; color: {};".format(self.colors['dark']))
        release_form_layout.addRow(release_process_label, self.release_process_spin)
        
        self.release_resource_spin = QSpinBox()
        self.release_resource_spin.setRange(1, 100)
        self.release_resource_spin.setStyleSheet(
            "QSpinBox {{ border: 1px solid #bdc3c7; padding: 5px; border-radius: 3px; background-color: white; }} QSpinBox:focus {{ border: 1px solid {}; }}".format(self.colors['secondary'])
        )
        release_resource_label = QLabel("Kaynak ID:")
        release_resource_label.setStyleSheet("font-weight: bold; color: {};".format(self.colors['dark']))
        release_form_layout.addRow(release_resource_label, self.release_resource_spin)
        
        self.release_instances_spin = QSpinBox()
        self.release_instances_spin.setRange(1, 100)
        self.release_instances_spin.setStyleSheet(
            "QSpinBox {{ border: 1px solid #bdc3c7; padding: 5px; border-radius: 3px; background-color: white; }} QSpinBox:focus {{ border: 1px solid {}; }}".format(self.colors['secondary'])
        )
        release_instances_label = QLabel("Ornek Sayisi:")
        release_instances_label.setStyleSheet("font-weight: bold; color: {};".format(self.colors['dark']))
        release_form_layout.addRow(release_instances_label, self.release_instances_spin)
        
        self.release_button = QPushButton("Serbest Birak")
        self.release_button.setStyleSheet(
            "QPushButton {{ background-color: {}; color: white; padding: 8px 15px; border-radius: 4px; font-weight: bold; border: none; }} QPushButton:hover {{ background-color: #27ae60; }} QPushButton:pressed {{ background-color: #1e8449; }}".format(self.colors['secondary'])
        )
        self.release_button.clicked.connect(self.release_resource)
        release_form_layout.addRow(self.release_button)
        
        release_form_group.setLayout(release_form_layout)
        
        # Tahsis, talep ve serbest birakma formlarini panele ekle
        allocation_request_panel.addWidget(allocation_form_group)
        allocation_request_panel.addWidget(request_form_group)
        allocation_request_panel.addWidget(release_form_group)
        
        # Deadlock kontrol paneli
        control_panel = QHBoxLayout()
        
        self.detect_button = QPushButton("DEADLOCK ALGILA")
        self.detect_button.setStyleSheet(
            "QPushButton {{ background-color: {}; color: white; padding: 12px 25px; border-radius: 5px; font-weight: bold; border: none; font-size: 14px; }} QPushButton:hover {{ background-color: #c0392b; }} QPushButton:pressed {{ background-color: #96281f; }}".format(self.colors['accent'])
        )
        self.detect_button.clicked.connect(self.detect_deadlock)
        
        self.reset_graph_button = QPushButton("Grafigi Sifirla")
        self.reset_graph_button.setStyleSheet(
            "QPushButton {{ background-color: {}; color: white; padding: 10px 20px; border-radius: 4px; font-weight: bold; border: none; }} QPushButton:hover {{ background-color: #2c3e50; }} QPushButton:pressed {{ background-color: #1a242f; }}".format(self.colors['dark'])
        )
        self.reset_graph_button.clicked.connect(self.reset_graph)
        
        control_panel.addStretch(1)
        control_panel.addWidget(self.detect_button)
        control_panel.addWidget(self.reset_graph_button)
        control_panel.addStretch(1)
        
        # Kaynak tahsis grafi goruntuleme
        graph_title = QLabel("Kaynak Tahsis Grafi")
        graph_title.setAlignment(Qt.AlignCenter)
        graph_title.setStyleSheet("color: {}; font-size: 16px; font-weight: bold; margin: 5px 0;".format(self.colors['dark']))
        
        self.graph_canvas = FigureCanvas(self.detector.visualize_graph())
        
        graph_info = QLabel("""
        <b>Grafik Aciklamasi:</b><br>
        <span style='color:#3498db;'>■</span> <b>Mavi dugumler:</b> Prosesler<br>
        <span style='color:#2ecc71;'>■</span> <b>Yesil dugumler:</b> Kaynaklar<br>
        <span style='color:#27ae60;'>→</span> <b>Yesil ok:</b> Kaynak tahsisi (Kaynak → Proses)<br>
        <span style='color:#e74c3c;'>- - →</span> <b>Kirmizi kesikli ok:</b> Kaynak talebi (Proses → Kaynak)
        """)
        graph_info.setStyleSheet(
            "color: {}; padding: 8px; background-color: #f8f9fa; border-radius: 5px; border: 1px dashed #bdc3c7; margin-top: 5px;".format(self.colors['dark'])
        )
        
        # Tum panelleri Deadlock Algilama sekmesine ekle
        detection_layout.addLayout(resource_process_panel)
        detection_layout.addLayout(allocation_request_panel)
        detection_layout.addLayout(control_panel)
        detection_layout.addWidget(graph_title)
        detection_layout.addWidget(self.graph_canvas, 1)  # Esnek
        detection_layout.addWidget(graph_info)
        
        self.detection_tab.setLayout(detection_layout)
        
        # 2. Sekme: Banker's Algoritmasi
        self.bankers_tab = QWidget()
        bankers_layout = QVBoxLayout()
        
        # Banker's bilgi etiketi
        bankers_info_label = QLabel("""
        <b>Banker's Algoritmasi:</b> Deadlock onleme icin guvenli durum kontrolu yapar.
        Her prosesin maksimum kaynak taleplerini onceden bilmek gerekir.
        Sistem guvenli ise, en az bir prosesin butun taleplerini karsilayabilir.
        """)
        bankers_info_label.setStyleSheet(
            "color: {}; padding: 8px; background-color: #f8f9fa; border-radius: 5px; border-left: 3px solid {}; margin-bottom: 10px;".format(self.colors['dark'], self.colors['info'])
        )
        bankers_info_label.setWordWrap(True)
        bankers_layout.addWidget(bankers_info_label)
        
        # Ust panel: Sistem kurulumu
        bankers_top_panel = QHBoxLayout()
        
        # Proses ve kaynak ayarlari
        setup_group = QGroupBox("Sistem Ayarlari")
        setup_group.setStyleSheet(
            "QGroupBox {{ background-color: {}; border: 1px solid {}; border-radius: 5px; margin-top: 15px; font-weight: bold; }} QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 5px; color: {}; }}".format(self.colors['light'], self.colors['primary'], self.colors['primary'])
        )
        setup_layout = QFormLayout()
        
        self.bankers_num_processes = QSpinBox()
        self.bankers_num_processes.setRange(1, 10)
        self.bankers_num_processes.setValue(3)
        self.bankers_num_processes.setStyleSheet(
            "QSpinBox {{ border: 1px solid #bdc3c7; padding: 5px; border-radius: 3px; background-color: white; }} QSpinBox:focus {{ border: 1px solid {}; }}".format(self.colors['primary'])
        )
        bankers_num_processes_label = QLabel("Proses Sayisi:")
        bankers_num_processes_label.setStyleSheet("font-weight: bold; color: {};".format(self.colors['dark']))
        setup_layout.addRow(bankers_num_processes_label, self.bankers_num_processes)
        
        self.bankers_num_resources = QSpinBox()
        self.bankers_num_resources.setRange(1, 10)
        self.bankers_num_resources.setValue(3)
        self.bankers_num_resources.setStyleSheet(
            "QSpinBox {{ border: 1px solid #bdc3c7; padding: 5px; border-radius: 3px; background-color: white; }} QSpinBox:focus {{ border: 1px solid {}; }}".format(self.colors['primary'])
        )
        bankers_num_resources_label = QLabel("Kaynak Turu Sayisi:")
        bankers_num_resources_label.setStyleSheet("font-weight: bold; color: {};".format(self.colors['dark']))
        setup_layout.addRow(bankers_num_resources_label, self.bankers_num_resources)
        
        self.bankers_setup_button = QPushButton("Sistemi Kur")
        self.bankers_setup_button.setStyleSheet(
            "QPushButton {{ background-color: {}; color: white; padding: 8px 15px; border-radius: 4px; font-weight: bold; border: none; }} QPushButton:hover {{ background-color: #2980b9; }} QPushButton:pressed {{ background-color: #1c5a85; }}".format(self.colors['primary'])
        )
        self.bankers_setup_button.clicked.connect(self.setup_bankers)
        setup_layout.addRow(self.bankers_setup_button)
        
        setup_group.setLayout(setup_layout)
        
        # Mevcut kaynaklar
        available_group = QGroupBox("Mevcut Kaynaklar")
        available_group.setStyleSheet(
            "QGroupBox {{ background-color: {}; border: 1px solid {}; border-radius: 5px; margin-top: 15px; font-weight: bold; }} QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 5px; color: {}; }}".format(self.colors['light'], self.colors['secondary'], self.colors['secondary'])
        )
        available_layout = QFormLayout()
        
        self.available_resources_edit = QLineEdit()
        self.available_resources_edit.setPlaceholderText("Örn: 10,5,7")
        self.available_resources_edit.setStyleSheet(
            "QLineEdit {{ border: 1px solid #bdc3c7; padding: 5px; border-radius: 3px; background-color: white; }} QLineEdit:focus {{ border: 1px solid {}; }}".format(self.colors['secondary'])
        )
        available_label = QLabel("Kaynaklar (virgülle ayrılmış):")
        available_label.setStyleSheet("font-weight: bold; color: {};".format(self.colors['dark']))
        available_layout.addRow(available_label, self.available_resources_edit)
        
        self.set_available_button = QPushButton("Ayarla")
        self.set_available_button.setStyleSheet(
            "QPushButton {{ background-color: {}; color: white; padding: 8px 15px; border-radius: 4px; font-weight: bold; border: none; }} QPushButton:hover {{ background-color: #27ae60; }} QPushButton:pressed {{ background-color: #1e8449; }}".format(self.colors['secondary'])
        )
        self.set_available_button.clicked.connect(self.set_available_resources)
        available_layout.addRow(self.set_available_button)
        
        available_group.setLayout(available_layout)
        
        # Üst panele grupları ekle
        bankers_top_panel.addWidget(setup_group)
        bankers_top_panel.addWidget(available_group)
        
        # Orta panel: Maksimum talep, tahsisat ve kaynak talepleri
        bankers_mid_panel = QHBoxLayout()
        
        # Maksimum talep
        max_claim_group = QGroupBox("Maksimum Talep")
        max_claim_group.setStyleSheet(
            "QGroupBox {{ background-color: {}; border: 1px solid {}; border-radius: 5px; margin-top: 15px; font-weight: bold; }} QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 5px; color: {}; }}".format(self.colors['light'], self.colors['info'], self.colors['info'])
        )
        max_claim_layout = QFormLayout()
        
        self.max_claim_process = QSpinBox()
        self.max_claim_process.setRange(0, 9)
        self.max_claim_process.setStyleSheet(
            "QSpinBox {{ border: 1px solid #bdc3c7; padding: 5px; border-radius: 3px; background-color: white; }} QSpinBox:focus {{ border: 1px solid {}; }}".format(self.colors['info'])
        )
        max_claim_process_label = QLabel("Proses Dizini:")
        max_claim_process_label.setStyleSheet("font-weight: bold; color: {};".format(self.colors['dark']))
        max_claim_layout.addRow(max_claim_process_label, self.max_claim_process)
        
        self.max_claim_edit = QLineEdit()
        self.max_claim_edit.setPlaceholderText("Örn: 7,5,3")
        self.max_claim_edit.setStyleSheet(
            "QLineEdit {{ border: 1px solid #bdc3c7; padding: 5px; border-radius: 3px; background-color: white; }} QLineEdit:focus {{ border: 1px solid {}; }}".format(self.colors['info'])
        )
        max_claim_edit_label = QLabel("Maksimum Talepler (virgülle ayrılmış):")
        max_claim_edit_label.setStyleSheet("font-weight: bold; color: {};".format(self.colors['dark']))
        max_claim_layout.addRow(max_claim_edit_label, self.max_claim_edit)
        
        self.set_max_claim_button = QPushButton("Ayarla")
        self.set_max_claim_button.setStyleSheet(
            "QPushButton {{ background-color: {}; color: white; padding: 8px 15px; border-radius: 4px; font-weight: bold; border: none; }} QPushButton:hover {{ background-color: #8e44ad; }} QPushButton:pressed {{ background-color: #6c3483; }}".format(self.colors['info'])
        )
        self.set_max_claim_button.clicked.connect(self.set_max_claim)
        max_claim_layout.addRow(self.set_max_claim_button)
        
        max_claim_group.setLayout(max_claim_layout)
        
        # Kaynak tahsisi
        allocation_group = QGroupBox("Kaynak Tahsisi")
        allocation_group.setStyleSheet(
            "QGroupBox {{ background-color: {}; border: 1px solid {}; border-radius: 5px; margin-top: 15px; font-weight: bold; }} QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 5px; color: {}; }}".format(self.colors['light'], self.colors['primary'], self.colors['primary'])
        )
        allocation_layout = QFormLayout()
        
        self.allocation_process_idx = QSpinBox()
        self.allocation_process_idx.setRange(0, 9)
        self.allocation_process_idx.setStyleSheet(
            "QSpinBox {{ border: 1px solid #bdc3c7; padding: 5px; border-radius: 3px; background-color: white; }} QSpinBox:focus {{ border: 1px solid {}; }}".format(self.colors['primary'])
        )
        allocation_process_idx_label = QLabel("Proses Dizini:")
        allocation_process_idx_label.setStyleSheet("font-weight: bold; color: {};".format(self.colors['dark']))
        allocation_layout.addRow(allocation_process_idx_label, self.allocation_process_idx)
        
        self.allocation_edit = QLineEdit()
        self.allocation_edit.setPlaceholderText("Örn: 0,1,0")
        self.allocation_edit.setStyleSheet(
            "QLineEdit {{ border: 1px solid #bdc3c7; padding: 5px; border-radius: 3px; background-color: white; }} QLineEdit:focus {{ border: 1px solid {}; }}".format(self.colors['primary'])
        )
        allocation_edit_label = QLabel("Tahsis Edilecek Kaynaklar:")
        allocation_edit_label.setStyleSheet("font-weight: bold; color: {};".format(self.colors['dark']))
        allocation_layout.addRow(allocation_edit_label, self.allocation_edit)
        
        self.allocate_resources_button = QPushButton("Tahsis Et")
        self.allocate_resources_button.setStyleSheet(
            "QPushButton {{ background-color: {}; color: white; padding: 8px 15px; border-radius: 4px; font-weight: bold; border: none; }} QPushButton:hover {{ background-color: #2980b9; }} QPushButton:pressed {{ background-color: #1c5a85; }}".format(self.colors['primary'])
        )
        self.allocate_resources_button.clicked.connect(self.bankers_allocate)
        allocation_layout.addRow(self.allocate_resources_button)
        
        allocation_group.setLayout(allocation_layout)
        
        # Kaynak talebi
        request_group = QGroupBox("Kaynak Talebi")
        request_group.setStyleSheet(
            "QGroupBox {{ background-color: {}; border: 1px solid {}; border-radius: 5px; margin-top: 15px; font-weight: bold; }} QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 5px; color: {}; }}".format(self.colors['light'], self.colors['warning'], self.colors['warning'])
        )
        request_layout = QFormLayout()
        
        self.request_process_idx = QSpinBox()
        self.request_process_idx.setRange(0, 9)
        self.request_process_idx.setStyleSheet(
            "QSpinBox {{ border: 1px solid #bdc3c7; padding: 5px; border-radius: 3px; background-color: white; }} QSpinBox:focus {{ border: 1px solid {}; }}".format(self.colors['warning'])
        )
        request_process_idx_label = QLabel("Proses Dizini:")
        request_process_idx_label.setStyleSheet("font-weight: bold; color: {};".format(self.colors['dark']))
        request_layout.addRow(request_process_idx_label, self.request_process_idx)
        
        self.request_edit = QLineEdit()
        self.request_edit.setPlaceholderText("Örn: 1,0,2")
        self.request_edit.setStyleSheet(
            "QLineEdit {{ border: 1px solid #bdc3c7; padding: 5px; border-radius: 3px; background-color: white; }} QLineEdit:focus {{ border: 1px solid {}; }}".format(self.colors['warning'])
        )
        request_edit_label = QLabel("Talep Edilecek Kaynaklar:")
        request_edit_label.setStyleSheet("font-weight: bold; color: {};".format(self.colors['dark']))
        request_layout.addRow(request_edit_label, self.request_edit)
        
        self.request_resources_button = QPushButton("Talep Et")
        self.request_resources_button.setStyleSheet(
            "QPushButton {{ background-color: {}; color: white; padding: 8px 15px; border-radius: 4px; font-weight: bold; border: none; }} QPushButton:hover {{ background-color: #e67e22; }} QPushButton:pressed {{ background-color: #d35400; }}".format(self.colors['warning'])
        )
        self.request_resources_button.clicked.connect(self.bankers_request)
        request_layout.addRow(self.request_resources_button)
        
        request_group.setLayout(request_layout)
        
        # Orta panele grupları ekle
        bankers_mid_panel.addWidget(max_claim_group)
        bankers_mid_panel.addWidget(allocation_group)
        bankers_mid_panel.addWidget(request_group)
        
        # Alt panel: Banker's durumu ve görselleştirme
        bankers_bottom_panel = QVBoxLayout()
        
        # Güvenlik kontrolü
        control_layout = QHBoxLayout()
        
        self.check_safety_button = QPushButton("Güvenlik Durumunu Kontrol Et")
        self.check_safety_button.setStyleSheet(
            "QPushButton {{ background-color: {}; color: white; padding: 10px 20px; border-radius: 4px; font-weight: bold; border: none; }} QPushButton:hover {{ background-color: #2980b9; }} QPushButton:pressed {{ background-color: #1c5a85; }}".format(self.colors['primary'])
        )
        self.check_safety_button.clicked.connect(self.check_safety)
        
        self.reset_bankers_button = QPushButton("Sistemi Sıfırla")
        self.reset_bankers_button.setStyleSheet(
            "QPushButton {{ background-color: {}; color: white; padding: 10px 20px; border-radius: 4px; font-weight: bold; border: none; }} QPushButton:hover {{ background-color: #c0392b; }} QPushButton:pressed {{ background-color: #96281f; }}".format(self.colors['accent'])
        )
        self.reset_bankers_button.clicked.connect(self.reset_bankers)
        
        control_layout.addWidget(self.check_safety_button)
        control_layout.addWidget(self.reset_bankers_button)
        
        # Banker's durumu görselleştirme
        self.bankers_canvas = FigureCanvas(self.bankers.get_state_visualization())
        
        # Alt panele öğeleri ekle
        bankers_bottom_panel.addLayout(control_layout)
        bankers_bottom_panel.addWidget(self.bankers_canvas, 1)  # Esnek
        
        # Tüm panelleri Banker's sekmesine ekle
        bankers_layout.addLayout(bankers_top_panel)
        bankers_layout.addLayout(bankers_mid_panel)
        bankers_layout.addLayout(bankers_bottom_panel)
        
        self.bankers_tab.setLayout(bankers_layout)
        
        # Sekmeleri üst sekmelere ekle
        top_tabs.addTab(self.detection_tab, "Deadlock Algılama")
        top_tabs.addTab(self.bankers_tab, "Banker's Algoritması")
        
        # Ana düzene üst sekmeleri ekle
        main_layout.addWidget(top_tabs)
        
        # Ana düzeni pencereye uygula
        self.setLayout(main_layout)
    
    def add_resource(self):
        """Yeni bir kaynak ekler"""
        resource_id = self.resource_id_spin.value()
        instances = self.resource_instances_spin.value()
        
        # Kaynağı ekle
        self.detector.add_resource(resource_id, instances)
        
        # Grafiği güncelle
        self.update_graph()
        
        # Başarılı mesajı göster
        QMessageBox.information(self, "Başarılı", 
                             "Kaynak R{} eklendi ({} örnek).".format(resource_id, instances))
    
    def add_process(self):
        """Yeni bir proses ekler"""
        process_id = self.process_id_spin.value()
        
        # Prosesi ekle
        self.detector.add_process(process_id)
        
        # Grafiği güncelle
        self.update_graph()
        
        # Başarılı mesajı göster
        QMessageBox.information(self, "Başarılı", 
                             "Proses P{} eklendi.".format(process_id))
    
    def allocate_resource(self):
        """Bir kaynağı bir prosese tahsis eder"""
        process_id = self.allocation_process_spin.value()
        resource_id = self.allocation_resource_spin.value()
        instances = self.allocation_instances_spin.value()
        
        # Kaynağı tahsis et
        success = self.detector.allocate_resource(process_id, resource_id, instances)
        
        if success:
            # Grafiği güncelle
            self.update_graph()
            
            # Başarılı mesajı göster
            QMessageBox.information(self, "Başarılı", 
                                 "Kaynak R{} ({} örnek) Proses P{}'e tahsis edildi.".format(resource_id, instances, process_id))
        else:
            # Hata mesajı göster
            QMessageBox.warning(self, "Hata", 
                              "Kaynak R{} ({} örnek) tahsis edilemedi.".format(resource_id, instances))
    
    def request_resource(self):
        """Bir prosesin bir kaynak talebini ekler"""
        process_id = self.request_process_spin.value()
        resource_id = self.request_resource_spin.value()
        instances = self.request_instances_spin.value()
        
        # Kaynak talebini ekle
        self.detector.request_resource(process_id, resource_id, instances)
        
        # Grafiği güncelle
        self.update_graph()
        
        # Başarılı mesajı göster
        QMessageBox.information(self, "Başarılı", 
                             "Proses P{} Kaynak R{} ({} örnek) için talepte bulundu.".format(process_id, resource_id, instances))
    
    def release_resource(self):
        """Bir prosesin sahip olduğu bir kaynağı serbest bırakır"""
        process_id = self.release_process_spin.value()
        resource_id = self.release_resource_spin.value()
        instances = self.release_instances_spin.value()
        
        # Kaynağı serbest bırak
        success = self.detector.release_resource(process_id, resource_id, instances)
        
        if success:
            # Grafiği güncelle
            self.update_graph()
            
            # Başarılı mesajı göster
            QMessageBox.information(self, "Başarılı", 
                                 "Proses P{} Kaynak R{} ({} örnek) serbest bıraktı.".format(process_id, resource_id, instances))
        else:
            # Hata mesajı göster
            QMessageBox.warning(self, "Hata", 
                              "Kaynak R{} ({} örnek) serbest bırakılamadı.".format(resource_id, instances))
    
    def detect_deadlock(self):
        """Deadlock durumunu kontrol eder"""
        deadlock_cycle = self.detector.detect_deadlock()
        
        if deadlock_cycle:
            # Deadlock bulundu
            cycle_str = " -> ".join(deadlock_cycle)
            QMessageBox.critical(self, "Deadlock Algılandı", 
                               "Sistemde deadlock tespit edildi!\n\nDöngü: {}".format(cycle_str))
        else:
            # Deadlock yok
            QMessageBox.information(self, "Deadlock Yok", 
                                 "Sistemde deadlock tespit edilmedi.")
        
        # Grafiği güncelle
        self.update_graph()
    
    def reset_graph(self):
        """Kaynak tahsis grafını sıfırlar"""
        self.detector.reset()
        
        # Grafiği güncelle
        self.update_graph()
        
        # Başarılı mesajı göster
        QMessageBox.information(self, "Başarılı", "Kaynak tahsis grafı sıfırlandı.")
    
    def update_graph(self):
        """Kaynak tahsis grafı görselleştirmesini günceller"""
        self.graph_canvas.figure = self.detector.visualize_graph()
        self.graph_canvas.draw()
    
    def setup_bankers(self):
        """Banker's algoritması için sistemi kurar"""
        num_processes = self.bankers_num_processes.value()
        num_resources = self.bankers_num_resources.value()
        
        # Proses ve kaynak ID'leri oluştur
        process_ids = list(range(num_processes))
        resource_ids = list(range(num_resources))
        
        # Başlangıçta mevcut kaynaklar sıfır
        available_resources = [0] * num_resources
        
        # Banker's algoritmasını kur
        self.bankers.setup(process_ids, resource_ids, available_resources)
        
        # Görselleştirmeyi güncelle
        self.update_bankers_visualization()
        
        # Başarılı mesajı göster
        QMessageBox.information(self, "Başarılı", 
                             "Banker's algoritması kuruldu ({} proses, {} kaynak türü).".format(num_processes, num_resources))
    
    def set_available_resources(self):
        """Mevcut kaynakları ayarlar"""
        # Metin girişini oku
        text = self.available_resources_edit.text()
        
        try:
            # Virgülle ayrılmış değerleri ayır ve tamsayıya çevir
            values = [int(x.strip()) for x in text.split(",")]
            
            # Kaynak sayısını kontrol et
            if len(values) != len(self.bankers.resources):
                raise ValueError("Tam olarak {} kaynak değeri girmelisiniz".format(len(self.bankers.resources)))
            
            # Mevcut kaynakları ayarla
            self.bankers.available = values.copy()
            
            # Görselleştirmeyi güncelle
            self.update_bankers_visualization()
            
            # Başarılı mesajı göster
            QMessageBox.information(self, "Başarılı", "Mevcut kaynaklar güncellendi.")
            
        except Exception as e:
            # Hata mesajı göster
            QMessageBox.warning(self, "Hata", "Mevcut kaynaklar ayarlanamadı: {}".format(str(e)))
    
    def set_max_claim(self):
        """Bir proses için maksimum talepleri ayarlar"""
        process_idx = self.max_claim_process.value()
        
        if process_idx >= len(self.bankers.processes):
            QMessageBox.warning(self, "Hata", "Geçersiz proses dizini")
            return
        
        # Metin girişini oku
        text = self.max_claim_edit.text()
        
        try:
            # Virgülle ayrılmış değerleri ayır ve tamsayıya çevir
            values = [int(x.strip()) for x in text.split(",")]
            
            # Kaynak sayısını kontrol et
            if len(values) != len(self.bankers.resources):
                raise ValueError("Tam olarak {} kaynak değeri girmelisiniz".format(len(self.bankers.resources)))
            
            # Maksimum talepleri ayarla
            self.bankers.set_max_claim(process_idx, values)
            
            # Görselleştirmeyi güncelle
            self.update_bankers_visualization()
            
            # Başarılı mesajı göster
            QMessageBox.information(self, "Başarılı", 
                                 "Proses {} için maksimum talepler güncellendi.".format(self.bankers.processes[process_idx]))
            
        except Exception as e:
            # Hata mesajı göster
            QMessageBox.warning(self, "Hata", "Maksimum talepler ayarlanamadı: {}".format(str(e)))
    
    def bankers_allocate(self):
        """Bir prosese kaynakları tahsis eder"""
        process_idx = self.allocation_process_idx.value()
        
        if process_idx >= len(self.bankers.processes):
            QMessageBox.warning(self, "Hata", "Geçersiz proses dizini")
            return
        
        # Metin girişini oku
        text = self.allocation_edit.text()
        
        try:
            # Virgülle ayrılmış değerleri ayır ve tamsayıya çevir
            values = [int(x.strip()) for x in text.split(",")]
            
            # Kaynak sayısını kontrol et
            if len(values) != len(self.bankers.resources):
                raise ValueError("Tam olarak {} kaynak değeri girmelisiniz".format(len(self.bankers.resources)))
            
            # Kaynakları tahsis et
            success = self.bankers.allocate_resources(process_idx, values)
            
            if not success:
                raise ValueError("Tahsis başarısız oldu (yetersiz kaynaklar veya maksimum talepten fazla)")
            
            # Görselleştirmeyi güncelle
            self.update_bankers_visualization()
            
            # Başarılı mesajı göster
            QMessageBox.information(self, "Başarılı", 
                                 "Proses {} için kaynaklar tahsis edildi.".format(self.bankers.processes[process_idx]))
            
        except Exception as e:
            # Hata mesajı göster
            QMessageBox.warning(self, "Hata", "Kaynaklar tahsis edilemedi: {}".format(str(e)))
    
    def bankers_request(self):
        """Bir prosesin kaynak talebini değerlendirir"""
        process_idx = self.request_process_idx.value()
        
        if process_idx >= len(self.bankers.processes):
            QMessageBox.warning(self, "Hata", "Geçersiz proses dizini")
            return
        
        # Metin girişini oku
        text = self.request_edit.text()
        
        try:
            # Virgülle ayrılmış değerleri ayır ve tamsayıya çevir
            values = [int(x.strip()) for x in text.split(",")]
            
            # Kaynak sayısını kontrol et
            if len(values) != len(self.bankers.resources):
                raise ValueError("Tam olarak {} kaynak değeri girmelisiniz".format(len(self.bankers.resources)))
            
            # Kaynak talebini değerlendir
            success, message = self.bankers.request_resources(process_idx, values)
            
            # Görselleştirmeyi güncelle
            self.update_bankers_visualization()
            
            if success:
                # Başarılı mesajı göster
                QMessageBox.information(self, "Talep Karşılandı", message)
            else:
                # Uyarı mesajı göster
                QMessageBox.warning(self, "Talep Reddedildi", message)
            
        except Exception as e:
            # Hata mesajı göster
            QMessageBox.warning(self, "Hata", "Kaynak talebi değerlendirilemedi: {}".format(str(e)))
    
    def check_safety(self):
        """Sistemin güvenli durumda olup olmadığını kontrol eder"""
        is_safe, safe_sequence = self.bankers.is_safe_state()
        
        if is_safe:
            # Güvenli
            sequence_str = " -> ".join(str(p) for p in safe_sequence)
            QMessageBox.information(self, "Güvenli Durum", 
                                 "Sistem GÜVENLİ bir durumdadır.\n\nGüvenli Sıralama: {}".format(sequence_str))
        else:
            # Güvenli değil
            QMessageBox.critical(self, "Güvensiz Durum", 
                               "Sistem GÜVENSİZ bir durumdadır.\n\nHerhangi bir zamanda deadlock oluşabilir!")
        
        # Görselleştirmeyi güncelle
        self.update_bankers_visualization()
    
    def reset_bankers(self):
        """Banker's algoritmasını sıfırlar"""
        self.bankers = BankersAlgorithm()
        
        # Görselleştirmeyi güncelle
        self.update_bankers_visualization()
        
        # Başarılı mesajı göster
        QMessageBox.information(self, "Başarılı", "Banker's algoritması sıfırlandı.")
    
    def update_bankers_visualization(self):
        """Banker's algoritması görselleştirmesini günceller"""
        self.bankers_canvas.figure = self.bankers.get_state_visualization()
        self.bankers_canvas.draw()