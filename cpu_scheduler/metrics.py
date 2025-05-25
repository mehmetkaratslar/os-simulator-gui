"""
CPU Zamanlama Metrikleri
Bu modül, CPU zamanlama performans metriklerini hesaplar ve görselleştirir.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

class SchedulingMetrics:
    """Zamanlama metriklerini hesaplayan ve görselleştiren sınıf"""
    
    def __init__(self, scheduler):
        """
        Parametreler:
        scheduler (CPUScheduler): Metriklerin hesaplanacağı zamanlayıcı
        """
        self.scheduler = scheduler
    
    def calculate_all_metrics(self):
        """Tüm metrikleri hesaplar ve bir sözlük olarak döndürür"""
        metrics = {
            'avg_waiting_time': self.scheduler.get_average_waiting_time(),
            'avg_turnaround_time': self.scheduler.get_average_turnaround_time(),
            'avg_response_time': self.scheduler.get_average_response_time(),
            'throughput': len(self.scheduler.processes) / self.scheduler.current_time if self.scheduler.current_time > 0 else 0,
            'cpu_utilization': self.calculate_cpu_utilization()
        }
        return metrics
    
    def calculate_cpu_utilization(self):
        """CPU kullanım oranını hesaplar"""
        if not self.scheduler.gantt_chart or self.scheduler.current_time == 0:
            return 0
        
        # CPU'nun meşgul olduğu toplam süre
        busy_time = sum(end - start for _, start, end in self.scheduler.gantt_chart)
        # CPU kullanım oranı = meşgul süre / toplam süre
        return busy_time / self.scheduler.current_time
    
    def create_gantt_chart(self):
        """
        Gantt şeması görselleştirmesi oluşturur
        
        Dönüş:
        Figure: matplotlib Figure nesnesi
        """
        if not self.scheduler.gantt_chart:
            fig = Figure(figsize=(10, 1))
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, "Henüz çalıştırılmadı", ha='center', va='center')
            return fig
        
        # Benzersiz proses ID'leri
        unique_pids = sorted(set(pid for pid, _, _ in self.scheduler.gantt_chart))
        
        # Her proses için renk ata
        colors = plt.cm.tab10(np.linspace(0, 1, len(unique_pids)))
        color_map = {pid: colors[i] for i, pid in enumerate(unique_pids)}
        
        # Figür oluştur
        fig = Figure(figsize=(12, 6))
        ax = fig.add_subplot(111)
        
        # Y ekseni etiketlerini ayarla
        ax.set_yticks([])
        ax.set_xlabel('Zaman')
        ax.set_title('CPU Zamanlama Gantt Şeması')
        
        # Gantt şemasını çiz
        for pid, start, end in self.scheduler.gantt_chart:
            ax.barh(0, end - start, left=start, height=0.5, 
                  color=color_map[pid], edgecolor='black')
            # Proses ID'sini çubuğun üzerine yaz
            if end - start > 0.5:  # Sadece yeterince geniş ise metin ekle
                ax.text((start + end) / 2, 0, f'P{pid}', 
                      ha='center', va='center', color='black', fontweight='bold')
        
        # X ekseni ızgaralarını ekle
        ax.grid(axis='x', linestyle='--', alpha=0.7)
        
        return fig
    
    def create_metrics_comparison(self, metrics_dict):
        """
        Farklı zamanlama algoritmaları için metrikleri karşılaştıran görselleştirme
        
        Parametreler:
        metrics_dict (dict): Algoritma adı -> metrik sözlüğü eşlemesi
        
        Dönüş:
        Figure: matplotlib Figure nesnesi
        """
        if not metrics_dict:
            fig = Figure(figsize=(10, 1))
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, "Veri yok", ha='center', va='center')
            return fig
        
        # Metrik türleri
        metric_types = ['avg_waiting_time', 'avg_turnaround_time', 'avg_response_time']
        metric_labels = ['Ortalama Bekleme Süresi', 'Ortalama Toplam İşlem Süresi', 'Ortalama Cevap Süresi']
        
        # Algoritma adları
        algorithm_names = list(metrics_dict.keys())
        
        # Figür oluştur
        fig = Figure(figsize=(12, 8))
        ax = fig.add_subplot(111)
        
        # Çubuk genişliği ve konumu
        bar_width = 0.25
        positions = np.arange(len(algorithm_names))
        
        # Her metrik için çubuk oluştur
        for i, (metric_type, metric_label) in enumerate(zip(metric_types, metric_labels)):
            values = [metrics_dict[alg].get(metric_type, 0) for alg in algorithm_names]
            ax.bar(positions + i * bar_width, values, bar_width, label=metric_label)
        
        # Eksen ayarları
        ax.set_ylabel('Süre (birim zaman)')
        ax.set_title('CPU Zamanlama Algoritmaları Metrik Karşılaştırması')
        ax.set_xticks(positions + bar_width)
        ax.set_xticklabels(algorithm_names)
        ax.legend()
        
        # Izgara ekle
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Çubuk etiketleri ekle
        for i, metric_type in enumerate(metric_types):
            values = [metrics_dict[alg].get(metric_type, 0) for alg in algorithm_names]
            for j, value in enumerate(values):
                ax.text(positions[j] + i * bar_width, value + 0.1, f'{value:.2f}',
                      ha='center', va='bottom', fontsize=8)
        
        return fig