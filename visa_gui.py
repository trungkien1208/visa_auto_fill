"""Pink‑themed modern PyQt5 GUI for the China‑Visa autofill helper
Author  : Luu Trung Kien (luutrungkien120894@gmail.com)
Position: Senior Software Engineer
"""

import sys
import threading
import queue
from pathlib import Path
import os

# Let the browser installation logic handle the path automatically
# The ensure_browsers_available() function will set the correct path


from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject, pyqtSlot, QMetaObject, Q_ARG, Q_RETURN_ARG, QEventLoop
from PyQt5.QtGui import QFont, QIntValidator
from PyQt5.QtWidgets import (
    QHBoxLayout, 
    QApplication,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QCheckBox,
    QTextEdit,
    QWidget,
    QSizePolicy,
)

# ----------- business imports (same as before) ---------------------------
from visa_autofill import main as run_visa_autofill
# ---------------- default config -----------------------------------------
PLUS_DAY_TO_DATE = 4
DATA_FILE = "application.xlsx"
EMAIL_LOGIN = "hientrang24hvisa@gmail.com"
PASSWORD_LOGIN = "@Trang126"
LOGIN_URL = "https://www.visaforchina.cn/user/login?site=SGN3_EN"
HEADLESS = False
USE_EXISTING_BROWSER = True
AUTO_NEXT = False
QUICK_FORM_URL = "https://consular.mfa.gov.cn/VISA/?visadata=eyJndWlkIjoiMTcwOTcxMjk0MDU0OTAiLCJleHBpcmVzX2luIjoiIiwidG1wX3NlY3JldCI6InZjZW50ZXJfMTcwOTcxMjk0MDU0OTBfOWEwZGE2MjZkODVmYWE5NzBjYTMzYzJlZjdmYmIxNjlfMTkxODM3MzhfMTc1MTM4OTU5MzE3MF9iOTBhYzA5ZTc1MDQ4ZTlmNTBmMGU2MWI5MWViYTM2YiIsInRva2VuIjoiWW1WallXWmpOVGxoWkRFM1kyVmhNMlE0TkdJMU9XUXlOemxtT0RGa056QXpObUl6T0RBeU0yTXhPR05pWm1JMk1tVmlPRE01TmpVek0yVmxPV1JtTlE9PSIsImxhbmciOiJlbl9VUyIsImVtYmFzc3lJZCI6IlZOTUIiLCJwYWdlcyI6Im5vZGUiLCJ1aWQiOiIyYTM4ZDUzYTdjYzI0ZmRhYTgxYjVhNGM1YzJlNzUzMCIsImVtYWlsIjoiaGllbnRyYW5nMjRodmlzYUBnbWFpbC5jb20iLCJwbHQiOiJ2Y2VudGVyIn0%3D"  # shortened for brevity
FORM_URL = "https://consular.mfa.gov.cn/VISA/node"
CURRENT_INDEX = 0
# ---------------- UI helper ----------------------------------------------
class LogEmitter(QObject):
    new_text = pyqtSignal(str)


class GateKeeperStream:
    """Redirect stdout/stderr to a Qt‑safe signal emitter."""

    def __init__(self, emitter: LogEmitter):
        self._emitter = emitter

    def write(self, text):
        if text:
            self._emitter.new_text.emit(text)

    def flush(self):
        pass


