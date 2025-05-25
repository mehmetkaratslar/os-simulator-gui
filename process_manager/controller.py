"""
Proses Kontrolü
Bu modül, prosesleri başlatma, durdurma ve önceliklerini değiştirme işlevlerini sağlar.
"""

import os
import sys
import psutil
import subprocess

class ProcessController:
    """Prosesleri kontrol eden sınıf"""
    
    def __init__(self):
        """Proses kontrolünü başlatır"""
        # İşletim sistemi tipini tespit et
        self.is_windows = sys.platform.startswith('win')
        self.is_linux = sys.platform.startswith('linux')
        self.is_mac = sys.platform.startswith('darwin')
    
    def start_process(self, command, shell=True):
        """
        Yeni bir proses başlatır
        
        Parametreler:
        command (str): Başlatılacak komut
        shell (bool): Kabuk kullanılsın mı
        
        Dönüş:
        tuple: (başarılı mı, proses ID veya hata mesajı)
        """
        try:
            # Proses başlat
            process = subprocess.Popen(
                command,
                shell=shell,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return True, process.pid
        except Exception as e:
            return False, str(e)
    
    def stop_process(self, pid):
        """
        Bir prosesi durdurur
        
        Parametreler:
        pid (int): Proses ID
        
        Dönüş:
        tuple: (başarılı mı, mesaj)
        """
        try:
            process = psutil.Process(pid)
            process.terminate()
            
            # Termination başarısız olursa, daha sert bir şekilde sonlandır
            try:
                process.wait(timeout=3)
            except psutil.TimeoutExpired:
                process.kill()
            
            return True, f"Proses {pid} durduruldu"
        except psutil.NoSuchProcess:
            return False, f"Proses {pid} bulunamadı"
        except psutil.AccessDenied:
            return False, f"Proses {pid} durdurmak için yetki yetersiz"
        except Exception as e:
            return False, str(e)
    
    def change_priority(self, pid, priority):
        """
        Bir prosesin önceliğini değiştirir
        
        Parametreler:
        pid (int): Proses ID
        priority (str/int): Yeni öncelik ('low', 'normal', 'high' veya sayısal değer)
        
        Dönüş:
        tuple: (başarılı mı, mesaj)
        """
        try:
            process = psutil.Process(pid)
            
            # Metin önceliklerini sayısal değerlere dönüştür
            if isinstance(priority, str):
                priority = priority.lower()
                if self.is_windows:
                    # Windows
                    if priority == 'low':
                        priority_value = psutil.BELOW_NORMAL_PRIORITY_CLASS
                    elif priority == 'normal':
                        priority_value = psutil.NORMAL_PRIORITY_CLASS
                    elif priority == 'high':
                        priority_value = psutil.ABOVE_NORMAL_PRIORITY_CLASS
                    else:
                        return False, f"Geçersiz öncelik: {priority}"
                else:
                    # Linux/Mac (nice değeri)
                    if priority == 'low':
                        priority_value = 10
                    elif priority == 'normal':
                        priority_value = 0
                    elif priority == 'high':
                        priority_value = -10
                    else:
                        return False, f"Geçersiz öncelik: {priority}"
            else:
                # Sayısal değer doğrudan kullan
                priority_value = priority
            
            # Önceliği değiştir
            if self.is_windows:
                process.nice(priority_value)
            else:
                # Linux/Mac
                process.nice(priority_value)
            
            return True, f"Proses {pid} önceliği değiştirildi"
        except psutil.NoSuchProcess:
            return False, f"Proses {pid} bulunamadı"
        except psutil.AccessDenied:
            return False, f"Proses {pid} önceliğini değiştirmek için yetki yetersiz"
        except Exception as e:
            return False, str(e)
    
    def get_process_info(self, pid):
        """
        Bir prosesin detaylı bilgilerini alır
        
        Parametreler:
        pid (int): Proses ID
        
        Dönüş:
        dict: Proses bilgileri sözlüğü veya None
        """
        try:
            process = psutil.Process(pid)
            with process.oneshot():
                process_info = {
                    'pid': pid,
                    'name': process.name(),
                    'status': process.status(),
                    'cpu_percent': process.cpu_percent() / psutil.cpu_count(),
                    'memory_percent': process.memory_percent(),
                    'create_time': process.create_time(),
                    'username': process.username(),
                    'cmdline': process.cmdline(),
                    'nice': process.nice(),
                    'num_threads': process.num_threads(),
                    'io_counters': process.io_counters() if hasattr(process, 'io_counters') else None,
                    'connections': process.connections(),
                    'open_files': process.open_files()
                }
                
                # İşletim sistemine özgü bilgileri ekle
                if self.is_windows:
                    process_info['priority'] = self._get_windows_priority_name(process.nice())
                else:
                    process_info['priority'] = self._get_unix_priority_name(process.nice())
                
                return process_info
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return None
    
    def _get_windows_priority_name(self, priority):
        """Windows öncelik değerini metne dönüştürür"""
        priority_map = {
            psutil.IDLE_PRIORITY_CLASS: "Idle",
            psutil.BELOW_NORMAL_PRIORITY_CLASS: "Below Normal",
            psutil.NORMAL_PRIORITY_CLASS: "Normal",
            psutil.ABOVE_NORMAL_PRIORITY_CLASS: "Above Normal",
            psutil.HIGH_PRIORITY_CLASS: "High",
            psutil.REALTIME_PRIORITY_CLASS: "Realtime"
        }
        return priority_map.get(priority, f"Unknown ({priority})")
    
    def _get_unix_priority_name(self, nice):
        """Unix nice değerini metne dönüştürür"""
        if nice < -10:
            return "Very High"
        elif -10 <= nice < 0:
            return "High"
        elif nice == 0:
            return "Normal"
        elif 0 < nice <= 10:
            return "Low"
        else:
            return "Very Low"