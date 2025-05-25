"""
CPU Zamanlama Algoritmaları
Bu modül, çeşitli CPU zamanlama algoritmalarını içerir.
"""

class Process:
    """Proses bilgilerini temsil eden sınıf"""
    def __init__(self, pid, arrival_time, burst_time, priority=0):
        self.pid = pid  # Proses ID
        self.arrival_time = arrival_time  # Varış zamanı
        self.burst_time = burst_time  # İşlem süresi
        self.priority = priority  # Öncelik (düşük değer, yüksek öncelik)
        self.remaining_time = burst_time  # Kalan işlem süresi
        self.completion_time = 0  # Tamamlanma zamanı
        self.waiting_time = 0  # Bekleme süresi
        self.turnaround_time = 0  # Toplam işlem süresi
        self.response_time = -1  # İlk CPU ataması zamanı

    def __str__(self):
        return f"Process {self.pid}: arrival={self.arrival_time}, burst={self.burst_time}, priority={self.priority}"


class CPUScheduler:
    """Ana zamanlayıcı sınıf"""
    def __init__(self):
        self.processes = []
        self.gantt_chart = []
        self.current_time = 0
    
    def add_process(self, pid, arrival_time, burst_time, priority=0):
        """Yeni bir proses ekler"""
        self.processes.append(Process(pid, arrival_time, burst_time, priority))
    
    def reset(self):
        """Zamanlayıcıyı sıfırlar"""
        for process in self.processes:
            process.remaining_time = process.burst_time
            process.completion_time = 0
            process.waiting_time = 0
            process.turnaround_time = 0
            process.response_time = -1
        
        self.gantt_chart = []
        self.current_time = 0
    
    def calculate_metrics(self):
        """Performans metriklerini hesaplar"""
        for process in self.processes:
            process.turnaround_time = process.completion_time - process.arrival_time
            process.waiting_time = process.turnaround_time - process.burst_time
    
    def get_average_waiting_time(self):
        """Ortalama bekleme süresini hesaplar"""
        total_waiting_time = sum(process.waiting_time for process in self.processes)
        return total_waiting_time / len(self.processes) if self.processes else 0
    
    def get_average_turnaround_time(self):
        """Ortalama toplam işlem süresini hesaplar"""
        total_turnaround_time = sum(process.turnaround_time for process in self.processes)
        return total_turnaround_time / len(self.processes) if self.processes else 0
    
    def get_average_response_time(self):
        """Ortalama cevap süresini hesaplar"""
        total_response_time = sum(process.response_time - process.arrival_time 
                                  for process in self.processes if process.response_time != -1)
        return total_response_time / len(self.processes) if self.processes else 0
    
    def schedule_fcfs(self):
        """First-Come-First-Serve zamanlama algoritması"""
        # Prosesleri varış zamanına göre sırala
        sorted_processes = sorted(self.processes, key=lambda p: p.arrival_time)
        
        self.reset()
        self.current_time = 0
        
        for process in sorted_processes:
            # Eğer proses henüz varmadıysa, zamanı prosesin varış zamanına ayarla
            if self.current_time < process.arrival_time:
                self.current_time = process.arrival_time
            
            # İlk kez CPU'ya atanıyorsa cevap zamanını kaydet
            if process.response_time == -1:
                process.response_time = self.current_time
            
            # Gantt şemasına ekle
            self.gantt_chart.append((process.pid, self.current_time, self.current_time + process.burst_time))
            
            # Proses tamamlanma zamanını güncelle
            self.current_time += process.burst_time
            process.completion_time = self.current_time
            process.remaining_time = 0
        
        # Metrikleri hesapla
        self.calculate_metrics()
        return self.gantt_chart
    
    def schedule_sjf(self, preemptive=False):
        """
        Shortest Job First zamanlama algoritması
        preemptive=False: Non-preemptive SJF (SRTF)
        preemptive=True: Preemptive SJF (SRTF)
        """
        # Orijinal proses listesini klonla ve tüm prosesleri sıfırla
        self.reset()
        
        remaining_processes = [Process(p.pid, p.arrival_time, p.burst_time, p.priority) 
                              for p in self.processes]
        
        self.current_time = 0
        
        # Tüm prosesler tamamlanana kadar
        while remaining_processes:
            # Varış zamanı şu anki zamandan küçük veya eşit olan prosesleri al
            available_processes = [p for p in remaining_processes if p.arrival_time <= self.current_time]
            
            if not available_processes:
                # Eğer şu anda işlenebilecek proses yoksa, zamanı bir sonraki prosesin varış zamanına ayarla
                next_arrival = min(p.arrival_time for p in remaining_processes)
                self.current_time = next_arrival
                continue
            
            # Kalan işlem süresine göre sırala (en kısa işlem önce)
            available_processes.sort(key=lambda p: p.remaining_time)
            
            # En kısa işlemi seç
            shortest_process = available_processes[0]
            
            # İlk kez CPU'ya atanıyorsa cevap zamanını kaydet
            original_process = next(p for p in self.processes if p.pid == shortest_process.pid)
            if original_process.response_time == -1:
                original_process.response_time = self.current_time
            
            if preemptive:
                # Preemptive SJF (SRTF) - Kesinti olabilir
                next_arrival = float('inf')
                for p in remaining_processes:
                    if p.arrival_time > self.current_time and p.arrival_time < next_arrival:
                        next_arrival = p.arrival_time
                
                # Ya proses tamamlanana kadar ya da bir sonraki proses varışına kadar çalıştır
                run_time = min(shortest_process.remaining_time, 
                              next_arrival - self.current_time if next_arrival != float('inf') else shortest_process.remaining_time)
                
                # Gantt şemasına ekle
                self.gantt_chart.append((shortest_process.pid, self.current_time, self.current_time + run_time))
                
                # Zamanı ve kalan işlem süresini güncelle
                self.current_time += run_time
                shortest_process.remaining_time -= run_time
                
                # Proses tamamlandıysa
                if shortest_process.remaining_time == 0:
                    original_process.completion_time = self.current_time
                    remaining_processes.remove(shortest_process)
            else:
                # Non-preemptive SJF - Kesinti olmaz
                # Gantt şemasına ekle
                self.gantt_chart.append((shortest_process.pid, self.current_time, 
                                       self.current_time + shortest_process.remaining_time))
                
                # Zamanı güncelle ve prosesi tamamlandı olarak işaretle
                self.current_time += shortest_process.remaining_time
                original_process.completion_time = self.current_time
                remaining_processes.remove(shortest_process)
        
        # Metrikleri hesapla
        self.calculate_metrics()
        return self.gantt_chart
    
    def schedule_round_robin(self, time_quantum):
        """Round Robin zamanlama algoritması"""
        # Prosesleri sıfırla
        self.reset()
        
        # Varış zamanlarına göre sıralanmış kuyruk
        queue = []
        remaining_processes = [Process(p.pid, p.arrival_time, p.burst_time, p.priority) 
                              for p in self.processes]
        
        self.current_time = 0
        
        # Tüm prosesler tamamlanana kadar
        while remaining_processes or queue:
            # Varış zamanı şu anki zamandan küçük veya eşit olan yeni prosesleri kuyruğa ekle
            new_arrivals = [p for p in remaining_processes if p.arrival_time <= self.current_time]
            for process in new_arrivals:
                queue.append(process)
                remaining_processes.remove(process)
            
            if not queue:
                # Eğer kuyruk boşsa, zamanı bir sonraki prosesin varış zamanına ayarla
                if remaining_processes:
                    next_arrival = min(p.arrival_time for p in remaining_processes)
                    self.current_time = next_arrival
                continue
            
            # Kuyruktan bir proses al
            current_process = queue.pop(0)
            
            # İlk kez CPU'ya atanıyorsa cevap zamanını kaydet
            original_process = next(p for p in self.processes if p.pid == current_process.pid)
            if original_process.response_time == -1:
                original_process.response_time = self.current_time
            
            # Prosesin kalan işlem süresine göre çalışma süresini belirle
            run_time = min(time_quantum, current_process.remaining_time)
            
            # Gantt şemasına ekle
            self.gantt_chart.append((current_process.pid, self.current_time, self.current_time + run_time))
            
            # Zamanı ve kalan işlem süresini güncelle
            self.current_time += run_time
            current_process.remaining_time -= run_time
            
            # Varış zamanı şu anki zamandan küçük veya eşit olan yeni prosesleri kuyruğa ekle
            new_arrivals = [p for p in remaining_processes if p.arrival_time <= self.current_time]
            for process in new_arrivals:
                queue.append(process)
                remaining_processes.remove(process)
            
            # Proses tamamlanmadıysa, tekrar kuyruğa ekle
            if current_process.remaining_time > 0:
                queue.append(current_process)
            else:
                # Proses tamamlandı
                original_process.completion_time = self.current_time
        
        # Metrikleri hesapla
        self.calculate_metrics()
        return self.gantt_chart
    
    def schedule_priority(self, preemptive=False):
        """
        Priority zamanlama algoritması
        preemptive=False: Non-preemptive Priority
        preemptive=True: Preemptive Priority
        """
        # Prosesleri sıfırla
        self.reset()
        
        remaining_processes = [Process(p.pid, p.arrival_time, p.burst_time, p.priority) 
                              for p in self.processes]
        
        self.current_time = 0
        
        # Tüm prosesler tamamlanana kadar
        while remaining_processes:
            # Varış zamanı şu anki zamandan küçük veya eşit olan prosesleri al
            available_processes = [p for p in remaining_processes if p.arrival_time <= self.current_time]
            
            if not available_processes:
                # Eğer şu anda işlenebilecek proses yoksa, zamanı bir sonraki prosesin varış zamanına ayarla
                next_arrival = min(p.arrival_time for p in remaining_processes)
                self.current_time = next_arrival
                continue
            
            # Önceliğe göre sırala (düşük değer, yüksek öncelik)
            available_processes.sort(key=lambda p: p.priority)
            
            # En yüksek öncelikli prosesi seç
            highest_priority_process = available_processes[0]
            
            # İlk kez CPU'ya atanıyorsa cevap zamanını kaydet
            original_process = next(p for p in self.processes if p.pid == highest_priority_process.pid)
            if original_process.response_time == -1:
                original_process.response_time = self.current_time
            
            if preemptive:
                # Preemptive Priority - Kesinti olabilir
                next_event_time = float('inf')
                
                # Bir sonraki proses varış zamanını bul
                for p in remaining_processes:
                    if p.arrival_time > self.current_time and p.arrival_time < next_event_time:
                        next_event_time = p.arrival_time
                
                # Ya proses tamamlanana kadar ya da bir sonraki proses varışına kadar çalıştır
                run_time = min(highest_priority_process.remaining_time, 
                              next_event_time - self.current_time if next_event_time != float('inf') else highest_priority_process.remaining_time)
                
                # Gantt şemasına ekle
                self.gantt_chart.append((highest_priority_process.pid, self.current_time, self.current_time + run_time))
                
                # Zamanı ve kalan işlem süresini güncelle
                self.current_time += run_time
                highest_priority_process.remaining_time -= run_time
                
                # Proses tamamlandıysa
                if highest_priority_process.remaining_time == 0:
                    original_process.completion_time = self.current_time
                    remaining_processes.remove(highest_priority_process)
            else:
                # Non-preemptive Priority - Kesinti olmaz
                # Gantt şemasına ekle
                self.gantt_chart.append((highest_priority_process.pid, self.current_time, 
                                      self.current_time + highest_priority_process.remaining_time))
                
                # Zamanı güncelle ve prosesi tamamlandı olarak işaretle
                self.current_time += highest_priority_process.remaining_time
                original_process.completion_time = self.current_time
                remaining_processes.remove(highest_priority_process)
        
        # Metrikleri hesapla
        self.calculate_metrics()
        return self.gantt_chart