# ------------------------------------------------------------------------
class VisaAutofillWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("China Visa Autofill")
        self.setMinimumSize(1000, 700)  # Increased minimum size for better responsiveness
        self.resize(1200, 800)  # Set initial size
        
        # Make window resizable
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # enable gradient background & window‑specific styling
        self.setObjectName("VisaAutofillWindow")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        # ---------------- header area -----------------
        self._title_lbl = QLabel("China Visa Autofill Helper")
        self._title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title_lbl.setFont(QFont("Helvetica", 28, QFont.Bold))  # Use system font
        self._title_lbl.setStyleSheet("""
            color: #2196F3;
            padding: 8px;
            border-radius: 8px;
            font-weight: bold;
            background: rgba(33, 150, 243, 0.1);
        """)

        self._payment_lbl = QLabel("(Payment pending)")
        self._payment_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._payment_lbl.setFont(QFont("Helvetica", 12))  # Use system font
        self._payment_lbl.setStyleSheet("""
            color: #f44336; 
            padding: 4px 12px;
            border-radius: 4px;
            background: rgba(244, 67, 54, 0.1);
            margin-top: 8px;
        """)
        header_widget = QWidget()
        header_layout = QGridLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setHorizontalSpacing(0)
        header_layout.setVerticalSpacing(8)
        
        # Stack title and payment vertically (centered)
        header_layout.addWidget(
            self._title_lbl,
            0,
            0,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )
        header_layout.addWidget(
            self._payment_lbl,
            1,
            0,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )

        # wrapper completes

        # use a single pink style sheet everywhere
        self._apply_global_styles()
        # ---------------- state vars ----------------
        self.data_path = Path(DATA_FILE)
        self.log_queue: queue.Queue[str] = queue.Queue()
        self._log_emitter = LogEmitter()
        self._log_emitter.new_text.connect(self._append_log)


        # ---------------- build ui ------------------
        self._central_widget = QWidget(self)
        self.setCentralWidget(self._central_widget)
        self._layout = QGridLayout(self._central_widget)  # Changed back to grid layout for proper structure
        self._layout.setContentsMargins(32, 32, 32, 32)
        self._layout.setHorizontalSpacing(24)
        self._layout.setVerticalSpacing(16)

        # --- Header spans both columns ------------------------------------------
        # (header_widget is already created above)
        
        # --- Create container for two columns -----------------------------------
        columns_container = QWidget()
        columns_layout = QHBoxLayout(columns_container)
        columns_layout.setContentsMargins(0, 0, 0, 0)
        columns_layout.setSpacing(24)

        # --- LEFT COLUMN: Configuration/Settings ---------------------------------
        left_column = QWidget()
        left_column.setMinimumWidth(400)  # Set minimum width for the entire left column
        left_layout = QGridLayout(left_column)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setVerticalSpacing(16)
        
        # --- file chooser group -------------------------------------------------
        self._file_group = QGroupBox("Applicant file")
        file_layout = QGridLayout()
        self._file_edit = QLineEdit(str(DATA_FILE))
        self._file_edit.setMinimumWidth(300)  # Set minimum width for responsiveness
        self._file_btn = QPushButton("Browse…")
        self._file_btn.setMaximumWidth(100)   # Prevent button from being too wide
        self._file_btn.clicked.connect(self._choose_file)
        file_layout.addWidget(self._file_edit, 0, 0, 1, 2)
        file_layout.addWidget(self._file_btn, 0, 2)
        self._file_group.setLayout(file_layout)

        # --- select folder of images ---------------------------------------------
        self._image_folder_edit = QLineEdit()
        self._image_folder_edit.setMinimumWidth(300)
        self._image_folder_edit.setPlaceholderText("Select folder containing images...")
        self._image_folder_btn = QPushButton("Browse…")
        self._image_folder_btn.setMaximumWidth(100)
        self._image_folder_btn.clicked.connect(self._choose_image_folder)
        file_layout.addWidget(self._image_folder_edit, 1, 0, 1, 2)
        file_layout.addWidget(self._image_folder_btn, 1, 2)

        # --- auth group ---------------------------------------------------------
        self._auth_group = QGroupBox("Account")
        auth_layout = QGridLayout()
        self._email_edit = QLineEdit(EMAIL_LOGIN)
        self._email_edit.setMinimumWidth(250)
        self._pass_edit = QLineEdit(PASSWORD_LOGIN)
        self._pass_edit.setMinimumWidth(250)
        self._pass_edit.setEchoMode(QLineEdit.Password)
        auth_layout.addWidget(QLabel("Email"), 0, 0)
        auth_layout.addWidget(self._email_edit, 0, 1)
        auth_layout.addWidget(QLabel("Password"), 1, 0)
        auth_layout.addWidget(self._pass_edit, 1, 1)
        # Make the input column stretch
        auth_layout.setColumnStretch(1, 1)
        self._auth_group.setLayout(auth_layout)
        # Initialize start index edit field
        self._start_index_edit = QLineEdit("0")
        self._start_index_edit.setValidator(QIntValidator(0, 999999))
        self._start_index_edit.setMinimumWidth(100)

        # --- options group -------------------------------------------------------
        self._opt_group = QGroupBox("Options")
        opt_layout = QGridLayout()
        opt_layout.setVerticalSpacing(12)  # Add vertical spacing between rows
        opt_layout.setHorizontalSpacing(8)  # Add horizontal spacing between columns

        self._reuse_chk = QCheckBox("Reuse existing browser")
        self._reuse_chk.setChecked(USE_EXISTING_BROWSER)
        self._autonext_chk = QCheckBox("Auto‑advance steps")
        self._autonext_chk.setChecked(AUTO_NEXT)
        
        # Put checkboxes in separate rows for better layout
        opt_layout.addWidget(self._reuse_chk, 0, 0, 1, 2)
        opt_layout.addWidget(self._autonext_chk, 1, 0, 1, 2)
        
        # Quick form URL with better layout
        self._quick_edit = QLineEdit(QUICK_FORM_URL)
        self._quick_edit.setMinimumWidth(300)
        # Add tooltip for the long URL
        self._quick_edit.setToolTip("Enter the quick form URL for visa application")
        opt_layout.addWidget(QLabel("Quick form URL"), 2, 0)
        opt_layout.addWidget(self._quick_edit, 3, 0, 1, 2)  # Span 2 columns for more space
        
        # Plus days to departure
        self._plus_spin = QSpinBox()
        self._plus_spin.setRange(0, 30)
        self._plus_spin.setValue(PLUS_DAY_TO_DATE)
        self._plus_spin.setMinimumWidth(80)
        opt_layout.addWidget(QLabel("Plus days to departure"), 4, 0)
        opt_layout.addWidget(self._plus_spin, 4, 1)
        
        # Start from row index
        opt_layout.addWidget(QLabel("Start from row index"), 5, 0)
        opt_layout.addWidget(self._start_index_edit, 5, 1)
        
        # Make the input columns stretch properly
        opt_layout.setColumnStretch(1, 1)
        self._opt_group.setLayout(opt_layout)
        
        # --- run button ---------------------------------------------------------
        self._run_btn = QPushButton("Run visa autofill ➜")
        self._run_btn.clicked.connect(self._start_process)
        self._run_btn.setMinimumHeight(48)
        self._run_btn.setFont(QFont("Helvetica", 14, QFont.Bold))  # Use system font
        
        # Set proper size policy for responsiveness
        self._run_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Add all configuration elements to left column
        left_layout.addWidget(self._file_group, 0, 0)
        left_layout.addWidget(self._auth_group, 1, 0)
        left_layout.addWidget(self._opt_group, 2, 0)
        left_layout.addWidget(self._run_btn, 3, 0)
        left_layout.setRowStretch(4, 1)  # Add stretch to push everything to top

        # Set size policies for responsive behavior
        left_column.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        
        # --- RIGHT COLUMN: Logs and Output --------------------------------------
        right_column = QWidget()
        right_column.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_layout = QGridLayout(right_column)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setVerticalSpacing(16)

        # --- log viewer ---------------------------------------------------------
        self._log_view = QTextEdit()
        self._log_view.setReadOnly(True)
        self._log_view.setLineWrapMode(QTextEdit.NoWrap)
        self._log_view.setStyleSheet("background:#1e1e1e; color:#d4d4d4; font-family:'Monaco','Menlo','DejaVu Sans Mono',monospace; padding:8px")
        self._log_view.setMinimumHeight(400)
        
        # Add log title
        log_title = QLabel("Process Logs")
        log_title.setFont(QFont("Helvetica", 14, QFont.Bold))  # Use system font
        log_title.setStyleSheet("color: #ad1457; padding: 8px 0; border-bottom: 2px solid #ec407a;")
        
        # Add elements to right column
        right_layout.addWidget(log_title, 0, 0)
        right_layout.addWidget(self._log_view, 1, 0)
        right_layout.setRowStretch(1, 1)  # Make log view expandable

        # Add columns to container
        columns_layout.addWidget(left_column, 1)   # Left column for configuration
        columns_layout.addWidget(right_column, 2)  # Right column for logs (larger)

        # --- signature ----------------------------------------------------------
        signature = QLabel("<i>Luu Trung Kien – Senior Software Engineer<br/>luutrungkien120894@gmail.com</i>")
        signature.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        signature.setStyleSheet("color:#ad1457; margin-top:16px")
        signature.setFont(QFont("Helvetica", 10))  # Use system font

        # Add to main layout
        self._layout.addWidget(header_widget, 0, 0, 1, 1)      # Header at top
        self._layout.addWidget(columns_container, 1, 0, 1, 1)  # Two columns below
        self._layout.addWidget(signature, 2, 0, 1, 1)          # Signature at bottom
        self._layout.setRowStretch(1, 1)  # Make columns container expandable

    
    # ---------------------------------------------------------------------
    def _apply_global_styles(self):
        """Impose a bright pink color palette using Qt stylesheets."""
        pink = "#ec407a"  # primary
        dark_pink = "#ad1457"  # accent
        self.setStyleSheet(
            f"""
            QWidget {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                font-size: 12pt;
            }}
            QWidget#VisaAutofillWindow, QWidget[objectName="VisaAutofillWindow"] {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #fff1f9, stop:1 #ffe6f0);
            }}
            QGroupBox {{
                border: 2px solid {pink};
                border-radius: 8px;
                margin-top: 6px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
                color: {dark_pink};
                font-weight: bold;
            }}
            QPushButton {{
                background-color: {pink};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 18px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {dark_pink};
            }}
            QPushButton:disabled {{
                background-color: #f8bbd0;
            }}
            QLineEdit, QTextEdit, QSpinBox {{
                border: 1px solid {pink};
                border-radius: 6px;
                padding: 4px 6px;
                font-size: 11pt;
            }}
            QLineEdit::placeholder {{
                color: #b71c4a;
            }}
            QCheckBox {{
                color: #5b2848;
                font-weight: 500;
                padding: 4px 0;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 2px solid {pink};
                border-radius: 3px;
                background-color: white;
            }}
            QCheckBox::indicator:checked {{
                background-color: {pink};
                border: 2px solid {dark_pink};
            }}
            QLabel {{
                color: #5b2848;
                font-weight: 500;
            }}
            """
        )

    # ------------------------------------------------------------------
    def _choose_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select applicant Excel/CSV",
            str(self.data_path),
            "Excel/CSV (*.xls *.xlsx *.csv)",
        )
        if path:
            self._file_edit.setText(path)
            self.data_path = Path(path)

    # ------------------------------------------------------------------
    def _choose_image_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select image folder")
        if path:
            self._image_folder_edit.setText(path)
            self.image_folder = Path(path)

    # ------------------------------------------------------------------
    def _start_process(self):
        if not self.data_path.exists():
            QMessageBox.critical(
                self,
                "Validation",
                f"Input file does not exist:\n{self.data_path}",
            )
            return
        # Disable run button to avoid duplicates
        self._run_btn.setEnabled(False)
        conf = {
            "DATA_FILE": self.data_path,
            "EMAIL_LOGIN": self._email_edit.text().strip(),
            "PASSWORD_LOGIN": self._pass_edit.text(),
            "HEADLESS": HEADLESS,
            "USE_EXISTING_BROWSER": self._reuse_chk.isChecked(),
            "AUTO_NEXT": self._autonext_chk.isChecked(),
            "LOGIN_URL": LOGIN_URL,
            "FORM_URL": FORM_URL,
            "QUICK_FORM_URL": self._quick_edit.text().strip(),
            "PLUS_DAY_TO_DATE": self._plus_spin.value(),
            "START_INDEX": int(self._start_index_edit.text().strip()),
            "IMAGE_FOLDER": self._image_folder_edit.text().strip(),
        }
        # fire background thread
        threading.Thread(target=self._worker, args=(conf,), daemon=True).start()

    def _worker(self, conf):
        # Patch stdout/stderr for the duration
        import sys as _sys, builtins as _builtin
        emitter_stream = GateKeeperStream(self._log_emitter)
        old_stdout, old_stderr = _sys.stdout, _sys.stderr
        
        _sys.stdout = _sys.stderr = emitter_stream

            # ---------- patch input() so CLI prompts become Qt dialogs ------------
        def gui_input(prompt: str = "") -> str:
            """Redirect input() calls from visa_autofill to Qt dialogs.

            All GUI interactions *must* occur on the main thread.  We therefore
            use QMetaObject.invokeMethod with a *BlockingQueuedConnection* so
            the call is executed synchronously on the GUI thread.  The dialog
            stores its answer on ``self._yes_no_result``; after the blocking
            call returns we can safely read that value from the worker thread.
            """

            # --- Yes / No question ------------------------------------------
            if "(y/n" in prompt.lower():
                # Ensure attribute exists
                self._yes_no_result = None

                # Execute the slot synchronously on the GUI thread
                QMetaObject.invokeMethod(
                    self,
                    "_ask_yes_no",
                    Qt.ConnectionType.BlockingQueuedConnection,
                    Q_ARG(str, prompt),
                )

                if self._yes_no_result == "C":
                    # stop the process
                    sys.exit(0)
                else:
                # Value has been set by the slot above
                    return (self._yes_no_result or "N").upper()

            # --- Informational prompt ---------------------------------------
            QMetaObject.invokeMethod(
                self,
                "_show_info",
                Qt.ConnectionType.BlockingQueuedConnection,
                Q_ARG(str, prompt),
            )
            return ""

        _builtin.input = gui_input   
     

        try:
            run_visa_autofill(conf)
        except Exception as exc:  # noqa: BLE001
            self._log_emitter.new_text.emit(f"\nERROR: {exc}\n")
            QTimer.singleShot(0, lambda: (QMessageBox.critical(self, "Visa Autofill", f"An error occurred:\n{exc}"), None)[1])
        finally:
            # restore patched stuff
            _sys.stdout, _sys.stderr = old_stdout, old_stderr
        
            QTimer.singleShot(0, lambda: self._run_btn.setEnabled(True))
            QTimer.singleShot(0, lambda: (QMessageBox.information(self, "Visa Autofill", "Process finished."), None)[1])
            self._run_btn.setEnabled(True)

    # ------------------------------------------------------------------
    def _append_log(self, text: str):
        """Append text to the log view."""
        self._log_view.moveCursor(self._log_view.textCursor().End)
        self._log_view.insertPlainText(text)
        self._log_view.ensureCursorVisible()

    # ------------------------------------------------------------------
    @pyqtSlot(str)
    def _ask_yes_no(self, prompt: str):
        """Yes/No dialog executed on the GUI thread.  Stores result on ``self``."""

        choice = QMessageBox.question(
            self,
            "Visa Autofill – Question",
            prompt.replace("(Y/N)", "").strip(),
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            QMessageBox.Yes,  # ← ENTER will select "Yes" now
        )

        # Persist the result for the worker thread to read
        self._yes_no_result = "Y" if choice == QMessageBox.Yes else "N" if choice == QMessageBox.No else "C"

    @pyqtSlot(str)
    def _show_info(self, prompt: str):
        """Simple information dialog executed on the GUI thread."""
        QMessageBox.information(self, "Visa Autofill", prompt.strip())


# ------------------------------------------------------------------------

def main():
    app = QApplication(sys.argv)
    window = VisaAutofillWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
