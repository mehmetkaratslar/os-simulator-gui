# -*- coding: utf-8 -*-
"""
Kullanici arayuzu modulu
"""

# Ana siniflari dogrudan ice aktar
from gui.cpu_tab import CPUSchedulerTab
from gui.deadlock_tab import DeadlockManagerTab
from gui.process_tab import ProcessManagerTab
# Bu satiri en sona birak
from gui.main_window import MainWindow

__all__ = ['MainWindow', 'CPUSchedulerTab', 'DeadlockManagerTab', 'ProcessManagerTab']

