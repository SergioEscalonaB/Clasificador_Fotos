import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from clasificador.ui.main_window import MainWindow
from clasificador.ui.styles import APP_STYLESHEET


def main():
    # Asegurar renderizado correcto en monitores con escalado High-DPI de Windows
    app = QApplication(sys.argv)
    app.setApplicationName("Clasificador de Fotos")
    app.setOrganizationName("ClasificadorApp")

    # Aplicar hoja de estilos visual
    app.setStyleSheet(APP_STYLESHEET)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
