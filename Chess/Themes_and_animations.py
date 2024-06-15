from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,QFileDialog, QDialog, QMessageBox, QTextEdit,QStyleFactory
from PyQt5.QtGui import QPainter, QPixmap, QColor, QIcon, QFont, QPalette, QTransform
from PyQt5.QtCore import Qt, QTimer, QSize, QByteArray, QBuffer, QIODevice
import sys

SQ_SIZE = 50
DIM_ROW = 10
DIM_COL = 10
IMAGES = {}

palettes = {
    1: [QColor(180, 180, 150), QColor(40, 40, 50)],   # Default
    2: [QColor(53, 53, 53), QColor(25, 25, 25)],      # Dark Mode
    3: [QColor(215, 215, 215), QColor(225, 225, 225)] # Light Mode
}


class ChessPiece:
    def __init__(self, piece, start_row, start_col):
        self.piece = piece
        self.x = start_col * SQ_SIZE
        self.y = start_row * SQ_SIZE
        self.angle = 0


class StartScreenBoard(QWidget):
    def __init__(self):
        super().__init__()
        self.loadImages()
        self.pieces = [
            # ChessPiece('bp', 0, 0),
            ChessPiece('bN', 0, 0),
            # ChessPiece('bB', 2, 0),
            # ChessPiece('bR', 3, 0),
            # ChessPiece('bQ', 4, 0),
            # ChessPiece('bK', 5, 0)
        ]

        self.setWindowTitle('Szachownica')
        self.setGeometry(100, 100, DIM_COL * SQ_SIZE, DIM_ROW * SQ_SIZE)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(60)  # 50 ms for smooth animation

    def loadImages(self):
        piece_names = ["bR", "bN", "bB", "bQ", "bK", "bp", "wR", "wN", "wB", "wQ", "wK", "wp"]
        
        for piece in piece_names:
            # Ładujemy figury i skalujemy je do rozmiaru pola
            pixmap = QPixmap("Figury_HD/" + piece + ".png")
            pixmap = pixmap.scaled(SQ_SIZE, SQ_SIZE, Qt.KeepAspectRatio)
            IMAGES[piece] = pixmap

    def update_animation(self):
        for piece in self.pieces:
            # piece.x += 1  # Ruch w prawo
            # if piece.x > self.width():
            #     piece.x = -SQ_SIZE  # Powrót na lewą stronę
            piece.angle += 5  # Obrót o 5 stopni
            if piece.angle >= 360:
                piece.angle = 0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        
        # Kolory szachownicy
        light_color = QColor(255, 255, 255)
        dark_color = QColor(0, 0, 0)
        
        # Rysujemy szachownicę
        for row in range(DIM_ROW):
            for col in range(DIM_COL):
                color = light_color if (row + col) % 2 == 0 else dark_color
                painter.fillRect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE, color)
                
        # Rysujemy figury
        for piece in self.pieces:
            pixmap = IMAGES[piece.piece]
            transform = QTransform().translate(piece.x + SQ_SIZE / 2, piece.y + SQ_SIZE / 2).rotate(piece.angle).translate(-SQ_SIZE / 2, -SQ_SIZE / 2)
            painter.setTransform(transform)
            painter.drawPixmap(piece.x, piece.y, SQ_SIZE, SQ_SIZE, pixmap)

        painter.end()



def neonMode(window):
    window.neon_palette = QPalette()
    window.neon_palette.setColor(QPalette.Window, QColor(0, 0, 0))
    window.neon_palette.setColor(QPalette.WindowText, QColor(57, 255, 20))
    window.neon_palette.setColor(QPalette.Button, QColor(0, 0, 0))
    window.neon_palette.setColor(QPalette.ButtonText, QColor(57, 255, 20))
    window.neon_palette.setColor(QPalette.Base, QColor(0, 0, 0))
    window.neon_palette.setColor(QPalette.AlternateBase, QColor(0, 0, 0))
    window.neon_palette.setColor(QPalette.ToolTipBase, QColor(0, 0, 0))
    window.neon_palette.setColor(QPalette.ToolTipText, QColor(57, 255, 20))
    window.neon_palette.setColor(QPalette.Text, QColor(57, 255, 20))
    window.neon_palette.setColor(QPalette.Highlight, QColor(142, 45, 197))
    window.neon_palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))

    # Ustawianie neonowego motywu
    window.setPalette(window.neon_palette)

    # Ustawianie stylu Fusion
    QApplication.setStyle(QStyleFactory.create('Fusion'))
    # window.button.setStyleSheet()
    styleSheet = """
        QPushButton {
            background-color: #000000;
            border: 2px solid #39FF14;
            border-radius: 30px;  /* Zaokrąglone rogi */
            color: #39FF14;
            padding: 10px 20px;
            font-weight: bold;
                                
            font-family: Arial, sans-serif; /* Dodanie niestandardowej czcionki */
            font-size: 13pt; /* Rozmiar czcionki */
        }
        QPushButton:hover {
            background-color: #39FF14;
            color: #000000;
        }
        QPushButton:pressed {
            background-color: #0B0B0B;
            color: #39FF14;
        }
        """
    
    return styleSheet

