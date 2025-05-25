"""
Yardımcı Fonksiyonlar
Bu modül, projenin çeşitli bölümlerinde kullanılan yardımcı fonksiyonları içerir.
"""

import time
import os
import platform
import psutil
import numpy as np
from datetime import datetime

def format_time(seconds):
    """
    Saniye cinsinden zamanı biçimlendirir
    
    Parametreler:
    seconds (float): Biçimlendirilecek saniye değeri
    
    Dönüş:
    str: Biçimlendirilmiş zaman (mm:ss veya hh:mm:ss)
    """
    if seconds < 3600:
        # Dakika:saniye formatı
        minutes, seconds = divmod(int(seconds), 60)
        return f"{minutes:02d}:{seconds:02d}"
    else:
        # Saat:dakika:saniye formatı
        hours, remainder = divmod(int(seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def format_timestamp(timestamp):
    """
    Unix zaman damgasını insan tarafından okunabilir biçime dönüştürür
    
    Parametreler:
    timestamp (float): Unix zaman damgası
    
    Dönüş:
    str: Biçimlendirilmiş tarih ve saat
    """
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def get_system_info():
    """
    Sistem bilgilerini toplar
    
    Dönüş:
    dict: Sistemin bilgilerini içeren sözlük
    """
    info = {
        'os': platform.system(),
        'os_version': platform.version(),
        'architecture': platform.architecture()[0],
        'processor': platform.processor(),
        'hostname': platform.node(),
        'python_version': platform.python_version(),
        'total_memory': psutil.virtual_memory().total,
        'available_memory': psutil.virtual_memory().available,
        'cpu_count': psutil.cpu_count(logical=False),
        'logical_cpu_count': psutil.cpu_count(logical=True),
        'cpu_usage': psutil.cpu_percent(interval=0.1, percpu=True),
        'boot_time': psutil.boot_time()
    }
    
    return info

def format_bytes(bytes_value, precision=2):
    """
    Bayt değerini insan tarafından okunabilir biçime dönüştürür
    
    Parametreler:
    bytes_value (int): Bayt cinsinden değer
    precision (int): Ondalık basamak sayısı
    
    Dönüş:
    str: Biçimlendirilmiş değer (KB, MB, GB vb.)
    """
    if bytes_value < 0:
        return "0 B"
    
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
    i = 0
    
    while bytes_value >= 1024 and i < len(suffixes) - 1:
        bytes_value /= 1024
        i += 1
    
    return f"{bytes_value:.{precision}f} {suffixes[i]}"

def calculate_statistics(data):
    """
    Verilen veri kümesi için temel istatistikleri hesaplar
    
    Parametreler:
    data (list/array): Sayısal veri dizisi
    
    Dönüş:
    dict: İstatistik değerlerini içeren sözlük
    """
    if not data:
        return {
            'min': 0,
            'max': 0,
            'mean': 0,
            'median': 0,
            'std_dev': 0
        }
    
    data_array = np.array(data)
    
    stats = {
        'min': np.min(data_array),
        'max': np.max(data_array),
        'mean': np.mean(data_array),
        'median': np.median(data_array),
        'std_dev': np.std(data_array)
    }
    
    return stats

def get_process_priority_name(priority):
    """
    Sayısal öncelik değerini metin karşılığına dönüştürür
    
    Parametreler:
    priority (int): Öncelik değeri
    
    Dönüş:
    str: Öncelik ismi
    """
    # Windows öncelik sınıfları
    if platform.system() == 'Windows':
        priorities = {
            64: "Idle",
            16384: "Below Normal",
            32: "Normal",
            32768: "Above Normal",
            128: "High",
            256: "Realtime"
        }
        
        return priorities.get(priority, f"Unknown ({priority})")
    
    # Unix nice değerleri
    else:
        if priority < -10:
            return "Very High"
        elif -10 <= priority < 0:
            return "High"
        elif priority == 0:
            return "Normal"
        elif 0 < priority <= 10:
            return "Low"
        else:
            return "Very Low"

def is_deadlock(graph, resources, processes):
    """
    Kaynak tahsis grafında döngü kontrolü yapar
    
    Parametreler:
    graph (dict): Kaynak tahsis grafı
    resources (list): Kaynak listesi
    processes (list): Proses listesi
    
    Dönüş:
    tuple: (Deadlock var mı, döngü)
    """
    # Proses bekleme grafı oluştur
    wait_for = {p: [] for p in processes}
    
    # Her proses için, talep ettiği ve başka bir proses tarafından kullanılan kaynakları bul
    for p1 in processes:
        for r in resources:
            # Eğer p1 r kaynağını talep ediyorsa
            if (p1, r) in graph.get('request', set()):
                # r kaynağını hangi proseslerin kullandığını bul
                for p2 in processes:
                    if p2 != p1 and (r, p2) in graph.get('allocation', set()):
                        # p1 prosesi, p2 prosesinin serbest bırakmasını bekliyor
                        wait_for[p1].append(p2)
    
    # Döngü arama algoritması
    def find_cycle(node, path, visited):
        if node in path:
            # Döngü bulundu
            cycle_start = path.index(node)
            return path[cycle_start:]
        
        if node in visited:
            return None
        
        visited.add(node)
        path.append(node)
        
        for neighbor in wait_for[node]:
            cycle = find_cycle(neighbor, path, visited)
            if cycle:
                return cycle
        
        path.pop()
        return None
    
    # Her prosesten başlayarak döngü ara
    for p in processes:
        visited = set()
        cycle = find_cycle(p, [], visited)
        if cycle:
            return True, cycle
    
    return False, []

def round_robin_next_process(processes, current_index, time_quantum):
    """
    Round Robin algoritması için bir sonraki prosesi belirler
    
    Parametreler:
    processes (list): Proses listesi
    current_index (int): Mevcut proses indeksi
    time_quantum (int): Zaman dilimi
    
    Dönüş:
    tuple: (Sonraki proses indeksi, çalışma süresi)
    """
    if not processes:
        return None, 0
    
    # Çalışabilir prosesler
    runnable = [i for i, p in enumerate(processes) if p['remaining_time'] > 0]
    
    if not runnable:
        return None, 0
    
    # Sonraki proses indeksi
    next_index = (current_index + 1) % len(processes)
    while next_index not in runnable:
        next_index = (next_index + 1) % len(processes)
    
    # Çalışma süresi
    run_time = min(time_quantum, processes[next_index]['remaining_time'])
    
    return next_index, run_time