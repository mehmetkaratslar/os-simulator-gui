"""
Banker's Algoritması
Bu modül, deadlock önleme için Banker's algoritmasını uygular.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

class BankersAlgorithm:
    """Banker's algoritmasını uygulayan sınıf"""
    
    def __init__(self):
        """Banker's algoritmasını başlatır"""
        self.processes = []  # Proses ID'leri
        self.resources = []  # Kaynak türleri
        
        # Matrislerin başlangıç değerleri
        self.available = None  # Mevcut kaynaklar vektörü
        self.max_claim = None  # Maksimum talep matrisi
        self.allocation = None  # Tahsis matrisi
        self.need = None  # İhtiyaç matrisi (max_claim - allocation)
    
    def setup(self, process_ids, resource_ids, available_resources):
        """
        Algoritma için kaynakları ve prosesleri ayarlar
        
        Parametreler:
        process_ids (list): Proses ID'leri listesi
        resource_ids (list): Kaynak türü ID'leri listesi
        available_resources (list): Her kaynak türü için mevcut örnek sayısı
        """
        self.processes = process_ids
        self.resources = resource_ids
        
        n_processes = len(process_ids)
        n_resources = len(resource_ids)
        
        # Matrisleri sıfırla
        self.available = np.array(available_resources, dtype=int)
        self.max_claim = np.zeros((n_processes, n_resources), dtype=int)
        self.allocation = np.zeros((n_processes, n_resources), dtype=int)
        self.need = np.zeros((n_processes, n_resources), dtype=int)
    
    def set_max_claim(self, process_idx, resource_claims):
        """
        Bir proses için maksimum kaynak taleplerini ayarlar
        
        Parametreler:
        process_idx (int): Proses dizini
        resource_claims (list): Her kaynak türü için maksimum talep
        """
        if not (0 <= process_idx < len(self.processes)):
            raise ValueError("Geçersiz proses dizini")
        
        if len(resource_claims) != len(self.resources):
            raise ValueError("Kaynak talepleri sayısı, kaynak türleri sayısı ile eşleşmiyor")
        
        self.max_claim[process_idx] = np.array(resource_claims, dtype=int)
        # İhtiyaç matrisini güncelle
        self.need[process_idx] = self.max_claim[process_idx] - self.allocation[process_idx]
    
    def allocate_resources(self, process_idx, resource_allocation):
        """
        Bir proses için kaynakları tahsis eder
        
        Parametreler:
        process_idx (int): Proses dizini
        resource_allocation (list): Her kaynak türü için tahsis edilecek miktar
        
        Dönüş:
        bool: Tahsisat başarılı ise True, değilse False
        """
        if not (0 <= process_idx < len(self.processes)):
            raise ValueError("Geçersiz proses dizini")
        
        if len(resource_allocation) != len(self.resources):
            raise ValueError("Kaynak tahsisatları sayısı, kaynak türleri sayısı ile eşleşmiyor")
        
        allocation = np.array(resource_allocation, dtype=int)
        
        # Mevcut kaynaklar yeterli mi?
        if any(allocation > self.available):
            return False
        
        # Maksimum taleplere uygun mu?
        new_allocation = self.allocation[process_idx] + allocation
        if any(new_allocation > self.max_claim[process_idx]):
            return False
        
        # Kaynakları tahsis et
        self.allocation[process_idx] += allocation
        self.available -= allocation
        self.need[process_idx] = self.max_claim[process_idx] - self.allocation[process_idx]
        
        return True
    
    def release_resources(self, process_idx, resource_release):
        """
        Bir prosesin kaynaklarını serbest bırakır
        
        Parametreler:
        process_idx (int): Proses dizini
        resource_release (list): Her kaynak türü için serbest bırakılacak miktar
        
        Dönüş:
        bool: Serbest bırakma başarılı ise True, değilse False
        """
        if not (0 <= process_idx < len(self.processes)):
            raise ValueError("Geçersiz proses dizini")
        
        if len(resource_release) != len(self.resources):
            raise ValueError("Serbest bırakılan kaynaklar sayısı, kaynak türleri sayısı ile eşleşmiyor")
        
        release = np.array(resource_release, dtype=int)
        
        # Tahsis edilmiş kaynaklar yeterli mi?
        if any(release > self.allocation[process_idx]):
            return False
        
        # Kaynakları serbest bırak
        self.allocation[process_idx] -= release
        self.available += release
        self.need[process_idx] = self.max_claim[process_idx] - self.allocation[process_idx]
        
        return True
    
    def is_safe_state(self):
        """
        Sistemin güvenli durumda olup olmadığını kontrol eder
        
        Dönüş:
        (bool, list): (Güvenli durumda ise True, değilse False), Güvenli sıralama (eğer varsa)
        """
        # Çalışma kopyaları oluştur
        work = self.available.copy()
        finish = np.zeros(len(self.processes), dtype=bool)
        
        # Güvenli sıralama
        safe_sequence = []
        
        # Tüm prosesler tamamlanana kadar
        while not all(finish):
            found = False
            
            for i in range(len(self.processes)):
                # Proses tamamlanmamışsa ve ihtiyaçları karşılanabiliyorsa
                if not finish[i] and all(self.need[i] <= work):
                    # İşlemi "tamamla" ve kaynaklarını serbest bırak
                    work += self.allocation[i]
                    finish[i] = True
                    safe_sequence.append(self.processes[i])
                    found = True
                    break
            
            # Hiçbir proses için ilerleme sağlanamadıysa döngüyü sonlandır
            if not found:
                break
        
        # Tüm prosesler tamamlandı mı?
        is_safe = all(finish)
        
        return is_safe, safe_sequence if is_safe else []
    
    def request_resources(self, process_idx, request):
        """
        Bir proses için kaynak talebini değerlendirir
        
        Parametreler:
        process_idx (int): Proses dizini
        request (list): Her kaynak türü için talep edilen miktar
        
        Dönüş:
        (bool, str): (Talep güvenli ise True, değilse False), Mesaj
        """
        if not (0 <= process_idx < len(self.processes)):
            return False, "Geçersiz proses dizini"
        
        if len(request) != len(self.resources):
            return False, "Talep edilen kaynaklar sayısı, kaynak türleri sayısı ile eşleşmiyor"
        
        request_array = np.array(request, dtype=int)
        
        # Talep, ihtiyaçtan büyük mü?
        if any(request_array > self.need[process_idx]):
            return False, "Talep, maksimum talepten fazla"
        
        # Mevcut kaynaklar yeterli mi?
        if any(request_array > self.available):
            return False, "Yetersiz kaynaklar"
        
        # Talebi geçici olarak tahsis et
        self.allocation[process_idx] += request_array
        self.available -= request_array
        self.need[process_idx] -= request_array
        
        # Güvenlik kontrolü
        is_safe, safe_sequence = self.is_safe_state()
        
        if is_safe:
            # Talep güvenli, tahsisatı koru
            return True, f"Talep güvenli bir şekilde karşılandı. Güvenli sıralama: {safe_sequence}"
        else:
            # Talep güvenli değil, tahsisatı geri al
            self.allocation[process_idx] -= request_array
            self.available += request_array
            self.need[process_idx] += request_array
            return False, "Talep reddedildi çünkü sistem deadlock durumuna girebilir"
    
    def get_state_visualization(self):
        """
        Sistemin mevcut durumunu gösteren görselleştirme
        
        Dönüş:
        Figure: matplotlib Figure nesnesi
        """
        # Proses ve kaynak sayıları
        n_processes = len(self.processes)
        n_resources = len(self.resources)
        
        if n_processes == 0 or n_resources == 0:
            fig = Figure(figsize=(10, 1))
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, "Veri yok", ha='center', va='center')
            return fig
        
        # Figür oluştur
        fig = Figure(figsize=(12, 8))
        
        # 2x2 alt grafikler
        ax1 = fig.add_subplot(221)  # Mevcut kaynaklar
        ax2 = fig.add_subplot(222)  # Maksimum talep
        ax3 = fig.add_subplot(223)  # Tahsis
        ax4 = fig.add_subplot(224)  # İhtiyaç
        
        # Mevcut kaynaklar (Available)
        ax1.bar(range(n_resources), self.available, color='green')
        ax1.set_title('Mevcut Kaynaklar')
        ax1.set_xticks(range(n_resources))
        ax1.set_xticklabels([f'R{r}' for r in self.resources])
        ax1.set_ylabel('Miktar')
        
        # Matris görselleştirme fonksiyonu
        def plot_matrix(ax, matrix, title):
            im = ax.imshow(matrix, cmap='YlGnBu')
            ax.set_title(title)
            ax.set_xticks(range(n_resources))
            ax.set_xticklabels([f'R{r}' for r in self.resources])
            ax.set_yticks(range(n_processes))
            ax.set_yticklabels([f'P{p}' for p in self.processes])
            
            # Değerleri ekle
            for i in range(n_processes):
                for j in range(n_resources):
                    ax.text(j, i, str(matrix[i, j]),
                          ha="center", va="center", color="black")
            
            return im
        
        # Maksimum talep (Max)
        plot_matrix(ax2, self.max_claim, 'Maksimum Talep')
        
        # Tahsis (Allocation)
        plot_matrix(ax3, self.allocation, 'Tahsis')
        
        # İhtiyaç (Need)
        plot_matrix(ax4, self.need, 'İhtiyaç')
        
        # Güvenlik durumu kontrolü
        is_safe, safe_sequence = self.is_safe_state()
        safety_status = f"Sistem {'GÜVENLİ' if is_safe else 'GÜVENSİZ'}"
        if is_safe:
            safety_status += f"\nGüvenli Sıralama: {' -> '.join(str(p) for p in safe_sequence)}"
        
        fig.suptitle(safety_status, fontsize=14, fontweight='bold', 
                  color='green' if is_safe else 'red')
        
        fig.tight_layout()
        fig.subplots_adjust(top=0.85)
        
        return fig