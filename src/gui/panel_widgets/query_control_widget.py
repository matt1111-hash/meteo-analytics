"""
QueryControlWidget - Lekérdezés és Megszakítás Gombok Widget

Felelősség: CSAK a fetch/cancel gombok állapotának kezelése
- Fetch gomb: elemzés indítása
- Cancel gomb: futó elemzés megszakítása  
- State management: fetching/idle állapotok között váltás
- Clean interface: egyszerű signal-ok kifelé

Nem tudja: mi az elemzés tartalma, hol fut, mennyi ideig tart
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QLabel, QProgressBar
)
from PySide6.QtCore import Signal, QTimer
from PySide6.QtGui import QIcon


class QueryControlWidget(QWidget):
    """
    SINGLE RESPONSIBILITY: Fetch/Cancel gombok kezelése
    
    KIMENŐ JELEK:
    - fetch_requested(): Felhasználó lekérdezést kért
    - cancel_requested(): Felhasználó megszakítást kért
    
    BEMENŐ METÓDUSOK:
    - set_fetching_state(bool): Külső vezérlés a gomb állapotokról
    - set_progress_text(str): Opcionális progress szöveg megjelenítése
    """
    
    # === CLEAN INTERFACE SIGNALS ===
    fetch_requested = Signal()     # Egyszerű jelzés: "Indítsuk el!"
    cancel_requested = Signal()    # Egyszerű jelzés: "Állítsuk le!"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_fetching = False
        self._setup_ui()
        self._connect_signals()
        
    def _setup_ui(self):
        """UI elemek létrehozása és elrendezése"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # === FETCH GOMB ===
        self.fetch_button = QPushButton("🔍 Lekérdezés Indítása")
        self.fetch_button.setMinimumHeight(35)
        self.fetch_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        
        # === CANCEL GOMB ===
        self.cancel_button = QPushButton("⏹️ Megszakítás")
        self.cancel_button.setMinimumHeight(35)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        
        # === PROGRESS LABEL ===
        self.progress_label = QLabel("")
        self.progress_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-style: italic;
                padding: 0px 10px;
            }
        """)
        
        # === PROGRESS BAR (opcionális) ===
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)  # Kezdetben rejtett
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 3px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 2px;
            }
        """)
        
        # === LAYOUT ÖSSZEÁLLÍTÁS ===
        layout.addWidget(self.fetch_button)
        layout.addWidget(self.cancel_button)
        layout.addWidget(self.progress_label)
        layout.addWidget(self.progress_bar)
        layout.addStretch()  # Kitölti a maradék helyet
        
        # === KEZDŐ ÁLLAPOT ===
        self._update_button_states()
        
    def _connect_signals(self):
        """Belső signal connections"""
        self.fetch_button.clicked.connect(self._on_fetch_clicked)
        self.cancel_button.clicked.connect(self._on_cancel_clicked)
        
    def _on_fetch_clicked(self):
        """
        FETCH GOMB ESEMÉNY
        Nem tudja mi az elemzés, csak jelzi hogy indítani kell
        """
        if not self._is_fetching:
            self.fetch_requested.emit()  # CLEAN SIGNAL - tartalommentes
            
    def _on_cancel_clicked(self):
        """
        CANCEL GOMB ESEMÉNY  
        Nem tudja mi fut, csak jelzi hogy meg kell szakítani
        """
        if self._is_fetching:
            self.cancel_requested.emit()  # CLEAN SIGNAL - tartalommentes
            
    # === PUBLIC INTERFACE METHODS ===
    
    def set_fetching_state(self, is_fetching: bool):
        """
        KÜLSŐ VEZÉRLÉS: Gomb állapotok beállítása
        
        Args:
            is_fetching (bool): True = folyamatban, False = várakozás
        """
        if self._is_fetching != is_fetching:
            self._is_fetching = is_fetching
            self._update_button_states()
            
    def set_progress_text(self, text: str = ""):
        """
        OPCIONÁLIS PROGRESS SZÖVEG
        
        Args:
            text (str): Megjelenítendő szöveg (pl. "Adatok letöltése...")
        """
        self.progress_label.setText(text)
        
    def set_progress_value(self, value: int = 0, maximum: int = 100):
        """
        OPCIONÁLIS PROGRESS BAR
        
        Args:
            value (int): Jelenlegi érték
            maximum (int): Maximum érték
        """
        if value > 0 and maximum > 0:
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, maximum)
            self.progress_bar.setValue(value)
        else:
            self.progress_bar.setVisible(False)
            
    def get_state(self) -> dict:
        """
        ÁLLAPOT LEKÉRDEZÉS
        Konzisztencia a többi widget-tel
        
        Returns:
            dict: Widget jelenlegi állapota
        """
        return {
            'is_fetching': self._is_fetching,
            'progress_text': self.progress_label.text(),
            'progress_visible': self.progress_bar.isVisible()
        }
        
    # === PRIVATE HELPER METHODS ===
        
    def _update_button_states(self):
        """Gomb állapotok frissítése a fetching state alapján"""
        if self._is_fetching:
            # FETCHING ÁLLAPOT
            self.fetch_button.setText("⏳ Elemzés Folyamatban...")
            self.fetch_button.setEnabled(False)
            self.cancel_button.setEnabled(True)
            self.cancel_button.setVisible(True)
        else:
            # IDLE ÁLLAPOT
            self.fetch_button.setText("🔍 Lekérdezés Indítása")
            self.fetch_button.setEnabled(True)
            self.cancel_button.setEnabled(False)
            self.cancel_button.setVisible(False)  # Elrejtjük ha nincs mit megszakítani
            self.set_progress_text("")  # Progress szöveg törlése
            self.set_progress_value(0)  # Progress bar elrejtése


# === USAGE EXAMPLE ===
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QVBoxLayout, QMainWindow
    import sys
    
    class TestWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("QueryControlWidget Test")
            self.setGeometry(100, 100, 600, 200)
            
            # Central widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)
            
            # Test widget
            self.query_widget = QueryControlWidget()
            layout.addWidget(self.query_widget)
            
            # Connect signals for testing
            self.query_widget.fetch_requested.connect(self._test_fetch)
            self.query_widget.cancel_requested.connect(self._test_cancel)
            
            # Test timer for simulating work
            self.test_timer = QTimer()
            self.test_timer.timeout.connect(self._test_finish)
            
        def _test_fetch(self):
            print("🔍 FETCH REQUESTED - Szimuláljuk a munkát...")
            self.query_widget.set_fetching_state(True)
            self.query_widget.set_progress_text("Elemzés folyamatban...")
            # Szimuláljuk a 3 másodperces munkát
            self.test_timer.start(3000)
            
        def _test_cancel(self):
            print("⏹️ CANCEL REQUESTED - Munka megszakítása...")
            self.test_timer.stop()
            self.query_widget.set_fetching_state(False)
            
        def _test_finish(self):
            print("✅ MUNKA BEFEJEZVE")
            self.test_timer.stop()
            self.query_widget.set_fetching_state(False)
    
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())
