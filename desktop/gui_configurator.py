#!/usr/bin/env python3
"""GUI konfigurator (PyQt) dla desktopowej wersji Hand Wave Slide Controller."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "gesture_config.yaml"
BACKUP_PATH = BASE_DIR / "gesture_config.backup.yaml"

PARAMS = [
    ("detection_confidence", "Detection confidence", float),
    ("tracking_confidence", "Tracking confidence", float),
    ("wave_window_sec", "Okno gestu [s]", float),
    ("wave_min_delta_x_px", "Min. ruch poziomy [px]", int),
    ("wave_max_delta_y_px", "Max. ruch pionowy [px]", int),
    ("min_samples_in_window", "Min. próbki w oknie", int),
    ("min_horizontal_velocity_px_s", "Min. prędkość [px/s]", float),
    ("cooldown_sec", "Cooldown [s]", float),
    ("arm_hold_sec", "Uzbrojenie gestu [s]", float),
    ("min_extended_fingers", "Min. wyprostowane palce", int),
    ("debug_action_flash_duration_sec", "Debug flash [s]", float),
]


class ConfiguratorWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Hand Wave Desktop Configurator (PyQt)")
        self.resize(920, 720)

        self.entries: dict[str, QLineEdit] = {}
        self.defaults: dict[str, Any] = {}
        self.is_dirty = False

        self._build_ui()
        self._build_menu()
        self.load_config()

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)

        title = QLabel("Konfiguracja detekcji gestów (desktop)")
        title.setStyleSheet("font-size: 20px; font-weight: 600;")
        layout.addWidget(title)

        subtitle = QLabel("Zmiany zapisują się do desktop/gesture_config.yaml.")
        subtitle.setStyleSheet("color: #666;")
        layout.addWidget(subtitle)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Szukaj parametru (QoL)")
        self.search.textChanged.connect(self.filter_fields)
        layout.addWidget(self.search)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        form_wrap = QWidget()
        self.form = QFormLayout(form_wrap)
        self.form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        self.form.setFormAlignment(Qt.AlignmentFlag.AlignTop)

        for key, label, _kind in PARAMS:
            edit = QLineEdit()
            edit.setPlaceholderText(f"{key}")
            edit.textChanged.connect(self.mark_dirty)
            self.entries[key] = edit
            self.form.addRow(f"{label}:", edit)

        scroll.setWidget(form_wrap)
        layout.addWidget(scroll, stretch=1)

        actions = QHBoxLayout()
        btn_load = QPushButton("Wczytaj")
        btn_load.clicked.connect(self.load_config)
        btn_save = QPushButton("Zapisz")
        btn_save.clicked.connect(self.save_config)
        btn_restore = QPushButton("Przywróć domyślne")
        btn_restore.clicked.connect(self.restore_defaults)
        btn_backup = QPushButton("Przywróć backup")
        btn_backup.clicked.connect(self.restore_backup)
        actions.addWidget(btn_load)
        actions.addWidget(btn_save)
        actions.addWidget(btn_restore)
        actions.addWidget(btn_backup)
        actions.addStretch(1)
        layout.addLayout(actions)

        roadmap = QWidget()
        roadmap_layout = QHBoxLayout(roadmap)
        for label in [
            "Profile konfiguracji",
            "Kalibracja gestów",
            "Podgląd kamery / ROI",
            "Makra i skróty",
            "Diagnostyka",
            "Aktualizacje",
        ]:
            button = QPushButton(label)
            button.setEnabled(False)
            button.setToolTip("Planowana funkcja - jeszcze niedostępna")
            roadmap_layout.addWidget(button)
        layout.addWidget(QLabel("Planowana rozbudowa GUI (przyciski nieaktywne):"))
        layout.addWidget(roadmap)

        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Gotowe")

    def _build_menu(self) -> None:
        menu = self.menuBar().addMenu("Plik")

        export_action = QAction("Eksportuj konfigurację…", self)
        export_action.triggered.connect(self.export_config)
        menu.addAction(export_action)

        import_action = QAction("Importuj konfigurację…", self)
        import_action.triggered.connect(self.import_config)
        menu.addAction(import_action)

    def mark_dirty(self) -> None:
        self.is_dirty = True
        self.statusBar().showMessage("Niezapisane zmiany")

    def filter_fields(self, text: str) -> None:
        needle = text.lower().strip()
        for i, (key, label, _kind) in enumerate(PARAMS):
            visible = not needle or needle in key.lower() or needle in label.lower()
            self.entries[key].setVisible(visible)
            label_widget = self.form.labelForField(self.entries[key])
            if label_widget is not None:
                label_widget.setVisible(visible)

    def _current_payload(self) -> dict[str, dict[str, Any]]:
        values = {}
        for key, _label, kind in PARAMS:
            raw = self.entries[key].text().strip()
            try:
                values[key] = kind(raw) if raw else kind(0)
            except ValueError as exc:
                raise ValueError(f"{key}: {exc}") from exc
        return {"gesture_detection": values}

    def load_config(self) -> None:
        if not CONFIG_PATH.exists():
            QMessageBox.critical(self, "Błąd", f"Brak pliku konfiguracji: {CONFIG_PATH}")
            return

        data = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}
        gesture = data.get("gesture_detection", {})
        for key, _label, _kind in PARAMS:
            self.entries[key].setText(str(gesture.get(key, "")))

        self.defaults = dict(gesture)
        self.is_dirty = False
        self.statusBar().showMessage("Wczytano konfigurację")

    def save_config(self) -> None:
        try:
            payload = self._current_payload()
        except ValueError as exc:
            QMessageBox.critical(self, "Błąd walidacji", str(exc))
            return

        if CONFIG_PATH.exists():
            BACKUP_PATH.write_text(CONFIG_PATH.read_text(encoding="utf-8"), encoding="utf-8")

        CONFIG_PATH.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")
        self.is_dirty = False
        self.statusBar().showMessage("Zapisano konfigurację")
        QMessageBox.information(self, "Zapisano", "Konfiguracja została zapisana.")

    def restore_defaults(self) -> None:
        if not self.defaults:
            return
        for key, _label, _kind in PARAMS:
            self.entries[key].setText(str(self.defaults.get(key, "")))
        self.statusBar().showMessage("Przywrócono wartości domyślne")

    def restore_backup(self) -> None:
        if not BACKUP_PATH.exists():
            QMessageBox.warning(self, "Brak backupu", f"Nie znaleziono backupu: {BACKUP_PATH}")
            return
        CONFIG_PATH.write_text(BACKUP_PATH.read_text(encoding="utf-8"), encoding="utf-8")
        self.load_config()
        self.statusBar().showMessage("Przywrócono konfigurację z backupu")

    def export_config(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Eksport konfiguracji", str(BASE_DIR / "gesture_export.yaml"), "YAML (*.yaml)")
        if not path:
            return
        payload = self._current_payload()
        Path(path).write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")
        self.statusBar().showMessage("Wyeksportowano konfigurację")

    def import_config(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Import konfiguracji", str(BASE_DIR), "YAML (*.yaml)")
        if not path:
            return
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        gesture = data.get("gesture_detection", {})
        for key, _label, _kind in PARAMS:
            if key in gesture:
                self.entries[key].setText(str(gesture[key]))
        self.statusBar().showMessage("Zaimportowano konfigurację (nie zapisano jeszcze do pliku)")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConfiguratorWindow()
    window.show()
    sys.exit(app.exec())