def darkMode(window):
    window.dark_palette = QPalette()
    window.dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    window.dark_palette.setColor(QPalette.WindowText, Qt.white)
    window.dark_palette.setColor(QPalette.Button, QColor(60, 60, 60))  # Ciemnoszary przycisk
    window.dark_palette.setColor(QPalette.ButtonText, Qt.white)
    window.dark_palette.setColor(QPalette.Base, QColor(40, 40, 40))    # Ciemny kolor tła
    window.dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    window.dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    window.dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    window.dark_palette.setColor(QPalette.Text, Qt.white)
    window.dark_palette.setColor(QPalette.Highlight, QColor(142, 45, 197))
    window.dark_palette.setColor(QPalette.HighlightedText, Qt.black)

    # Ustawianie ciemnego motywu
    window.setPalette(window.dark_palette)

    # Ustawianie stylu Fusion
    QApplication.setStyle(QStyleFactory.create('Fusion'))

    # Stylizacja przycisku
    styleSheet = """
        QPushButton {
            background-color: #505050;  /* Ciemnoszary */
            border: 2px solid #757575; /* Szary obramowanie */
            border-radius: 30px;       /* Zaokrąglone rogi */
            color: #FFFFFF;            /* Biały tekst */
            padding: 10px 20px;
            font-weight: bold;
            
            font-family: Arial, sans-serif; /* Dodanie niestandardowej czcionki */
            font-size: 13pt; /* Rozmiar czcionki */
        }
        QPushButton:hover {
            background-color: #757575; /* Szary tło */
            color: #FFFFFF;            /* Biały tekst */
        }
        QPushButton:pressed {
            background-color: #424242; /* Ciemniejszy szary */
            color: #FFFFFF;            /* Biały tekst */
        }
        """
    
        # # Stylizacja QTextEdit
        # window.text_edit.setStyleSheet("""
        # QTextEdit {
        #     background-color: #424242;
        #     border: 1px solid #757575;
        #     color: #FFFFFF;
        #     padding: 10px;
        #     }
        # """)
    return styleSheet

def lightMode(window):
    window.light_palette = QPalette()
    window.light_palette.setColor(QPalette.Window, QColor(215, 215, 215))
    window.light_palette.setColor(QPalette.WindowText, QColor(50, 50, 50))
    window.light_palette.setColor(QPalette.Button, QColor(173, 216, 230))  # Jasny niebieski przycisk
    window.light_palette.setColor(QPalette.ButtonText, QColor(50, 50, 50))
    window.light_palette.setColor(QPalette.Base, QColor(225, 225, 225))
    window.light_palette.setColor(QPalette.AlternateBase, QColor(240, 240, 240))
    window.light_palette.setColor(QPalette.ToolTipBase, QColor(225, 225, 225))
    window.light_palette.setColor(QPalette.ToolTipText, QColor(50, 50, 50))
    window.light_palette.setColor(QPalette.Text, QColor(50, 50, 50))
    window.light_palette.setColor(QPalette.Highlight, QColor(76, 163, 224))
    window.light_palette.setColor(QPalette.HighlightedText, QColor(225, 225, 225))

    # Ustawianie jasnego motywu
    window.setPalette(window.light_palette)

    # Ustawianie stylu Fusion
    QApplication.setStyle(QStyleFactory.create('Fusion'))

    # Stylizacja przycisku
    # window.button.setStyleSheet()
    styleSheet = """
        QPushButton {
            background-color: #FFFFFF;
            border: 2px solid #2196F3;
            border-radius: 30px;  /* Zaokrąglone rogi */
            color: #2196F3;
            padding: 10px 20px;
            font-weight: bold;
                                
            font-family: Arial, sans-serif; /* Dodanie niestandardowej czcionki */
            font-size: 13pt; /* Rozmiar czcionki */
        }
        QPushButton:hover {
            background-color: #2196F3;
            color: #FFFFFF;
        }
        QPushButton:pressed {
            background-color: #64B5F6;
            color: #FFFFFF;
        }
        """
    return styleSheet

def bridgerToneMode(window):
    window.bridger_palette = QPalette()
    window.bridger_palette.setColor(QPalette.Window, QColor(29, 45, 71))  # Tło okna
    window.bridger_palette.setColor(QPalette.WindowText, QColor(255, 255, 255))  # Tekst okna
    window.bridger_palette.setColor(QPalette.Button, QColor(34, 72, 90))  # Jaśniejszy turkusowy kolor przycisku
    window.bridger_palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))  # Tekst przycisku
    window.bridger_palette.setColor(QPalette.Base, QColor(15, 25, 37))  # Tło tekstu
    window.bridger_palette.setColor(QPalette.AlternateBase, QColor(23, 35, 51))  # Alternatywne tło
    window.bridger_palette.setColor(QPalette.ToolTipBase, QColor(82, 94, 98))  # Tło podpowiedzi
    window.bridger_palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))  # Tekst podpowiedzi
    window.bridger_palette.setColor(QPalette.Text, QColor(255, 255, 255))  # Tekst
    window.bridger_palette.setColor(QPalette.Highlight, QColor(34, 72, 90))  # Kolor zaznaczenia
    window.bridger_palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))  # Tekst zaznaczenia

    # Ustawianie motywu BridgerTone
    window.setPalette(window.bridger_palette)

    # Ustawianie stylu Fusion
    QApplication.setStyle(QStyleFactory.create('Fusion'))

    # Stylizacja przycisku
    # window.button.setStyleSheet()
    styleSheet = """
        QPushButton {
            background-color: #22485A;  /* Jaśniejszy turkusowy kolor - RGB(34, 72, 90) */
            border: 2px solid #172437;  /* RGB(23, 36, 55) */
            border-radius: 30px;  /* Zaokrąglone rogi */
            color: #FFFFFF;
            padding: 10px 20px;
            font-weight: bold;
            font-family: Arial, sans-serif;
            font-size: 13pt; /* Rozmiar czcionki */
        }
        QPushButton:hover {
            background-color: #172437;  /* RGB(23, 36, 55) */
            color: #FFFFFF;
        }
        QPushButton:pressed {
            background-color: #0F1925;  /* RGB(15, 25, 37) */
            color: #FFFFFF;
        }
    """
    return styleSheet



if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = StartScreenBoard()
    window.show()

    sys.exit(app.exec_())

