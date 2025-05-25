"""
Proses İzleme
Bu modül, sistemdeki prosesleri gerçek zamanlı olarak izler.
"""

import psutil
import time
import threading
import numpy as np
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

class ProcessMonitor:
    """Sistemdeki prosesleri izleyen sınıf"""
    
    def __init__(self, history_length=60):
        """
        Proses izleyiciyi başlatır
        
        Parametreler:
        history_length (int): Tarihçe uzunluğu (saniye)
        """
        self.history_length = history_length
        self.monitored_processes = {}  # pid -> process_info
        self.running = False
        self.monitor_thread = None
        
        # Zaman serileri için
        self.timestamps = deque(maxlen=history_length)
        # CPU kullanımı için tarihçe (pid -> [kullanım1, kullanım2, ...])
        self.cpu_history = {}
        # Bellek kullanımı için tarihçe (pid -> [bellek1, bellek2, ...])
        self.memory_history = {}
    
    def start_monitoring(self, interval=1.0):
        """
        İzlemeyi başlatır
        
        Parametreler:
        interval (float): Örnekleme aralığı (saniye)
        """
        if self.running:
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """İzlemeyi durdurur"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
            self.monitor_thread = None
    
    def _monitor_loop(self, interval):
        """
        İzleme döngüsü
        
        Parametreler:
        interval (float): Örnekleme aralığı (saniye)
        """
        while self.running:
            try:
                # Mevcut zaman
                current_time = time.time()
                self.timestamps.append(current_time)
                
                # İzlenen tüm prosesleri güncelle
                for pid in list(self.monitored_processes.keys()):
                    try:
                        if not self._update_process_info(pid):
                            # Proses artık mevcut değil
                            self._remove_process(pid)
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        # Proses artık erişilebilir değil
                        self._remove_process(pid)
                        
                # Belirli aralıklarla izleme
                time.sleep(interval)
                
            except Exception as e:
                print(f"İzleme hatası: {e}")
                time.sleep(interval)
    
    def add_process(self, pid):
        """
        İzlenecek yeni bir proses ekler
        
        Parametreler:
        pid (int): Proses ID
        
        Dönüş:
        bool: İşlem başarılı ise True, değilse False
        """
        if pid in self.monitored_processes:
            return True  # Zaten izleniyor
        
        try:
            process = psutil.Process(pid)
            process_info = {
                'pid': pid,
                'name': process.name(),
                'status': process.status(),
                'process': process,
                'cpu_percent': 0.0,
                'memory_percent': 0.0,
                'create_time': process.create_time(),
                'username': process.username()
            }
            
            self.monitored_processes[pid] = process_info
            
            # Zaman serisi verilerini başlat
            empty_history = deque([0.0] * len(self.timestamps), maxlen=self.history_length)
            self.cpu_history[pid] = empty_history.copy()
            self.memory_history[pid] = empty_history.copy()
            
            return True
            
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return False
    
    def remove_process(self, pid):
        """
        İzlenen bir prosesi kaldırır
        
        Parametreler:
        pid (int): Proses ID
        """
        self._remove_process(pid)
    
    def _remove_process(self, pid):
        """
        İzlenen bir prosesi kaldırır (dahili)
        
        Parametreler:
        pid (int): Proses ID
        """
        if pid in self.monitored_processes:
            del self.monitored_processes[pid]
        
        if pid in self.cpu_history:
            del self.cpu_history[pid]
        
        if pid in self.memory_history:
            del self.memory_history[pid]
    
    def _update_process_info(self, pid):
        """
        Proses bilgilerini günceller
        
        Parametreler:
        pid (int): Proses ID
        
        Dönüş:
        bool: İşlem başarılı ise True, değilse False
        """
        if pid not in self.monitored_processes:
            return False
        
        try:
            process_info = self.monitored_processes[pid]
            process = process_info['process']
            
            # Proses durumunu kontrol et
            if not process.is_running():
                return False
            
            # CPU ve bellek kullanımını güncelle
            with process.oneshot():
                cpu_percent = process.cpu_percent()
                memory_percent = process.memory_percent()
                status = process.status()
            
            # Bilgileri güncelle
            process_info['cpu_percent'] = cpu_percent
            process_info['memory_percent'] = memory_percent
            process_info['status'] = status
            
            # Zaman serisi verilerini güncelle
            self.cpu_history[pid].append(cpu_percent)
            self.memory_history[pid].append(memory_percent)
            
            return True
            
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return False
    
    def get_process_info(self, pid):
        """
        Belirli bir prosesin bilgilerini döndürür
        
        Parametreler:
        pid (int): Proses ID
        
        Dönüş:
        dict: Proses bilgileri sözlüğü, proses mevcut değilse None
        """
        return self.monitored_processes.get(pid)
    
    def get_all_processes(self):
        """
        Tüm izlenen proseslerin bilgilerini döndürür
        
        Dönüş:
        dict: pid -> proses bilgileri sözlüğü
        """
        return self.monitored_processes
    
    def get_process_history(self, pid):
        """
        Bir prosesin CPU ve bellek kullanım geçmişini döndürür
        
        Parametreler:
        pid (int): Proses ID
        
        Dönüş:
        tuple: (zaman_dizisi, cpu_geçmişi, bellek_geçmişi)
        """
        if pid not in self.monitored_processes:
            return None, None, None
        
        return list(self.timestamps), list(self.cpu_history[pid]), list(self.memory_history[pid])
    
    def get_system_processes(self, sort_by='cpu_percent', limit=10):
        """
        Sistemdeki tüm prosesleri döndürür (izlenmeyen prosesler dahil)
        
        Parametreler:
        sort_by (str): Sıralama için kullanılacak özellik
        limit (int): Döndürülecek maksimum proses sayısı
        
        Dönüş:
        list: Proses bilgileri sözlüğü listesi
        """
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'username', 'status']):
            try:
                # Proses bilgilerini al
                proc_info = proc.info
                proc_info['cpu_percent'] = proc.cpu_percent() / psutil.cpu_count()
                proc_info['memory_percent'] = proc.memory_percent()
                processes.append(proc_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Kullanıma göre sırala ve sınırla
        return sorted(processes, key=lambda x: x.get(sort_by, 0), reverse=True)[:limit]
    
    def visualize_cpu_usage(self, pids=None):
        """
        İzlenen proseslerin CPU kullanımını görselleştirir
        
        Parametreler:
        pids (list): Görselleştirilecek proses ID'leri, None ise tüm prosesler
        
        Dönüş:
        Figure: matplotlib Figure nesnesi
        """
        if not self.monitored_processes:
            fig = Figure(figsize=(10, 1))
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, "İzlenen proses yok", ha='center', va='center')
            return fig
        
        if pids is None:
            pids = list(self.monitored_processes.keys())
        else:
            # Sadece monitör edilen prosesleri filtrele
            pids = [pid for pid in pids if pid in self.monitored_processes]
        
        if not pids:
            fig = Figure(figsize=(10, 1))
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, "Görselleştirilecek proses bulunamadı", ha='center', va='center')
            return fig
        
        # Figür oluştur
        fig = Figure(figsize=(12, 6))
        ax = fig.add_subplot(111)
        
        # Zaman ekseni
        x_axis = range(len(self.timestamps))
        
        # Her proses için çizgi oluştur
        for pid in pids:
            process_info = self.monitored_processes[pid]
            cpu_data = self.cpu_history[pid]
            label = f"{process_info['name']} (PID: {pid})"
            ax.plot(x_axis, cpu_data, '-', label=label)
        
        # Eksen ayarları
        ax.set_title("Proses CPU Kullanımı Zaman Serisi")
        ax.set_xlabel("Zaman (s)")
        ax.set_ylabel("CPU Kullanımı (%)")
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend()
        
        return fig
    
    def visualize_memory_usage(self, pids=None):
        """
        İzlenen proseslerin bellek kullanımını görselleştirir
        
        Parametreler:
        pids (list): Görselleştirilecek proses ID'leri, None ise tüm prosesler
        
        Dönüş:
        Figure: matplotlib Figure nesnesi
        """
        if not self.monitored_processes:
            fig = Figure(figsize=(10, 1))
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, "İzlenen proses yok", ha='center', va='center')
            return fig
        
        if pids is None:
            pids = list(self.monitored_processes.keys())
        else:
            # Sadece monitör edilen prosesleri filtrele
            pids = [pid for pid in pids if pid in self.monitored_processes]
        
        if not pids:
            fig = Figure(figsize=(10, 1))
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, "Görselleştirilecek proses bulunamadı", ha='center', va='center')
            return fig
        
        # Figür oluştur
        fig = Figure(figsize=(12, 6))
        ax = fig.add_subplot(111)
        
        # Zaman ekseni
        x_axis = range(len(self.timestamps))
        
        # Her proses için çizgi oluştur
        for pid in pids:
            process_info = self.monitored_processes[pid]
            memory_data = self.memory_history[pid]
            label = f"{process_info['name']} (PID: {pid})"
            ax.plot(x_axis, memory_data, '-', label=label)
        
        # Eksen ayarları
        ax.set_title("Proses Bellek Kullanımı Zaman Serisi")
        ax.set_xlabel("Zaman (s)")
        ax.set_ylabel("Bellek Kullanımı (% RAM)")
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend()
        
        return fig