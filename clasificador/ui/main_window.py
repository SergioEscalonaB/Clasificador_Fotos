import os
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QCheckBox,
    QFileDialog,
    QMessageBox,
    QProgressBar,
    QFrame,
    QSplitter,
    QApplication,
)

from clasificador.core.session_manager import SessionManager
from clasificador.core.image_loader import load_image_with_exif
from clasificador.core.file_scanner import format_file_size
from clasificador.core.app_config import get_app_config, save_app_config
from clasificador.ui.image_viewer import ImageViewer
from clasificador.ui.category_panel import CategoryPanel
from clasificador.ui.lucide_icons import get_lucide_icon, get_lucide_pixmap


class MainWindow(QMainWindow):
    """
    Ventana principal de la aplicación Clasificador de Fotos.
    """

    def __init__(self):
        super().__init__()
        self.session = SessionManager()

        self.setWindowTitle("Clasificador Manual de Fotos")
        self.resize(1150, 780)
        self.setMinimumSize(850, 600)

        self._setup_ui()
        self._setup_shortcuts()
        self._load_saved_config()
        self._update_ui_state()

    def _setup_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(14, 14, 14, 14)
        root_layout.setSpacing(12)

        # 1. Panel de Configuración Superior
        root_layout.addWidget(self._create_header_card())

        # 2. Área Central (Visor a la izquierda + Panel de Categorías/Estadísticas a la derecha)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(8)

        # Contenedor Izquierdo: Visor + Información + Navegación
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)

        # Barra de metadatos de la imagen actual
        self.info_card = self._create_info_bar()
        left_layout.addWidget(self.info_card)

        # Visor de Imagen
        self.image_viewer = ImageViewer()
        left_layout.addWidget(self.image_viewer, 1)

        # Barra de navegación inferior
        self.nav_bar = self._create_navigation_bar()
        left_layout.addWidget(self.nav_bar)

        splitter.addWidget(left_container)

        # Contenedor Derecho: Estadísticas + Categorías + Ayuda
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)

        # Tarjeta de Progreso
        self.stats_card = self._create_stats_card()
        right_layout.addWidget(self.stats_card)

        # Panel de Categorías
        self.category_panel = CategoryPanel()
        self.category_panel.setObjectName("categoriesCard")
        self.category_panel.set_categories(self.session.categories)
        self.category_panel.category_selected.connect(self._on_category_selected)
        self.category_panel.category_added.connect(self._on_category_added)
        self.category_panel.category_renamed.connect(self._on_category_renamed)
        self.category_panel.category_removed.connect(self._on_category_removed)
        right_layout.addWidget(self.category_panel, 1)

        # Tarjeta de Ayuda de Atajos
        right_layout.addWidget(self._create_help_card())

        splitter.addWidget(right_container)

        # Proporciones iniciales del divisor (70% visor, 30% panel lateral)
        splitter.setSizes([750, 350])
        root_layout.addWidget(splitter, 1)

    def _create_header_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("headerCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)

        # Fila 1: Carpeta Origen
        row1 = QHBoxLayout()
        lbl_src = QLabel("Carpeta Origen:")
        lbl_src.setFixedWidth(115)
        lbl_src.setStyleSheet("font-weight: 600;")
        self.txt_source = QLineEdit()
        self.txt_source.setPlaceholderText("Selecciona la carpeta que contiene las fotos a clasificar...")
        btn_browse_src = QPushButton("Examinar...")
        btn_browse_src.setIcon(get_lucide_icon("folder", color="#475569", size=15))
        btn_browse_src.setIconSize(QSize(15, 15))
        btn_browse_src.clicked.connect(self._browse_source_folder)

        self.chk_recursive = QCheckBox("Incluir subcarpetas")
        self.chk_recursive.setChecked(True)
        self.chk_recursive.setToolTip("Si está activado, buscará fotos dentro de todas las subcarpetas de origen.")

        row1.addWidget(lbl_src)
        row1.addWidget(self.txt_source, 1)
        row1.addWidget(btn_browse_src)
        row1.addWidget(self.chk_recursive)
        layout.addLayout(row1)

        # Fila 2: Carpeta Destino + Modo Mover + Botón Iniciar
        row2 = QHBoxLayout()
        lbl_dst = QLabel("Carpeta Destino:")
        lbl_dst.setFixedWidth(115)
        lbl_dst.setStyleSheet("font-weight: 600;")
        self.txt_dest = QLineEdit()
        self.txt_dest.setPlaceholderText("Selecciona la carpeta donde se crearán las subcarpetas de categorías...")
        btn_browse_dst = QPushButton("Examinar...")
        btn_browse_dst.setIcon(get_lucide_icon("folder", color="#475569", size=15))
        btn_browse_dst.setIconSize(QSize(15, 15))
        btn_browse_dst.clicked.connect(self._browse_dest_folder)

        self.chk_move = QCheckBox("Mover en vez de copiar")
        self.chk_move.setChecked(False)
        self.chk_move.setToolTip(
            "Por seguridad, el comportamiento predeterminado es COPIAR (no altera los originales).\n"
            "Si activas esta casilla, las fotos se MOVERÁN definitivamente."
        )
        self.chk_move.toggled.connect(self._on_move_mode_toggled)

        self.btn_start = QPushButton("Cargar imágenes / Iniciar")
        self.btn_start.setObjectName("primaryButton")
        self.btn_start.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_start.setIcon(get_lucide_icon("play", color="#ffffff", size=15))
        self.btn_start.setIconSize(QSize(15, 15))
        self.btn_start.clicked.connect(self._start_session)

        row2.addWidget(lbl_dst)
        row2.addWidget(self.txt_dest, 1)
        row2.addWidget(btn_browse_dst)
        row2.addWidget(self.chk_move)
        row2.addWidget(self.btn_start)
        layout.addLayout(row2)

        return card

    def _create_info_bar(self) -> QFrame:
        card = QFrame()
        card.setObjectName("infoBar")
        layout = QHBoxLayout(card)
        layout.setContentsMargins(10, 6, 10, 6)

        self.lbl_filename = QLabel("Sin imagen seleccionada")
        self.lbl_filename.setStyleSheet("font-weight: bold; font-size: 13px; color: #0f172a;")

        self.lbl_filedetails = QLabel("")
        self.lbl_filedetails.setStyleSheet("color: #64748b; font-size: 12px;")

        self.lbl_status_badge = QLabel("")
        self.lbl_status_badge.setStyleSheet("font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 4px;")

        layout.addWidget(self.lbl_filename)
        layout.addWidget(self.lbl_filedetails)
        layout.addStretch()
        layout.addWidget(self.lbl_status_badge)

        return card

    def _create_navigation_bar(self) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.btn_prev = QPushButton("Anterior (Izq)")
        self.btn_prev.setIcon(get_lucide_icon("chevron-left", color="#475569", size=16))
        self.btn_prev.setIconSize(QSize(16, 16))
        self.btn_prev.setToolTip("Ir a la imagen anterior")
        self.btn_prev.clicked.connect(self._on_go_previous)

        self.btn_next = QPushButton("Siguiente (Der)")
        self.btn_next.setIcon(get_lucide_icon("chevron-right", color="#475569", size=16))
        self.btn_next.setIconSize(QSize(16, 16))
        self.btn_next.setToolTip("Ir a la imagen siguiente sin clasificar")
        self.btn_next.clicked.connect(self._on_go_next)

        self.btn_skip = QPushButton("Saltar (Espacio)")
        self.btn_skip.setObjectName("skipButton")
        self.btn_skip.setIcon(get_lucide_icon("skip-forward", color="#475569", size=16))
        self.btn_skip.setIconSize(QSize(16, 16))
        self.btn_skip.setToolTip("Omitir esta imagen y pasar a la siguiente (Espacio)")
        self.btn_skip.clicked.connect(self._on_skip)

        self.btn_undo = QPushButton("Deshacer (Ctrl+Z)")
        self.btn_undo.setObjectName("undoButton")
        self.btn_undo.setIcon(get_lucide_icon("undo", color="#c2410c", size=16))
        self.btn_undo.setIconSize(QSize(16, 16))
        self.btn_undo.setToolTip("Revertir la última clasificación o salto")
        self.btn_undo.clicked.connect(self._on_undo)

        layout.addWidget(self.btn_prev)
        layout.addWidget(self.btn_next)
        layout.addStretch()
        layout.addWidget(self.btn_skip)
        layout.addWidget(self.btn_undo)

        return widget

    def _create_stats_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("statsCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)

        self.lbl_progress_text = QLabel("Progreso: 0 de 0")
        self.lbl_progress_text.setStyleSheet("font-weight: bold; font-size: 14px; color: #0f172a;")
        layout.addWidget(self.lbl_progress_text)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Indicadores numéricos
        badges_layout = QHBoxLayout()
        badges_layout.setSpacing(8)

        self.lbl_count_classified = QLabel("Clasificadas: 0")
        self.lbl_count_classified.setStyleSheet(
            "background-color: #dcfce7; color: #166534; font-weight: 600; "
            "padding: 4px 8px; border-radius: 6px; font-size: 11px;"
        )

        self.lbl_count_pending = QLabel("Pendientes: 0")
        self.lbl_count_pending.setStyleSheet(
            "background-color: #dbeafe; color: #1e40af; font-weight: 600; "
            "padding: 4px 8px; border-radius: 6px; font-size: 11px;"
        )

        self.lbl_count_skipped = QLabel("Saltadas: 0")
        self.lbl_count_skipped.setStyleSheet(
            "background-color: #f1f5f9; color: #475569; font-weight: 600; "
            "padding: 4px 8px; border-radius: 6px; font-size: 11px;"
        )

        badges_layout.addWidget(self.lbl_count_classified)
        badges_layout.addWidget(self.lbl_count_pending)
        badges_layout.addWidget(self.lbl_count_skipped)
        layout.addLayout(badges_layout)

        return card

    def _create_help_card(self) -> QFrame:
        card = QFrame()
        card.setStyleSheet("background-color: #ffffff; border-radius: 10px; border: 1px solid #e2e8f0; padding: 10px;")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)

        title_layout = QHBoxLayout()
        title_icon = QLabel()
        title_icon.setPixmap(get_lucide_pixmap("keyboard", color="#475569", size=15))
        title = QLabel("Atajos de Teclado")
        title.setStyleSheet("font-weight: bold; font-size: 12px; color: #334155;")
        title_layout.addWidget(title_icon)
        title_layout.addWidget(title)
        title_layout.addStretch()
        layout.addLayout(title_layout)

        tips = [
            "• [1-9, 0, Q-P]: Clasificar en categoría",
            "• [Espacio]: Saltar imagen actual",
            "• [Izq / Der]: Navegar anterior / siguiente",
            "• [Ctrl + Z]: Deshacer última clasificación",
        ]
        for tip in tips:
            lbl = QLabel(tip)
            lbl.setStyleSheet("color: #64748b; font-size: 11px;")
            layout.addWidget(lbl)

        return card

    def _setup_shortcuts(self):
        """Configura atajos globales para la ventana."""
        # Deshacer con Ctrl+Z
        shortcut_undo = QShortcut(QKeySequence("Ctrl+Z"), self)
        shortcut_undo.activated.connect(self._on_undo)

        # Saltar con Espacio
        shortcut_skip = QShortcut(QKeySequence(Qt.Key.Key_Space), self)
        shortcut_skip.activated.connect(self._on_skip)

        # Anterior con Flecha Izquierda
        shortcut_prev = QShortcut(QKeySequence(Qt.Key.Key_Left), self)
        shortcut_prev.activated.connect(self._on_go_previous)

        # Siguiente con Flecha Derecha
        shortcut_next = QShortcut(QKeySequence(Qt.Key.Key_Right), self)
        shortcut_next.activated.connect(self._on_go_next)

    def keyPressEvent(self, event):
        """Captura pulsaciones de teclas para atajos numéricos y letras de categorías."""
        # Si un campo de texto tiene el foco, no interceptar
        focused = QApplication.focusWidget()
        if isinstance(focused, QLineEdit):
            super().keyPressEvent(event)
            return

        key_text = event.text().strip().upper()
        if key_text:
            category = self.category_panel.get_category_for_key(key_text)
            if category:
                self._on_category_selected(category)
                return

        super().keyPressEvent(event)

    # --- Persistencia de Configuración y Auto-reanudación ---

    def _load_saved_config(self):
        """Carga la configuración persistente: carpetas recientes y categorías personalizadas del usuario."""
        config = get_app_config()

        # Restaurar categorías previamente definidas por el usuario (o lista vacía)
        saved_cats = config.get("categories")
        if saved_cats is not None:
            self.session.categories = list(saved_cats)
        else:
            self.session.categories = []

        self.category_panel.set_categories(self.session.categories)

        saved_src = config.get("last_source_folder", "")
        saved_dst = config.get("last_destination_folder", "")
        self.chk_recursive.setChecked(config.get("recursive_scan", True))
        self.chk_move.setChecked(config.get("move_mode", False))

        if saved_src and os.path.isdir(saved_src):
            self.txt_source.setText(saved_src)
        if saved_dst and os.path.isdir(saved_dst):
            self.txt_dest.setText(saved_dst)

        # Si ambas carpetas existen en disco, reanudar sesión automáticamente de forma inmediata
        if saved_src and os.path.isdir(saved_src) and saved_dst and os.path.isdir(saved_dst):
            self._start_session(auto_resume=True)

    def _save_current_config(self):
        """Guarda la configuración actual para recordar carpetas y categorías personalizadas."""
        config = {
            "last_source_folder": self.txt_source.text().strip(),
            "last_destination_folder": self.txt_dest.text().strip(),
            "recursive_scan": self.chk_recursive.isChecked(),
            "move_mode": self.chk_move.isChecked(),
            "categories": self.session.categories,
        }
        save_app_config(config)

    # --- Acciones de Configuración y Rutas ---

    def _browse_source_folder(self):
        current = self.txt_source.text() or os.path.expanduser("~")
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta de Origen con Fotos", current)
        if folder:
            self.txt_source.setText(os.path.abspath(folder))
            self._save_current_config()

    def _browse_dest_folder(self):
        current = self.txt_dest.text() or self.txt_source.text() or os.path.expanduser("~")
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta de Destino para Clasificación", current)
        if folder:
            abs_folder = os.path.abspath(folder)
            self.txt_dest.setText(abs_folder)
            self._save_current_config()
            self._check_and_prompt_resume(abs_folder)

    def _check_and_prompt_resume(self, dest_folder: str):
        """Verifica si ya existe progreso en la carpeta de destino y ofrece reanudarlo."""
        if SessionManager.has_existing_session(dest_folder):
            summary = SessionManager.read_session_summary(dest_folder)
            if summary and summary.get("total", 0) > 0:
                classified = summary.get("classified", 0)
                total = summary.get("total", 0)
                saved_src = summary.get("source_folder", "")

                msg = (
                    f"Se encontró una sesión de trabajo previa en esta carpeta de destino.\n\n"
                    f"• Fotos clasificadas previamente: {classified} de {total}\n"
                    f"• Carpeta origen registrada: {saved_src or 'No registrada'}\n\n"
                    "¿Deseas reanudar el avance previo sin duplicar las fotos ya clasificadas?"
                )
                reply = QMessageBox.question(
                    self,
                    "Reanudar Sesión Previa",
                    msg,
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes,
                )
                if reply == QMessageBox.StandardButton.Yes:
                    if saved_src and not self.txt_source.text():
                        self.txt_source.setText(saved_src)
                    self._start_session(auto_resume=True)

    def _on_move_mode_toggled(self, checked: bool):
        if checked:
            reply = QMessageBox.warning(
                self,
                "Confirmación de Seguridad - Modo Mover",
                "ATENCIÓN: El modo predeterminado y más seguro es COPIAR.\n\n"
                "Al activar el modo MOVER, los archivos originales serán trasladados "
                "de su carpeta de origen a la carpeta de destino.\n\n"
                "¿Estás seguro de que deseas activar el modo Mover?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                self.chk_move.blockSignals(True)
                self.chk_move.setChecked(False)
                self.chk_move.blockSignals(False)
        self._save_current_config()

    def _start_session(self, auto_resume: bool = False):
        source_dir = self.txt_source.text().strip()
        dest_dir = self.txt_dest.text().strip()

        if not source_dir or not os.path.isdir(source_dir):
            if not auto_resume:
                QMessageBox.warning(self, "Carpeta de Origen Requerida", "Por favor selecciona una carpeta de origen válida.")
            return

        if not dest_dir:
            if not auto_resume:
                QMessageBox.warning(self, "Carpeta de Destino Requerida", "Por favor selecciona una carpeta de destino para organizar las fotos.")
            return

        # Prevenir que la carpeta destino sea idéntica a la de origen en modo mover sin cuidado
        if os.path.abspath(source_dir) == os.path.abspath(dest_dir) and not auto_resume:
            reply = QMessageBox.question(
                self,
                "Carpetas Coincidentes",
                "La carpeta de destino es la misma que la de origen.\n"
                "Se crearán las subcarpetas de categorías dentro de ella.\n¿Deseas continuar?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        # Inicializar sesión
        recursive = self.chk_recursive.isChecked()
        move_mode = self.chk_move.isChecked()

        total = self.session.initialize_session(
            source_folder=source_dir,
            destination_folder=dest_dir,
            recursive=recursive,
            move_mode=move_mode,
            categories=self.session.categories,
            resume_existing=True,
        )

        if total == 0:
            if not auto_resume:
                subfolder_hint = " (prueba marcando 'Incluir subcarpetas')" if not recursive else ""
                QMessageBox.information(
                    self,
                    "Sin Imágenes",
                    f"No se encontraron imágenes compatibles en la carpeta:\n{source_dir}{subfolder_hint}\n\n"
                    "Formatos aceptados: JPG, JPEG, PNG, BMP, GIF, TIFF, WEBP.",
                )
            self.image_viewer.set_placeholder("No se encontraron imágenes en la carpeta de origen.")
        else:
            self.category_panel.set_categories(self.session.categories)

        self._save_current_config()
        self._load_current_image()
        self._update_ui_state()

    # --- Acciones de Clasificación y Navegación ---

    def _on_category_selected(self, category_name: str):
        if not self.session.items:
            return

        item = self.session.get_current_item()
        if not item:
            return

        self.session.move_mode = self.chk_move.isChecked()

        success, err = self.session.classify_current(category_name)
        if not success:
            QMessageBox.critical(
                self,
                "Error al Clasificar",
                f"No se pudo guardar la imagen en la categoría '{category_name}':\n\n{err}\n\n"
                "La imagen NO ha sido marcada como clasificada.",
            )
            return

        self._load_current_image()
        self._update_ui_state()

    def _on_skip(self):
        if not self.session.items:
            return
        self.session.skip_current()
        self._load_current_image()
        self._update_ui_state()

    def _on_undo(self):
        if not self.session.history:
            return

        success, err = self.session.undo_last()
        if not success:
            QMessageBox.warning(
                self,
                "Error al Deshacer",
                f"No se pudo revertir la última acción:\n\n{err}",
            )
            return

        self._load_current_image()
        self._update_ui_state()

    def _on_go_previous(self):
        if self.session.go_previous():
            self._load_current_image()
            self._update_ui_state()

    def _on_go_next(self):
        if self.session.go_next():
            self._load_current_image()
            self._update_ui_state()

    # --- Gestión de Categorías ---

    def _on_category_added(self, name: str):
        success, err = self.session.add_category(name)
        if success:
            self.category_panel.set_categories(self.session.categories)
            self._save_current_config()
        else:
            QMessageBox.warning(self, "No se pudo agregar", err or "Error desconocido.")

    def _on_category_renamed(self, old_name: str, new_name: str):
        success, err = self.session.rename_category(old_name, new_name)
        if success:
            self.category_panel.set_categories(self.session.categories)
            self._update_info_bar()
            self._save_current_config()
        else:
            QMessageBox.warning(self, "No se pudo renombrar", err or "Error desconocido.")

    def _on_category_removed(self, name: str):
        success, err = self.session.remove_category(name)
        if success:
            self.category_panel.set_categories(self.session.categories)
            self._save_current_config()
        else:
            QMessageBox.warning(self, "No se pudo eliminar", err or "Error desconocido.")

    # --- Carga y Renderizado de Imagen ---

    def _load_current_image(self):
        item = self.session.get_current_item()
        if not item:
            if self.session.items:
                self.image_viewer.set_placeholder("¡Todas las imágenes han sido clasificadas!")
            else:
                self.image_viewer.set_placeholder("Selecciona la carpeta origen y presiona 'Cargar imágenes'.")
            self._clear_info_bar()
            return

        src_path = item["src_path"]
        pixmap, error_msg, metadata = load_image_with_exif(src_path)

        if error_msg:
            self.image_viewer.set_error(error_msg)
        else:
            self.image_viewer.set_image(pixmap)

        self._update_info_bar(metadata)

    def _update_info_bar(self, metadata: Optional[dict] = None):
        item = self.session.get_current_item()
        if not item:
            self._clear_info_bar()
            return

        src = item["src_path"]
        filename = os.path.basename(src)
        self.lbl_filename.setText(filename)
        self.lbl_filename.setToolTip(src)

        details = []
        if metadata:
            w = metadata.get("width", 0)
            h = metadata.get("height", 0)
            fmt = metadata.get("format", "")
            size_b = metadata.get("size_bytes", 0)
            if w and h:
                details.append(f"{w} × {h} px")
            if fmt:
                details.append(fmt)
            if size_b:
                details.append(format_file_size(size_b))

        self.lbl_filedetails.setText(f"  |  {' • '.join(details)}" if details else "")

        status = item.get("status", "pending")
        if status == "classified":
            cat = item.get("category", "")
            self.lbl_status_badge.setText(f"Clasificada en: {cat}")
            self.lbl_status_badge.setStyleSheet(
                "background-color: #dcfce7; color: #166534; font-weight: bold; padding: 2px 8px; border-radius: 4px;"
            )
        elif status == "skipped":
            self.lbl_status_badge.setText("Omitida")
            self.lbl_status_badge.setStyleSheet(
                "background-color: #f1f5f9; color: #475569; font-weight: bold; padding: 2px 8px; border-radius: 4px;"
            )
        else:
            self.lbl_status_badge.setText("Pendiente")
            self.lbl_status_badge.setStyleSheet(
                "background-color: #dbeafe; color: #1e40af; font-weight: bold; padding: 2px 8px; border-radius: 4px;"
            )

    def _clear_info_bar(self):
        self.lbl_filename.setText("Sin imagen activa")
        self.lbl_filedetails.setText("")
        self.lbl_status_badge.setText("")

    def _update_ui_state(self):
        """Actualiza el estado de botones, barra de progreso y contadores."""
        stats = self.session.get_stats()
        total = stats["total"]
        classified = stats["classified"]
        skipped = stats["skipped"]
        pending = stats["pending"]
        curr_display = stats["current_display"]

        # Textos de estadísticas
        if total > 0:
            self.lbl_progress_text.setText(f"Progreso: {curr_display} de {total}")
            pct = int((classified / total) * 100) if total > 0 else 0
            self.progress_bar.setValue(pct)
            self.progress_bar.setFormat(f"{pct}% ({classified}/{total})")
        else:
            self.lbl_progress_text.setText("Progreso: 0 de 0")
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("0%")

        self.lbl_count_classified.setText(f"Clasificadas: {classified}")
        self.lbl_count_pending.setText(f"Pendientes: {pending}")
        self.lbl_count_skipped.setText(f"Saltadas: {skipped}")

        # Habilitación de botones
        has_items = total > 0
        self.btn_prev.setEnabled(stats["has_previous"])
        self.btn_next.setEnabled(stats["has_next"])
        self.btn_skip.setEnabled(has_items)
        self.btn_undo.setEnabled(stats["can_undo"])

    def closeEvent(self, event):
        """Al cerrar la aplicación, guardar el progreso y la configuración automáticamente."""
        self._save_current_config()
        self.session.save_progress()
        event.accept()
