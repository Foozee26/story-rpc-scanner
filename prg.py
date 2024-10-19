import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QDialog, QMenu
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPalette, QColor, QFont
import csv
import vlc

class ValidatorUtilityApp(QWidget):
    def __init__(self):
        super().__init__()

        self.moving = False  # Pencereyi taşımak için flag

        # Ana layout
        vbox = QVBoxLayout()

        # Özel neon başlık
        self.title_label = QLabel("Story", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.title_label.setStyleSheet("""
            QLabel {
                color: #39ff14;
                background-color: #000000;
                padding: 10px;
                border: 2px solid #39ff14;
                border-radius: 10px;
            }
        """)
        vbox.addWidget(self.title_label)

        # Pencereyi kapatacak buton (Neon stil)
        self.close_button = self.create_neon_button("X", self.close_app)
        self.close_button.setFixedWidth(50)  # Küçük bir kapatma butonu

        # Kapatma butonunu başlıkla yan yana göstermek için layout
        hbox_title = QHBoxLayout()
        hbox_title.addWidget(self.title_label)
        hbox_title.addWidget(self.close_button)
        vbox.addLayout(hbox_title)

        # VLC oynatıcı kurulum
        self.instance = vlc.Instance()
        self.mediaplayer = self.instance.media_player_new()

        # Video oynatıcı alanı
        self.video_frame = QWidget(self)
        self.video_frame.setStyleSheet("background-color: black;")
        vbox.addWidget(self.video_frame)

        # Neon renkli butonlar (validatörlük işlemleri için)
        self.rpc_button = self.create_neon_button("Show Valid Result", self.show_valid_rpc)
        self.block_sync_button = self.create_neon_button("Show Vulnerable Validators Result", self.show_vulnerable_validators)
        self.performance_button = self.create_neon_button("StartNew Scan", self.start_new_scan)

        # Butonları tutacak alt layout
        hbox = QHBoxLayout()
        hbox.addWidget(self.rpc_button)
        hbox.addWidget(self.block_sync_button)
        hbox.addWidget(self.performance_button)

        vbox.addLayout(hbox)
        self.setLayout(vbox)

        # Pencere stil ayarları (Başlığı ve çerçeveyi gizliyoruz)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Arka planı siyah yapmak için palet ayarları
        self.set_background_black()

        # Pencereyi konumlandırma ve boyutlandırma
        self.setGeometry(100, 100, 800, 600)

        # Video başlatma ve otomatik döngü
        self.play_video()

    def create_neon_button(self, text, function):
        button = QPushButton(text)
        button.setStyleSheet("""
            QPushButton {
                background-color: #000000;
                color: #39ff14;
                border: 2px solid #39ff14;
                border-radius: 10px;
                padding: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #39ff14;
                color: #000000;
            }
        """)
        button.clicked.connect(function)
        return button

    def set_background_black(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(0, 0, 0))
        self.setPalette(palette)

    def play_video(self):
        # Video dosyasının tam yolunu ayarlayın
        video_path = os.path.abspath("hero-v2-desktop.mp4")
        
        # Medya ayarla ve oynat
        self.media = self.instance.media_new(video_path)
        self.mediaplayer.set_media(self.media)

        # Video oynatma alanını VLC'ye bağla
        if sys.platform == "win32":  # Windows platformu için
            self.mediaplayer.set_hwnd(self.video_frame.winId())
        else:  # Diğer platformlar için
            self.mediaplayer.set_xwindow(self.video_frame.winId())

        # Videoyu sürekli döndürme ayarları
        self.mediaplayer.play()

        # Video bittiğinde başa sarmak için timer ayarı
        self.timer = QTimer(self)
        self.timer.setInterval(1000)  # Her saniyede bir kontrol
        self.timer.timeout.connect(self.loop_video)
        self.timer.start()

    def loop_video(self):
        # Video bittiğinde başa sarmayı kontrol et
        if self.mediaplayer.get_state() == vlc.State.Ended:
            self.mediaplayer.stop()
            self.mediaplayer.play()

    # Pencereyi kapatmak için fonksiyon
    def close_app(self):
        self.close()

    # Pencere taşınabilirlik işlevleri (fare ile sürüklemek için)
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.moving = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.moving:
            self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.moving = False

    # Valid RPC Sonuçları Gösterme
    def show_valid_rpc(self):
        self.show_csv_data('results/valid_rpc.csv')

    # Vulnerable Validators Sonuçları Gösterme
    def show_vulnerable_validators(self):
        self.show_csv_data('results/vulnerable_validators.csv')

    # CSV Verilerini Tablo Olarak Gösterme
    def show_csv_data(self, file_path):
        try:
            print(f"Opening file: {file_path}")
            with open(file_path, newline='') as csvfile:
                reader = csv.reader(csvfile)
                data = list(reader)

                if not data:
                    print(f"File is empty: {file_path}")
                    return

                # Yeni bir QDialog ile sonuçları göstermek
                dialog = QDialog(self)
                dialog.setWindowTitle("Results")
                dialog.setGeometry(100, 100, 800, 600)
                dialog.setStyleSheet("background-color: #000000;")  # Arka plan siyah

                # QTableWidget ile tablo oluşturma
                table_widget = QTableWidget(len(data) - 1, len(data[0]))
                table_widget.setHorizontalHeaderLabels(data[0])

                # Neon stil uygulama
                table_widget.setStyleSheet("""
                    QTableWidget {
                        background-color: #000000;
                        color: #39ff14;
                        gridline-color: #39ff14;
                        font-size: 14px;
                    }
                    QHeaderView::section {
                        background-color: #39ff14;
                        color: #000000;
                    }
                """)

                # Satırları doldurma ve sağ tık menüsü ekleme
                for i, row in enumerate(data[1:]):
                    for j, cell in enumerate(row):
                        item = QTableWidgetItem(cell)
                        item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # Kopyalanabilir yapma
                        table_widget.setItem(i, j, item)

                # Sağ tıklama menüsü eklemek için event
                table_widget.setContextMenuPolicy(Qt.CustomContextMenu)
                table_widget.customContextMenuRequested.connect(lambda pos: self.create_context_menu(pos, table_widget))

                layout = QVBoxLayout()
                layout.addWidget(table_widget)
                dialog.setLayout(layout)

                dialog.exec_()

        except Exception as e:
            print(f"Error: {e}")

    # Sağ tıklama menüsü
    def create_context_menu(self, pos, table_widget):
        context_menu = QMenu(self)
        copy_action = context_menu.addAction("Copy")
        copy_action.triggered.connect(lambda: self.copy_selected_cell(table_widget))
        context_menu.exec_(table_widget.mapToGlobal(pos))

    # Seçili hücreyi kopyalama
    def copy_selected_cell(self, table_widget):
        selected_item = table_widget.selectedItems()
        if selected_item:
            clipboard = QApplication.clipboard()
            clipboard.setText(selected_item[0].text())

    # Yeni RPC Tarama Başlatma
    def start_new_scan(self):
        python_path = "C:/Users/x1001/AppData/Local/Programs/Python/Python313/python.exe"
        os.system(f'{python_path} scan.py')
        print("New scan started...")

# Uygulamayı başlat
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ValidatorUtilityApp()
    window.show()
    sys.exit(app.exec_())
