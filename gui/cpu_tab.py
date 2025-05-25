"""
CPU Zamanlayici Sekmesi
CPU zamanlama algoritmalarini gorselleştiren ve karsilastiran sekme.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
                           QGroupBox, QSpinBox, QFormLayout, QTabWidget,
                           QMessageBox, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from cpu_scheduler.scheduler import CPUScheduler
from cpu_scheduler.metrics import SchedulingMetrics

class CPUSchedulerTab(QWidget):
    """CPU zamanlayici sekmesi"""
    
    def __init__(self):
        """CPU zamanlayici sekmesini baslat"""
        super().__init__()
        
        # CPU zamanlayici ve metrik hesaplayici
        self.scheduler = CPUScheduler()
        self.metrics = SchedulingMetrics(self.scheduler)
        
        # Algoritma performans metrikleri
        self.algorithm_metrics = {}
        
        # Renk paleti
        self.colors = {
            "primary": "#3498db",
            "secondary": "#2ecc71",
            "accent": "#e74c3c",
            "light": "#ecf0f1",
            "dark": "#34495e",
            "table_header": "#2c3e50",
            "table_alt": "#f9f9f9"
        }
        
        # Arayuzu olustur
        self.init_ui()
    
    def init_ui(self):
        """Kullanici arayuzunu olusturur"""
        # Ana duzen
        main_layout = QVBoxLayout()
        
        # Baslik
        title_label = QLabel("CPU Zamanlama Algoritmalari Simulatoru")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(
            "color: {}; font-size: 18px; font-weight: bold; margin: 10px 0; padding: 5px; background-color: {}; border-radius: 5px; border-bottom: 3px solid {};".format(self.colors['dark'], self.colors['light'], self.colors['primary'])
        )
        main_layout.addWidget(title_label)
        
        # Ust panel: Proses ekleme ve tablo
        top_panel = QHBoxLayout()
        
        # Sol: Proses ekleme formu
        process_form_group = QGroupBox("Yeni Proses Ekle")
        process_form_group.setStyleSheet(
            "QGroupBox {{ background-color: {}; border: 1px solid {}; border-radius: 5px; margin-top: 15px; font-weight: bold; }} QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 5px; color: {}; }}".format(self.colors['light'], self.colors['primary'], self.colors['primary'])
        )
        process_form_layout = QFormLayout()
        
        # Proses ID'si
        self.pid_spin = QSpinBox()
        self.pid_spin.setRange(1, 100)
        self.pid_spin.setStyleSheet(
            "QSpinBox {{ border: 1px solid #bdc3c7; padding: 5px; border-radius: 3px; background-color: white; }} QSpinBox:focus {{ border: 1px solid {}; }}".format(self.colors['primary'])
        )
        pid_label = QLabel("Proses ID:")
        pid_label.setStyleSheet("font-weight: bold; color: {};".format(self.colors['dark']))
        process_form_layout.addRow(pid_label, self.pid_spin)
        
        # Varis zamani
        self.arrival_time_spin = QSpinBox()
        self.arrival_time_spin.setRange(0, 100)
        self.arrival_time_spin.setStyleSheet(
            "QSpinBox {{ border: 1px solid #bdc3c7; padding: 5px; border-radius: 3px; background-color: white; }} QSpinBox:focus {{ border: 1px solid {}; }}".format(self.colors['primary'])
        )
        arrival_label = QLabel("Varis Zamani:")
        arrival_label.setStyleSheet("font-weight: bold; color: {};".format(self.colors['dark']))
        process_form_layout.addRow(arrival_label, self.arrival_time_spin)
        
        # Islem suresi
        self.burst_time_spin = QSpinBox()
        self.burst_time_spin.setRange(1, 100)
        self.burst_time_spin.setStyleSheet(
            "QSpinBox {{ border: 1px solid #bdc3c7; padding: 5px; border-radius: 3px; background-color: white; }} QSpinBox:focus {{ border: 1px solid {}; }}".format(self.colors['primary'])
        )
        burst_label = QLabel("Islem Suresi:")
        burst_label.setStyleSheet("font-weight: bold; color: {};".format(self.colors['dark']))
        process_form_layout.addRow(burst_label, self.burst_time_spin)
        
        # Oncelik
        self.priority_spin = QSpinBox()
        self.priority_spin.setRange(1, 10)
        self.priority_spin.setStyleSheet(
            "QSpinBox {{ border: 1px solid #bdc3c7; padding: 5px; border-radius: 3px; background-color: white; }} QSpinBox:focus {{ border: 1px solid {}; }}".format(self.colors['primary'])
        )
        priority_label = QLabel("Oncelik (dusuk deger yuksek oncelik):")
        priority_label.setStyleSheet("font-weight: bold; color: {};".format(self.colors['dark']))
        process_form_layout.addRow(priority_label, self.priority_spin)
        
        # Proses ekle butonu
        self.add_process_button = QPushButton("Proses Ekle")
        self.add_process_button.setStyleSheet(
            "QPushButton {{ background-color: {}; color: white; padding: 8px 15px; border-radius: 4px; font-weight: bold; border: none; }} QPushButton:hover {{ background-color: #2980b9; }} QPushButton:pressed {{ background-color: #1c5a85; }}".format(self.colors['primary'])
        )
        self.add_process_button.clicked.connect(self.add_process)
        
        # Tum prosesleri temizle butonu
        self.clear_processes_button = QPushButton("Tum Prosesleri Temizle")
        self.clear_processes_button.setStyleSheet(
            "QPushButton {{ background-color: {}; color: white; padding: 8px 15px; border-radius: 4px; font-weight: bold; border: none; }} QPushButton:hover {{ background-color: #c0392b; }} QPushButton:pressed {{ background-color: #96281f; }}".format(self.colors['accent'])
        )
        self.clear_processes_button.clicked.connect(self.clear_processes)
        
        # Butonlari yatay duzene ekle
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.add_process_button)
        buttons_layout.addWidget(self.clear_processes_button)
        
        # Form duzenine butonlari ekle
        process_form_layout.addRow(buttons_layout)
        process_form_group.setLayout(process_form_layout)
        
        # Sag: Proses tablosu
        processes_group = QGroupBox("Prosesler")
        processes_group.setStyleSheet(
            "QGroupBox {{ background-color: {}; border: 1px solid {}; border-radius: 5px; margin-top: 15px; font-weight: bold; }} QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 5px; color: {}; }}".format(self.colors['light'], self.colors['secondary'], self.colors['secondary'])
        )
        processes_layout = QVBoxLayout()
        
        # Proses tablosu
        self.processes_table = QTableWidget(0, 4)
        self.processes_table.setHorizontalHeaderLabels(["Proses ID", "Varis Zamani", "Islem Suresi", "Oncelik"])
        self.processes_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.processes_table.setStyleSheet(
            "QTableWidget {{ border: 1px solid #dcdcdc; border-radius: 5px; alternate-background-color: {}; gridline-color: #dcdcdc; selection-background-color: {}; selection-color: white; }} QTableWidget QHeaderView::section {{ background-color: {}; color: white; padding: 6px; font-weight: bold; border: none; }} QTableWidget::item {{ padding: 4px; }}".format(self.colors['table_alt'], self.colors['primary'], self.colors['table_header'])
        )
        self.processes_table.setAlternatingRowColors(True)
        
        processes_layout.addWidget(self.processes_table)
        processes_group.setLayout(processes_layout)
        
        # Sol ve sag panelleri ust panele ekle
        top_panel.addWidget(process_form_group, 1)
        top_panel.addWidget(processes_group, 2)
        
        # Orta panel: Algoritma secimi ve parametreler
        mid_panel = QHBoxLayout()
        
        # Algoritma secim grubu
        algorithm_group = QGroupBox("Zamanlama Algoritmasi")
        algorithm_group.setStyleSheet(
            "QGroupBox {{ background-color: {}; border: 1px solid {}; border-radius: 5px; margin-top: 15px; font-weight: bold; }} QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 5px; color: {}; }}".format(self.colors['light'], self.colors['primary'], self.colors['primary'])
        )
        algorithm_layout = QFormLayout()
        
        # Algoritma secimi
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems([
            "First-Come-First-Serve (FCFS)", 
            "Shortest Job First (SJF)", 
            "Shortest Remaining Time First (SRTF)",
            "Round Robin (RR)", 
            "Priority (Non-preemptive)", 
            "Priority (Preemptive)"
        ])
        self.algorithm_combo.setStyleSheet(
            "QComboBox {{ border: 1px solid #bdc3c7; padding: 5px; border-radius: 3px; background-color: white; }} QComboBox:focus {{ border: 1px solid {}; }} QComboBox::drop-down {{ subcontrol-origin: padding; subcontrol-position: top right; width: 20px; border-left: 1px solid #bdc3c7; }} QComboBox QAbstractItemView {{ border: 1px solid #bdc3c7; selection-background-color: {}; selection-color: white; }}".format(self.colors['primary'], self.colors['primary'])
        )
        self.algorithm_combo.currentIndexChanged.connect(self.toggle_time_quantum)
        algorithm_label = QLabel("Algoritma:")
        algorithm_label.setStyleSheet("font-weight: bold; color: {};".format(self.colors['dark']))
        algorithm_layout.addRow(algorithm_label, self.algorithm_combo)
        
        # Round Robin zaman dilimi
        self.time_quantum_spin = QSpinBox()
        self.time_quantum_spin.setRange(1, 100)
        self.time_quantum_spin.setValue(4)
        self.time_quantum_spin.setEnabled(False)  # Baslangicta devre disi
        self.time_quantum_spin.setStyleSheet(
            "QSpinBox {{ border: 1px solid #bdc3c7; padding: 5px; border-radius: 3px; background-color: white; }} QSpinBox:focus {{ border: 1px solid {}; }}".format(self.colors['primary'])
        )
        time_quantum_label = QLabel("Zaman Dilimi (RR icin):")
        time_quantum_label.setStyleSheet("font-weight: bold; color: {};".format(self.colors['dark']))
        algorithm_layout.addRow(time_quantum_label, self.time_quantum_spin)
        
        # Calistir butonu
        self.run_button = QPushButton("Algoritmayi Calistir")
        self.run_button.setStyleSheet(
            "QPushButton {{ background-color: {}; color: white; padding: 10px 20px; border-radius: 4px; font-weight: bold; border: none; font-size: 14px; }} QPushButton:hover {{ background-color: #27ae60; }} QPushButton:pressed {{ background-color: #1e8449; }}".format(self.colors['secondary'])
        )
        self.run_button.clicked.connect(self.run_algorithm)
        algorithm_layout.addRow(self.run_button)
        
        algorithm_group.setLayout(algorithm_layout)
        
        # Karsilastirma butonu
        comparison_group = QGroupBox("Algoritma Karsilastirmasi")
        comparison_group.setStyleSheet(
            "QGroupBox {{ background-color: {}; border: 1px solid {}; border-radius: 5px; margin-top: 15px; font-weight: bold; }} QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 5px; color: {}; }}".format(self.colors['light'], self.colors['accent'], self.colors['accent'])
        )
        comparison_layout = QVBoxLayout()
        
        self.compare_button = QPushButton("Tum Algoritmalari Karsilastir")
        self.compare_button.setStyleSheet(
            "QPushButton {{ background-color: {}; color: white; padding: 10px 20px; border-radius: 4px; font-weight: bold; border: none; font-size: 14px; }} QPushButton:hover {{ background-color: #c0392b; }} QPushButton:pressed {{ background-color: #96281f; }}".format(self.colors['accent'])
        )
        self.compare_button.clicked.connect(self.compare_algorithms)
        comparison_layout.addWidget(self.compare_button)
        
        comparison_group.setLayout(comparison_layout)
        
        # Orta panele algoritma ve karsilastirma gruplarini ekle
        mid_panel.addWidget(algorithm_group)
        mid_panel.addWidget(comparison_group)
        
        # Alt panel: Sonuc sekmeleri
        bottom_panel = QTabWidget()
        bottom_panel.setStyleSheet(
            "QTabWidget::pane {{ border: 1px solid {}; background: {}; border-radius: 5px; }} QTabBar::tab {{ background: #e0e0e0; color: {}; padding: 8px 15px; margin-right: 2px; border-top-left-radius: 4px; border-top-right-radius: 4px; border: 1px solid #cccccc; font-weight: bold; }} QTabBar::tab:selected {{ background: {}; color: white; border-bottom-color: {}; }} QTabBar::tab:hover:!selected {{ background: #e8f6fe; }}".format(self.colors['primary'], self.colors['light'], self.colors['dark'], self.colors['primary'], self.colors['primary'])
        )
        
        # Gantt semasi sekmesi
        self.gantt_tab = QWidget()
        gantt_layout = QVBoxLayout()
        
        gantt_title = QLabel("Gantt Semasi")
        gantt_title.setAlignment(Qt.AlignCenter)
        gantt_title.setStyleSheet("color: {}; font-size: 16px; font-weight: bold; margin-bottom: 10px;".format(self.colors['dark']))
        gantt_layout.addWidget(gantt_title)
        
        self.gantt_canvas = FigureCanvas(self.metrics.create_gantt_chart())
        gantt_layout.addWidget(self.gantt_canvas)
        
        gantt_info = QLabel("Gantt semasi, proseslerin CPU'da calisma zamanlarini gosterir. Her renk farkli bir prosesi temsil eder.")
        gantt_info.setStyleSheet(
            "color: {}; font-style: italic; padding: 5px; background-color: #f8f9fa; border-radius: 3px; border-left: 3px solid {};".format(self.colors['dark'], self.colors['primary'])
        )
        gantt_info.setWordWrap(True)
        gantt_layout.addWidget(gantt_info)
        
        self.gantt_tab.setLayout(gantt_layout)
        
        # Metrikler sekmesi
        self.metrics_tab = QWidget()
        metrics_layout = QVBoxLayout()
        
        metrics_title = QLabel("Performans Metrikleri")
        metrics_title.setAlignment(Qt.AlignCenter)
        metrics_title.setStyleSheet("color: {}; font-size: 16px; font-weight: bold; margin-bottom: 10px;".format(self.colors['dark']))
        metrics_layout.addWidget(metrics_title)
        
        # Metrik tablosu
        self.metrics_table = QTableWidget(3, 2)
        self.metrics_table.setHorizontalHeaderLabels(["Metrik", "Deger"])
        self.metrics_table.verticalHeader().setVisible(False)
        self.metrics_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.metrics_table.setStyleSheet(
            "QTableWidget {{ border: 1px solid #dcdcdc; border-radius: 5px; alternate-background-color: {}; gridline-color: #dcdcdc; selection-background-color: {}; selection-color: white; }} QTableWidget QHeaderView::section {{ background-color: {}; color: white; padding: 6px; font-weight: bold; border: none; }} QTableWidget::item {{ padding: 4px; }}".format(self.colors['table_alt'], self.colors['primary'], self.colors['table_header'])
        )
        self.metrics_table.setAlternatingRowColors(True)
        
        # Metrik satirlarini ayarla
        metrics = ["Ortalama Bekleme Suresi", "Ortalama Toplam Islem Suresi", "Ortalama Cevap Suresi"]
        for i, metric in enumerate(metrics):
            self.metrics_table.setItem(i, 0, QTableWidgetItem(metric))
            self.metrics_table.setItem(i, 1, QTableWidgetItem("0.00"))
        
        metrics_layout.addWidget(self.metrics_table)
        
        metrics_info = QLabel("""
        <b>Metrik Aciklamalari:</b><br>
        <b>Ortalama Bekleme Suresi:</b> Proseslerin CPU'yu beklemek icin gecirdikleri ortalama sure.<br>
        <b>Ortalama Toplam Islem Suresi:</b> Proseslerin sistemde gecirdikleri toplam ortalama sure (bekleme + calisma).<br>
        <b>Ortalama Cevap Suresi:</b> Proseslerin ilk kez CPU'ya atanana kadar gecen ortalama sure.
        """)
        metrics_info.setStyleSheet(
            "color: {}; padding: 5px; background-color: #f8f9fa; border-radius: 3px; border-left: 3px solid {};".format(self.colors['dark'], self.colors['secondary'])
        )
        metrics_info.setWordWrap(True)
        metrics_layout.addWidget(metrics_info)
        
        self.metrics_tab.setLayout(metrics_layout)
        
        # Karsilastirma sekmesi
        self.comparison_tab = QWidget()
        comparison_tab_layout = QVBoxLayout()
        
        comparison_title = QLabel("Algoritma Karsilastirmasi")
        comparison_title.setAlignment(Qt.AlignCenter)
        comparison_title.setStyleSheet("color: {}; font-size: 16px; font-weight: bold; margin-bottom: 10px;".format(self.colors['dark']))
        comparison_tab_layout.addWidget(comparison_title)
        
        self.comparison_canvas = FigureCanvas(self.metrics.create_metrics_comparison({}))
        comparison_tab_layout.addWidget(self.comparison_canvas)
        
        comparison_info = QLabel("""
        <b>Karsilastirma Bilgisi:</b><br>
        Bu grafik, farkli zamanlama algoritmalari arasindaki performans metriklerini karsilastirir.
        Dusuk degerler genellikle daha iyi performansi gosterir.
        """)
        comparison_info.setStyleSheet(
            "color: {}; padding: 5px; background-color: #f8f9fa; border-radius: 3px; border-left: 3px solid {};".format(self.colors['dark'], self.colors['accent'])
        )
        comparison_info.setWordWrap(True)
        comparison_tab_layout.addWidget(comparison_info)
        
        self.comparison_tab.setLayout(comparison_tab_layout)
        
        # Sekmeleri alt panele ekle
        bottom_panel.addTab(self.gantt_tab, "Gantt Semasi")
        bottom_panel.addTab(self.metrics_tab, "Metrikler")
        bottom_panel.addTab(self.comparison_tab, "Karsilastirma")
        
        # Ana duzene panelleri ekle
        main_layout.addLayout(top_panel)
        main_layout.addLayout(mid_panel)
        main_layout.addWidget(bottom_panel, 1)  # Esnek
        
        # Ana duzeni pencereye uygula
        self.setLayout(main_layout)
    
    def toggle_time_quantum(self, index):
        """
        Round Robin secildiginde zaman dilimi spin box'ini etkinlestirir/devre disi birakir
        
        Parametreler:
        index (int): Combobox'taki secilen indeks
        """
        # Round Robin (3. indeks) secildiyse etkinlestir
        self.time_quantum_spin.setEnabled(index == 3)
    
    def add_process(self):
        """Yeni bir proses ekler"""
        pid = self.pid_spin.value()
        arrival_time = self.arrival_time_spin.value()
        burst_time = self.burst_time_spin.value()
        priority = self.priority_spin.value()
        
        # Ayni PID'li proses var mi kontrol et
        for i in range(self.processes_table.rowCount()):
            if int(self.processes_table.item(i, 0).text()) == pid:
                error_box = QMessageBox()
                error_box.setIcon(QMessageBox.Warning)
                error_box.setWindowTitle("Hata")
                error_box.setText("PID {} zaten kullaniliyor.".format(pid))
                error_box.setStandardButtons(QMessageBox.Ok)
                error_box.setStyleSheet(
                    "QMessageBox {{ background-color: {}; border: 1px solid {}; border-radius: 5px; }} QPushButton {{ background-color: {}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold; }} QPushButton:hover {{ background-color: #2980b9; }}".format(self.colors['light'], self.colors['accent'], self.colors['primary'])
                )
                error_box.exec_()
                return
        
        # Yeni satir ekle
        row_position = self.processes_table.rowCount()
        self.processes_table.insertRow(row_position)
        
        # Hucrelere degerleri ekle
        pid_item = QTableWidgetItem(str(pid))
        arrival_item = QTableWidgetItem(str(arrival_time))
        burst_item = QTableWidgetItem(str(burst_time))
        priority_item = QTableWidgetItem(str(priority))
        
        # Hucrelere renk ver
        pid_item.setBackground(QColor(self.colors['light']))
        arrival_item.setBackground(QColor(self.colors['light']))
        burst_item.setBackground(QColor(self.colors['light']))
        priority_item.setBackground(QColor(self.colors['light']))
        
        # Hucreleri tabloya ekle
        self.processes_table.setItem(row_position, 0, pid_item)
        self.processes_table.setItem(row_position, 1, arrival_item)
        self.processes_table.setItem(row_position, 2, burst_item)
        self.processes_table.setItem(row_position, 3, priority_item)
        
        # Zamanlayiciya prosesi ekle
        self.scheduler.add_process(pid, arrival_time, burst_time, priority)
        
        # Degerleri artir (kullanislilik icin)
        self.pid_spin.setValue(pid + 1)
        
        # Basarili mesaji goster
        self.status_message("Proses {} eklendi".format(pid), "success")
    
    def clear_processes(self):
        """Tum prosesleri temizler"""
        # Tabloyu temizle
        self.processes_table.setRowCount(0)
        
        # Zamanlayiciyi sifirla
        self.scheduler = CPUScheduler()
        self.metrics = SchedulingMetrics(self.scheduler)
        
        # Metrik tablosunu sifirla
        for i in range(3):
            self.metrics_table.setItem(i, 1, QTableWidgetItem("0.00"))
        
        # Gantt semasini sifirla
        self.gantt_canvas.figure = self.metrics.create_gantt_chart()
        self.gantt_canvas.draw()
        
        # PID'yi sifirla
        self.pid_spin.setValue(1)
        
        # Algoritma metriklerini temizle
        self.algorithm_metrics = {}
        self.comparison_canvas.figure = self.metrics.create_metrics_comparison({})
        self.comparison_canvas.draw()
        
        # Basarili mesaji goster
        self.status_message("Tum prosesler temizlendi", "info")
    
    def run_algorithm(self):
        """Secilen algoritmayi calistirir"""
        # Prosesler var mi kontrol et
        if self.processes_table.rowCount() == 0:
            error_box = QMessageBox()
            error_box.setIcon(QMessageBox.Warning)
            error_box.setWindowTitle("Hata")
            error_box.setText("Calistirilacak proses yok.")
            error_box.setStandardButtons(QMessageBox.Ok)
            error_box.setStyleSheet(
                "QMessageBox {{ background-color: {}; border: 1px solid {}; border-radius: 5px; }} QPushButton {{ background-color: {}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold; }} QPushButton:hover {{ background-color: #2980b9; }}".format(self.colors['light'], self.colors['accent'], self.colors['primary'])
            )
            error_box.exec_()
            return
        
        # Secilen algoritmayi al
        algorithm_index = self.algorithm_combo.currentIndex()
        algorithm_name = self.algorithm_combo.currentText()
        
        # Algoritma secimine gore zamanlayiciyi calistir
        if algorithm_index == 0:  # FCFS
            self.scheduler.schedule_fcfs()
        elif algorithm_index == 1:  # SJF (Non-preemptive)
            self.scheduler.schedule_sjf(preemptive=False)
        elif algorithm_index == 2:  # SRTF (Preemptive SJF)
            self.scheduler.schedule_sjf(preemptive=True)
        elif algorithm_index == 3:  # Round Robin
            time_quantum = self.time_quantum_spin.value()
            self.scheduler.schedule_round_robin(time_quantum)
        elif algorithm_index == 4:  # Priority (Non-preemptive)
            self.scheduler.schedule_priority(preemptive=False)
        elif algorithm_index == 5:  # Priority (Preemptive)
            self.scheduler.schedule_priority(preemptive=True)
        
        # Metrikleri hesapla
        metrics_dict = self.metrics.calculate_all_metrics()
        
        # Metrik tablosunu guncelle
        self.metrics_table.setItem(0, 1, QTableWidgetItem("{:.2f}".format(metrics_dict['avg_waiting_time'])))
        self.metrics_table.setItem(1, 1, QTableWidgetItem("{:.2f}".format(metrics_dict['avg_turnaround_time'])))
        self.metrics_table.setItem(2, 1, QTableWidgetItem("{:.2f}".format(metrics_dict['avg_response_time'])))
        
        # Gantt semasini guncelle
        self.gantt_canvas.figure = self.metrics.create_gantt_chart()
        self.gantt_canvas.draw()
        
        # Algoritma metriklerini kaydet (karsilastirma icin)
        self.algorithm_metrics[algorithm_name] = metrics_dict
        



    
    def compare_algorithms(self):
        """Tum algoritmalari karsilastirir"""
        # Prosesler var mi kontrol et
        if self.processes_table.rowCount() == 0:
            error_box = QMessageBox()
            error_box.setIcon(QMessageBox.Warning)
            error_box.setWindowTitle("Hata")
            error_box.setText("Karsilastirilacak proses yok.")
            error_box.setStandardButtons(QMessageBox.Ok)
            error_box.setStyleSheet(
                "QMessageBox {{ background-color: {}; border: 1px solid {}; border-radius: 5px; }} QPushButton {{ background-color: {}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold; }} QPushButton:hover {{ background-color: #2980b9; }}".format(self.colors['light'], self.colors['accent'], self.colors['primary'])
            )
            error_box.exec_()
            return
        
        # Mevcut prosesleri yedekle
        original_processes = []
        for i in range(self.processes_table.rowCount()):
            pid = int(self.processes_table.item(i, 0).text())
            arrival_time = int(self.processes_table.item(i, 1).text())
            burst_time = int(self.processes_table.item(i, 2).text())
            priority = int(self.processes_table.item(i, 3).text())
            original_processes.append((pid, arrival_time, burst_time, priority))
        
        # Tum algoritmalari calistir ve sonuclari topla
        algorithm_metrics = {}
        
        # Kullaniciya islemi bildiren mesaj
        self.status_message("Tum algoritma karsilastirmasi yapiliyor...", "info")
        
        # Algoritmalari calistir
        # 1. FCFS
        self.scheduler = CPUScheduler()
        for pid, arrival_time, burst_time, priority in original_processes:
            self.scheduler.add_process(pid, arrival_time, burst_time, priority)
        self.scheduler.schedule_fcfs()
        self.metrics = SchedulingMetrics(self.scheduler)
        algorithm_metrics["FCFS"] = self.metrics.calculate_all_metrics()
        
        # 2. SJF (Non-preemptive)
        self.scheduler = CPUScheduler()
        for pid, arrival_time, burst_time, priority in original_processes:
            self.scheduler.add_process(pid, arrival_time, burst_time, priority)
        self.scheduler.schedule_sjf(preemptive=False)
        self.metrics = SchedulingMetrics(self.scheduler)
        algorithm_metrics["SJF"] = self.metrics.calculate_all_metrics()
        
        # 3. SRTF (Preemptive SJF)
        self.scheduler = CPUScheduler()
        for pid, arrival_time, burst_time, priority in original_processes:
            self.scheduler.add_process(pid, arrival_time, burst_time, priority)
        self.scheduler.schedule_sjf(preemptive=True)
        self.metrics = SchedulingMetrics(self.scheduler)
        algorithm_metrics["SRTF"] = self.metrics.calculate_all_metrics()
        
        # 4. Round Robin
        self.scheduler = CPUScheduler()
        for pid, arrival_time, burst_time, priority in original_processes:
            self.scheduler.add_process(pid, arrival_time, burst_time, priority)
        self.scheduler.schedule_round_robin(self.time_quantum_spin.value())
        self.metrics = SchedulingMetrics(self.scheduler)
        algorithm_metrics["RR"] = self.metrics.calculate_all_metrics()
        
        # 5. Priority (Non-preemptive)
        self.scheduler = CPUScheduler()
        for pid, arrival_time, burst_time, priority in original_processes:
            self.scheduler.add_process(pid, arrival_time, burst_time, priority)
        self.scheduler.schedule_priority(preemptive=False)
        self.metrics = SchedulingMetrics(self.scheduler)
        algorithm_metrics["Priority"] = self.metrics.calculate_all_metrics()
        
        # 6. Priority (Preemptive)
        self.scheduler = CPUScheduler()
        for pid, arrival_time, burst_time, priority in original_processes:
            self.scheduler.add_process(pid, arrival_time, burst_time, priority)
        self.scheduler.schedule_priority(preemptive=True)
        self.metrics = SchedulingMetrics(self.scheduler)
        algorithm_metrics["Priority-P"] = self.metrics.calculate_all_metrics()
        
        # Karsilastirma grafigini guncelle
        self.comparison_canvas.figure = self.metrics.create_metrics_comparison(algorithm_metrics)
        self.comparison_canvas.draw()
        
        # Son zamanlayici durumunu koru
        self.scheduler = CPUScheduler()
        for pid, arrival_time, burst_time, priority in original_processes:
            self.scheduler.add_process(pid, arrival_time, burst_time, priority)
        self.metrics = SchedulingMetrics(self.scheduler)
        
        # Karsilastirma sekmesine gec
        parent = self.parent()
        if parent and hasattr(parent, 'parent') and callable(parent.parent):
            parent_of_parent = parent.parent()
            if parent_of_parent and hasattr(parent_of_parent, 'setCurrentIndex') and callable(parent_of_parent.setCurrentIndex):
                parent_of_parent.setCurrentIndex(2)  # Ust sekme widget'i
        
        # Basarili mesaji goster
        success_box = QMessageBox()
        success_box.setIcon(QMessageBox.Information)
        success_box.setWindowTitle("Basarili")
        success_box.setText("Tum algoritmalar karsilastirildi.")
        success_box.setInformativeText("Karsilastirma sonuclarini gormek icin 'Karsilastirma' sekmesine bakin.")
        success_box.setStandardButtons(QMessageBox.Ok)
        success_box.setStyleSheet(
            "QMessageBox {{ background-color: {}; border: 1px solid {}; border-radius: 5px; }} QPushButton {{ background-color: {}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold; }} QPushButton:hover {{ background-color: #27ae60; }}".format(self.colors['light'], self.colors['secondary'], self.colors['secondary'])
        )
        success_box.exec_()
    
    def status_message(self, message, type="info"):
        """
        Durumu gunceller ve gecici bir mesaj gosterir
        
        Parametreler:
        message (str): Gosterilecek mesaj
        type (str): Mesaj tipi ('info', 'success', 'warning', 'error')
        """
        # Ust pencereyi bul
        main_window = self.window()
        if hasattr(main_window, 'status_label'):
            status_label = main_window.status_label
            
            # Mesaj tipine gore stili ayarla
            if type == "success":
                style = "color: {}; font-weight: bold;".format(self.colors['secondary'])
            elif type == "warning":
                style = "color: #f39c12; font-weight: bold;"
            elif type == "error":
                style = "color: {}; font-weight: bold;".format(self.colors['accent'])
            else:  # info
                style = "color: {}; font-weight: bold;".format(self.colors['primary'])
            
            # Durumu guncelle
            status_label.setStyleSheet(style)
            status_label.setText(message)