# -*- coding: utf-8 -*-
"""
Deadlock Algilama
Bu modul, kaynak tahsis grafi kullanarak deadlock durumlarini algilar.
"""

import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

class DeadlockDetector:
    """Kaynak tahsis grafi ile deadlock algilayan sinif"""
    
    def __init__(self):
        """Deadlock algilayicisini baslatir"""
        self.resource_allocation_graph = nx.DiGraph()
        self.processes = set()  # Prosesler kumesi
        self.resources = set()  # Kaynaklar kumesi
    
    def reset(self):
        """Grafigi sifirlar"""
        self.resource_allocation_graph = nx.DiGraph()
        self.processes = set()
        self.resources = set()
    
    def add_resource(self, resource_id, instances=1):
        """
        Yeni bir kaynak ekler
        
        Parametreler:
        resource_id (str/int): Kaynagin benzersiz kimligi
        instances (int): Kaynak orneklerinin sayisi
        """
        self.resources.add(resource_id)
        self.resource_allocation_graph.add_node(f"R{resource_id}", type='resource', instances=instances, allocated=0)
    
    def add_process(self, process_id):
        """
        Yeni bir proses ekler
        
        Parametreler:
        process_id (str/int): Prosesin benzersiz kimligi
        """
        self.processes.add(process_id)
        self.resource_allocation_graph.add_node(f"P{process_id}", type='process')
    
    def allocate_resource(self, process_id, resource_id, instances=1):
        """
        Proses icin bir kaynak tahsis eder
        
        Parametreler:
        process_id (str/int): Kaynagi isteyen proses
        resource_id (str/int): Talep edilen kaynak
        instances (int): Talep edilen kaynak orneklerinin sayisi
        
        Donus:
        bool: Tahsisat basarili ise True, degilse False
        """
        process_node = f"P{process_id}"
        resource_node = f"R{resource_id}"
        
        # Proses ve kaynak var mi kontrol et
        if process_node not in self.resource_allocation_graph.nodes or resource_node not in self.resource_allocation_graph.nodes:
            return False
        
        # Kaynagin yeterli ornegi var mi kontrol et
        resource_data = self.resource_allocation_graph.nodes[resource_node]
        if resource_data['allocated'] + instances > resource_data['instances']:
            return False
        
        # Kaynak -> Proses kenari olustur (tahsis)
        if self.resource_allocation_graph.has_edge(resource_node, process_node):
            # Kenar zaten varsa, agirligi artir
            current_weight = self.resource_allocation_graph.edges[resource_node, process_node]['weight']
            self.resource_allocation_graph.edges[resource_node, process_node]['weight'] = current_weight + instances
        else:
            # Yeni kenar olustur
            self.resource_allocation_graph.add_edge(resource_node, process_node, weight=instances, type='allocation')
        
        # Tahsis sayisini guncelle
        resource_data['allocated'] += instances
        
        return True
    
    def request_resource(self, process_id, resource_id, instances=1):
        """
        Prosesin bir kaynak talebini ekler
        
        Parametreler:
        process_id (str/int): Kaynagi isteyen proses
        resource_id (str/int): Talep edilen kaynak
        instances (int): Talep edilen kaynak orneklerinin sayisi
        """
        process_node = f"P{process_id}"
        resource_node = f"R{resource_id}"
        
        # Proses ve kaynak var mi kontrol et
        if process_node not in self.resource_allocation_graph.nodes or resource_node not in self.resource_allocation_graph.nodes:
            return
        
        # Proses -> Kaynak kenari olustur (talep)
        if self.resource_allocation_graph.has_edge(process_node, resource_node):
            # Kenar zaten varsa, agirligi artir
            current_weight = self.resource_allocation_graph.edges[process_node, resource_node]['weight']
            self.resource_allocation_graph.edges[process_node, resource_node]['weight'] = current_weight + instances
        else:
            # Yeni kenar olustur
            self.resource_allocation_graph.add_edge(process_node, resource_node, weight=instances, type='request')
    
    def release_resource(self, process_id, resource_id, instances=1):
        """
        Prosesin bir kaynagi serbest birakmasini saglar
        
        Parametreler:
        process_id (str/int): Kaynagi serbest birakan proses
        resource_id (str/int): Serbest birakilan kaynak
        instances (int): Serbest birakilan kaynak orneklerinin sayisi
        
        Donus:
        bool: Serbest birakma basarili ise True, degilse False
        """
        process_node = f"P{process_id}"
        resource_node = f"R{resource_id}"
        
        # Proses ve kaynak var mi kontrol et
        if process_node not in self.resource_allocation_graph.nodes or resource_node not in self.resource_allocation_graph.nodes:
            return False
        
        # Kaynak -> Proses kenari var mi kontrol et (tahsis)
        if not self.resource_allocation_graph.has_edge(resource_node, process_node):
            return False
        
        # Kenarin agirligini kontrol et
        current_weight = self.resource_allocation_graph.edges[resource_node, process_node]['weight']
        if instances > current_weight:
            return False
        
        # Agirligi guncelle veya kenari kaldir
        if instances < current_weight:
            self.resource_allocation_graph.edges[resource_node, process_node]['weight'] = current_weight - instances
        else:
            self.resource_allocation_graph.remove_edge(resource_node, process_node)
        
        # Tahsis sayisini guncelle
        resource_data = self.resource_allocation_graph.nodes[resource_node]
        resource_data['allocated'] -= instances
        
        return True
    
    def detect_deadlock(self):
        """
        Grafikte deadlock olup olmadigini kontrol eder
        
        Donus:
        list: Deadlock iceren dongudeki dugumler, deadlock yoksa bos liste
        """
        # Sadece proseslerden alinabilecek kaynaklara yonelik kenarlari iceren alt graf olustur
        wait_for_graph = nx.DiGraph()
        
        # Proses dugumlerini ekle
        for process in self.processes:
            process_node = f"P{process}"
            wait_for_graph.add_node(process_node)
        
        # Proses A -> Kaynak R -> Proses B seklindeki yollari incele
        for process_a in self.processes:
            process_a_node = f"P{process_a}"
            
            # Proses A'nin talep ettigi kaynaklari bul
            for _, resource_node in self.resource_allocation_graph.out_edges(process_a_node):
                
                # Bu kaynak bir proses tarafindan tahsis edilmis mi?
                for process_b_node in self.resource_allocation_graph.successors(resource_node):
                    if process_b_node != process_a_node:  # Kendisine kenar ekleme
                        # Proses A, Proses B'nin sahip oldugu bir kaynagi bekliyor
                        wait_for_graph.add_edge(process_a_node, process_b_node)
        
        # Dongu bul
        try:
            cycle = nx.find_cycle(wait_for_graph, orientation='original')
            return [node for node, _ in cycle]
        except nx.NetworkXNoCycle:
            return []
    
    def get_resource_allocation_graph(self):
        """Kaynak tahsis grafini dondurur"""
        return self.resource_allocation_graph
    
    def visualize_graph(self):
        """
        Kaynak tahsis grafini gorsellestirir
        
        Donus:
        Figure: matplotlib Figure nesnesi
        """
        if not self.resource_allocation_graph:
            fig = Figure(figsize=(10, 1))
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, "Graf bos", ha='center', va='center')
            return fig
        
        # Figure olustur
        fig = Figure(figsize=(12, 8))
        ax = fig.add_subplot(111)
        
        # Node pozisyonlarini belirle (yatay katmanlar halinde)
        pos = {}
        process_nodes = [n for n in self.resource_allocation_graph.nodes() if n.startswith('P')]
        resource_nodes = [n for n in self.resource_allocation_graph.nodes() if n.startswith('R')]
        
        # Prosesler ustte, kaynaklar altta
        for i, node in enumerate(process_nodes):
            pos[node] = (i * 2, 1)
        
        for i, node in enumerate(resource_nodes):
            pos[node] = (i * 2, 0)
        
        # Dugumleri ciz
        process_color = 'skyblue'
        resource_color = 'lightgreen'
        
        nx.draw_networkx_nodes(self.resource_allocation_graph, pos, 
                             nodelist=process_nodes, node_color=process_color, 
                             node_size=500, ax=ax)
        
        nx.draw_networkx_nodes(self.resource_allocation_graph, pos, 
                             nodelist=resource_nodes, node_color=resource_color, 
                             node_size=500, node_shape='s', ax=ax)  # Kare sekli
        
        # Dugum etiketlerini ciz
        nx.draw_networkx_labels(self.resource_allocation_graph, pos, ax=ax)
        
        # Tahsis kenarlarini ciz (Kaynak -> Proses)
        allocation_edges = [(u, v) for u, v, d in self.resource_allocation_graph.edges(data=True) 
                           if d.get('type') == 'allocation']
        
        nx.draw_networkx_edges(self.resource_allocation_graph, pos, 
                             edgelist=allocation_edges, 
                             edge_color='green', 
                             width=2.0,
                             arrowstyle='->', 
                             arrowsize=20, 
                             ax=ax)
        
        # Talep kenarlarini ciz (Proses -> Kaynak)
        request_edges = [(u, v) for u, v, d in self.resource_allocation_graph.edges(data=True) 
                        if d.get('type') == 'request']
        
        nx.draw_networkx_edges(self.resource_allocation_graph, pos, 
                             edgelist=request_edges, 
                             edge_color='red', 
                             style='dashed',
                             width=2.0,
                             arrowstyle='->', 
                             arrowsize=20, 
                             ax=ax)
        
        # Kenar agirliklarini ciz
        edge_labels = {(u, v): d.get('weight', '') for u, v, d in self.resource_allocation_graph.edges(data=True)}
        nx.draw_networkx_edge_labels(self.resource_allocation_graph, pos, edge_labels=edge_labels, ax=ax)
        
        # Deadlock kontrolu
        deadlock_cycle = self.detect_deadlock()
        if deadlock_cycle:
            ax.set_title("Kaynak Tahsis Grafi - DEADLOCK TESPIT EDILDI!", color='red', fontweight='bold')
            # Deadlock dongusundeki dugumleri vurgula
            nx.draw_networkx_nodes(self.resource_allocation_graph, pos, 
                                 nodelist=deadlock_cycle, 
                                 node_color='red', 
                                 node_size=700,
                                 ax=ax)
        else:
            ax.set_title("Kaynak Tahsis Grafi - Deadlock Yok", fontweight='bold')
        
        # Eksen etiketlerini kaldir
        ax.set_axis_off()
        
        # Aciklama ekle
        process_patch = plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=process_color, markersize=15, label='Proses')
        resource_patch = plt.Line2D([0], [0], marker='s', color='w', markerfacecolor=resource_color, markersize=15, label='Kaynak')
        allocation_patch = plt.Line2D([0], [0], color='green', lw=2, label='Tahsis')
        request_patch = plt.Line2D([0], [0], color='red', lw=2, linestyle='--', label='Talep')
        
        ax.legend(handles=[process_patch, resource_patch, allocation_patch, request_patch], 
                loc='best', framealpha=0.7)
        
        # Grafigi dondur
        return fig