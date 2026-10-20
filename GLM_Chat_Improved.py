# -*- coding: utf-8 -*-
"""
GLM Chat Improved V 1.0 Improved V 1.0 — Modern dark neon desktop UI
Creator: Agh4Saeed
Python 3.10+
pip install PySide6 requests
Optional: pip install keyring markdown
"""

import os
import sys
import html
import json
import uuid
import base64
import mimetypes
import re
from datetime import datetime
from pathlib import Path

import requests
from PySide6.QtCore import Qt, QThread, Signal, QEvent, QSize, QTimer, QUrl
from PySide6.QtGui import QFont, QTextCursor, QDragEnterEvent, QDropEvent, QAction, QDesktopServices, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QTextBrowser, QTextEdit, QFrame,
    QMessageBox, QFileDialog, QListWidget, QListWidgetItem,
    QAbstractItemView, QSplitter, QProgressBar, QMenu
)



try:
    import keyring
    HAS_KEYRING = True
except ImportError:
    HAS_KEYRING = False

try:
    import markdown as md_lib
    HAS_MARKDOWN = True
except ImportError:
    HAS_MARKDOWN = False

# ================= تنظیمات =================
API_URL = "http://127.0.0.1:8788/v1/chat/completions"
MODELS_URL = "http://127.0.0.1:8788/v1/models"
AVAILABLE_MODELS = ["GLM-5.3", "GLM-5.3-Flash"]
HISTORY_FILE = Path.home() / ".glm_chat_history.json"
CONFIG_FILE = Path.home() / ".glm_chat_config.json"
MAX_FILE_SIZE = 5 * 1024 * 1024
MAX_HISTORY_MESSAGES = 80          # per chat
MAX_TEXT_IN_HISTORY = 32 * 1024    # bytes kept for text attachments in history
DEFAULT_TEMPERATURE = 0.5
DEFAULT_MAX_TOKENS = 4096
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff", ".svg"}


T = {
    "en": {
        "window_title": "GLM Chat Improved V 1.0 • ZCode Client — by Agh4Saeed",
        "brand": "GLM Chat Improved V 1.0",
        "subtitle": "ZCode Local Client  •  AI Workspace",
        "local_client": "●  LOCAL CLIENT",
        "api_key": "⚿  API Key",
        "api_placeholder": "Enter your API Key...",
        "model": "▣  Model:",
        "test": "ϟ  Test Connection",
        "change_key": "✎  Change API Key",
        "clear": "♲  Clear Chat",
        "send": "Send  ➤",
        "composer_ph": "Type your message...  (Enter to send, Shift+Enter for new line)",
        "attach_tip": "Attach file or image (or drag & drop)",
        "status_ready": "Ready",
        "status_thinking": "Thinking with {model}...",
        "status_connected": "Connected ✓  —  API Key locked",
        "status_failed": "Connection failed",
        "status_cleared": "Chat cleared",
        "status_error": "An error occurred",
        "status_uploading": "Uploading {name}... {pct}%",
        "welcome_title": "✦  Welcome to GLM Smart Space  ✦",
        "welcome_body": "Enter your API Key, select a model and start chatting.<br>Attach any file or image (up to 5 MB) with ＋ or drag & drop.",
        "you": "You",
        "key_empty": "Please enter your API Key first.",
        "clear_title": "Clear Chat",
        "clear_msg": "Clear all messages in this chat?",
        "test_ok": "Connection successful!\nAvailable models:\n• {models}",
        "test_fail": "Connection failed:\n{error}",
        "conn_error": "Could not connect to the server.\nIs it running on port 8788?",
        "timeout": "Request timed out.",
        "generic_error": "Error: {error}",
        "lang": "Language:",
        "file_added": "Added: {name}",
        "file_too_large": "File too large (max 5 MB): {name}",
        "files_label": "Attached:",
        "new_chat": "+ New Chat",
        "chats": "Chats",
        "untitled": "New Chat",
        "creator": "Created by Agh4Saeed",
        "sent_file": "📎  {name}",
        "sent_image": "🖼  {name}",
        "delete_chat": "Delete Chat",
        "uploading": "Uploading...",
        "thinking_bubble": "Thinking… analyzing your request with {model}",
        "processing": "Processing…",
        "status_error_detail": "Error: {error}",
        "status_error_conn": "Connection failed — is the server running on port 8788?",
        "status_error_timeout": "Request timed out — try again or check the server",
        "stop": "■ Stop",
        "status_stopped": "Stopped",
        "stopped_bubble": "⏹  Generation stopped by user",
        "stopped_partial": "⏹  Generation stopped by user\n\n{partial}",
        "copy": "Copy",
        "copy_code": "Copy code",
        "copied": "Copied",
        "copied_title": "Clipboard",
        "copied_msg": "Code copied to clipboard successfully.",
        "temp": "Temp:",
        "max_tokens": "Max tokens:",
        "theme": "Theme:",
        "theme_dark": "Dark",
        "theme_light": "Light",
        "settings": "Settings",
        "chars": "{n} chars",
        "history_trimmed": "[… truncated for history; full content was sent to the model]",
    },
    "fa": {

        "window_title": "چت GLM • کلاینت ZCode — ساخته‌شده توسط Agh4Saeed",
        "brand": "چت GLM",
        "subtitle": "کلاینت محلی ZCode  •  فضای کاری هوش مصنوعی",
        "local_client": "●  کلاینت محلی",
        "api_key": "⚿  کلید API",
        "api_placeholder": "کلید API خود را وارد کنید...",
        "model": "▣  مدل:",
        "test": "ϟ  تست اتصال",
        "change_key": "✎  تغییر کلید API",
        "clear": "♲  پاک کردن چت",
        "send": "ارسال  ➤",
        "composer_ph": "پیام خود را بنویسید...  (Enter برای ارسال، Shift+Enter خط جدید)",
        "attach_tip": "افزودن فایل یا عکس (یا بکشید و رها کنید)",
        "status_ready": "آماده",
        "status_thinking": "در حال فکر کردن با {model}...",
        "status_connected": "اتصال برقرار ✓  —  کلید قفل شد",
        "status_failed": "اتصال ناموفق",
        "status_cleared": "چت پاک شد",
        "status_error": "خطا رخ داد",
        "status_uploading": "در حال آپلود {name}... {pct}%",
        "welcome_title": "✦  به فضای هوشمند GLM خوش آمدید  ✦",
        "welcome_body": "کلید API را وارد کنید، مدل را انتخاب کنید و شروع به چت کنید.<br>هر نوع فایل یا عکس (تا ۵ مگابایت) را با ＋ یا کشیدن و رها کردن اضافه کنید.",
        "you": "شما",
        "key_empty": "لطفاً ابتدا کلید API را وارد کنید.",
        "clear_title": "پاک کردن چت",
        "clear_msg": "همه پیام‌های این چت پاک شوند؟",
        "test_ok": "اتصال موفق!\nمدل‌های موجود:\n• {models}",
        "test_fail": "اتصال ناموفق:\n{error}",
        "conn_error": "اتصال به سرور برقرار نشد.\nآیا سرور روی پورت 8788 روشن است؟",
        "timeout": "زمان درخواست تمام شد.",
        "generic_error": "خطا: {error}",
        "lang": "زبان:",
        "file_added": "اضافه شد: {name}",
        "file_too_large": "فایل خیلی بزرگ است (حداکثر ۵ مگابایت): {name}",
        "files_label": "پیوست‌ها:",
        "new_chat": "+ چت جدید",
        "chats": "چت‌ها",
        "untitled": "چت جدید",
        "creator": "ساخته‌شده توسط Agh4Saeed",
        "sent_file": "📎  {name}",
        "sent_image": "🖼  {name}",
        "delete_chat": "حذف چت",
        "uploading": "در حال آپلود...",
        "thinking_bubble": "در حال فکر کردن… در حال تحلیل درخواست شما با {model}",
        "processing": "در حال پردازش…",
        "status_error_detail": "خطا: {error}",
        "status_error_conn": "اتصال ناموفق — آیا سرور روی پورت 8788 روشن است؟",
        "status_error_timeout": "زمان درخواست تمام شد — دوباره تلاش کنید یا سرور را چک کنید",
        "stop": "■ توقف",
        "status_stopped": "متوقف شد",
        "stopped_bubble": "⏹  تولید پاسخ توسط کاربر متوقف شد",
        "stopped_partial": "⏹  تولید پاسخ توسط کاربر متوقف شد\n\n{partial}",
        "copy": "کپی",
        "copy_code": "کپی کد",
        "copied": "کپی شد",
        "copied_title": "کلیپ‌بورد",
        "copied_msg": "کد با موفقیت در کلیپ‌بورد کپی شد.",
        "temp": "دما:",
        "max_tokens": "حداکثر توکن:",
        "theme": "تم:",
        "theme_dark": "تیره",
        "theme_light": "روشن",
        "settings": "تنظیمات",
        "chars": "{n} کاراکتر",
        "history_trimmed": "[… برای تاریخچه کوتاه شد؛ محتوای کامل به مدل ارسال شده بود]",
    }
}


APP_QSS = r"""
* { font-family: "Segoe UI", "Tahoma"; font-size: 10.5pt; }
QMainWindow, QWidget#root { background: #050b1b; color: #eaf2ff; }
QFrame#topbar, QFrame#hero, QFrame#settings, QFrame#chatPanel,
QFrame#composer, QFrame#statusbar, QFrame#sidebar {
    background: #07132d; border: 1px solid #123d78; border-radius: 14px;
}
QFrame#hero {
    border-color: #1555a5;
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
       stop:0 #07132d, stop:0.55 #07142c, stop:1 #0a1233);
}
QLabel#brand { font-size: 20pt; font-weight: 700; color: #f1f7ff; }
QLabel#subtitle { color: #83a7e5; font-size: 10pt; }
QLabel#sectionLabel { color: #bcd2fa; font-weight: 600; }
QLineEdit, QComboBox, QTextEdit {
    background: #0b1b3e; color: #f3f7ff; border: 1px solid #214c8d;
    border-radius: 9px; padding: 8px 12px; selection-background-color: #146cf3;
}
QLineEdit:focus, QComboBox:focus, QTextEdit:focus { border: 1px solid #08b9ff; }
QLineEdit:disabled { background: #0a1528; color: #6a7a9a; }
QComboBox QAbstractItemView {
    background: #0b1b3e; color: #f3f7ff; selection-background-color: #135ce7;
}
QPushButton {
    color: white; background: #10234c; border: 1px solid #24569a;
    border-radius: 10px; padding: 9px 14px; font-weight: 600;
}
QPushButton:hover { background: #15366f; border-color: #05baff; }
QPushButton:disabled { background: #0a1528; color: #5a6a8a; border-color: #1a2a4a; }
QPushButton#primary {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #08a9ed, stop:1 #4949ff);
    border: 1px solid #21c6ff; padding: 12px 22px; font-size: 11pt;
}
QPushButton#primary:hover { background: #1b8dff; }
QPushButton#danger { background: #48144d; border: 1px solid #db36ad; }
QPushButton#danger:hover { background: #671a63; }
QPushButton#iconButton { font-size: 14pt; padding: 6px 10px; min-width: 36px; }
QPushButton#delBtn {
    background: #5c1a2e; border: 1px solid #e05a7a; color: #ffb3c1;
    border-radius: 6px; padding: 2px 8px; font-size: 12pt; font-weight: 700;
    min-width: 26px; max-width: 28px;
}
QPushButton#delBtn:hover { background: #8b2240; }
QTextBrowser#chat {
    background: transparent; border: none; padding: 12px 18px; color: #e8f1ff;
    font-size: 12pt;
}
QTextEdit#composerText {
    background: #0b1b3e; border: 1px solid #214c8d; border-radius: 11px; padding: 12px;
}
QLabel#status { color: #81a3df; font-size: 10pt; }
QLabel#status[error="true"] { color: #ff7b9c; font-weight: 600; }
QLabel#greenDot { color: #00e59b; font-size: 16pt; }
QLabel#greenDot[error="true"] { color: #ff4d6d; }
QFrame#statusbar { border: none; border-top: 1px solid #102b54; border-radius: 0; }
QFrame#chatPanel {
    background: #061028;
    border: 1px solid #123d78;
}

/* لیست چت تمیز و یکدست */
QListWidget {
    background: transparent; border: none; outline: none;
    padding: 4px;
}
QListWidget::item {
    background: #0b1b3e;
    border: 1px solid #1a3a6e;
    border-radius: 10px;
    padding: 11px 14px;
    margin: 4px 2px;
    color: #e2eaff;
    font-weight: 600;
}
QListWidget::item:selected {
    background: #135ce7;
    border-color: #3b82f6;
    color: white;
}
QListWidget::item:hover {
    background: #0d2a5c;
    border-color: #2563eb;
}
QProgressBar {
    border: 1px solid #214c8d; border-radius: 6px; background: #0b1b3e;
    text-align: center; color: #eaf2ff; height: 18px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #08a9ed, stop:1 #4949ff);
    border-radius: 5px;
}
"""

APP_QSS_LIGHT = r"""
* { font-family: "Segoe UI", "Tahoma"; font-size: 10.5pt; }
QMainWindow, QWidget#root { background: #f0f4fa; color: #1a2332; }
QFrame#topbar, QFrame#hero, QFrame#settings, QFrame#chatPanel,
QFrame#composer, QFrame#statusbar, QFrame#sidebar {
    background: #ffffff; border: 1px solid #c5d4eb; border-radius: 14px;
}
QFrame#hero {
    border-color: #7aa2e3;
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
       stop:0 #ffffff, stop:0.55 #f5f8fd, stop:1 #eef3fb);
}
QLabel#brand { font-size: 20pt; font-weight: 700; color: #1a2332; }
QLabel#subtitle { color: #5a7ab0; font-size: 10pt; }
QLabel#sectionLabel { color: #3d5a80; font-weight: 600; }
QLineEdit, QComboBox, QTextEdit, QDoubleSpinBox, QSpinBox {
    background: #f7faff; color: #1a2332; border: 1px solid #b0c4de;
    border-radius: 9px; padding: 8px 12px; selection-background-color: #3b82f6;
}
QLineEdit:focus, QComboBox:focus, QTextEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus {
    border: 1px solid #2563eb;
}
QLineEdit:disabled { background: #e8eef8; color: #8a9ab8; }
QComboBox QAbstractItemView {
    background: #ffffff; color: #1a2332; selection-background-color: #3b82f6;
}
QPushButton {
    color: #1a2332; background: #e8eef8; border: 1px solid #b0c4de;
    border-radius: 10px; padding: 9px 14px; font-weight: 600;
}
QPushButton:hover { background: #d6e4f7; border-color: #3b82f6; }
QPushButton:disabled { background: #eef2f8; color: #a0aec0; border-color: #d0d8e8; }
QPushButton#primary {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #3b82f6, stop:1 #6366f1);
    border: 1px solid #2563eb; padding: 12px 22px; font-size: 11pt; color: white;
}
QPushButton#primary:hover { background: #2563eb; }
QPushButton#danger { background: #fde8ee; border: 1px solid #f0a0b0; color: #b91c4c; }
QPushButton#danger:hover { background: #fbd0da; }
QPushButton#iconButton { font-size: 14pt; padding: 6px 10px; min-width: 36px; }
QPushButton#delBtn {
    background: #fde8ee; border: 1px solid #f0a0b0; color: #b91c4c;
    border-radius: 6px; padding: 2px 8px; font-size: 12pt; font-weight: 700;
    min-width: 26px; max-width: 28px;
}
QPushButton#delBtn:hover { background: #fbd0da; }
QTextBrowser#chat {
    background: transparent; border: none; padding: 12px 18px; color: #1a2332;
    font-size: 12pt;
}
QTextEdit#composerText {
    background: #f7faff; border: 1px solid #b0c4de; border-radius: 11px; padding: 12px;
}
QLabel#status { color: #5a7ab0; font-size: 10pt; }
QLabel#status[error="true"] { color: #dc2626; font-weight: 600; }
QLabel#greenDot { color: #16a34a; font-size: 16pt; }
QLabel#greenDot[error="true"] { color: #dc2626; }
QFrame#statusbar { border: none; border-top: 1px solid #d0dcec; border-radius: 0; }
QFrame#chatPanel {
    background: #f8fafc;
    border: 1px solid #c5d4eb;
}
QListWidget {
    background: transparent; border: none; outline: none;
    padding: 4px;
}
QListWidget::item {
    background: #eef3fb;
    border: 1px solid #c5d4eb;
    border-radius: 10px;
    padding: 11px 14px;
    margin: 4px 2px;
    color: #1a2332;
    font-weight: 600;
}
QListWidget::item:selected {
    background: #3b82f6;
    border-color: #2563eb;
    color: white;
}
QListWidget::item:hover {
    background: #dde8f7;
    border-color: #7aa2e3;
}
QProgressBar {
    border: 1px solid #b0c4de; border-radius: 6px; background: #eef3fb;
    text-align: center; color: #1a2332; height: 18px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #3b82f6, stop:1 #6366f1);
    border-radius: 5px;
}
"""


# Short anti-hallucination hint (kept short so local proxies don't reject it)
SYSTEM_HINT = (

    "[System] You are a local chat assistant. You have NO terminal, NO Bash, NO tools, "
    "and NO live clock. Never pretend to run commands. Answer in the user's language. "
    "Be concise; do not repeat the same idea."
)


class ApiWorker(QThread):
    """Non-stream first (most reliable on local proxies), then optional streaming.
    Bound to a specific chat_id + generation_id so replies never leak across chats.

    Note: custom completion signal is named `reply_ready` so it does NOT shadow
    QThread.finished (needed for safe thread lifecycle / deleteLater).
    """
    chunk = Signal(str)
    reply_ready = Signal(str)   # was "finished" — renamed to avoid shadowing QThread.finished
    error = Signal(str)
    # Emits when stop was requested and we aborted (optional partial text)
    stopped = Signal(str)

    def __init__(self, api_key, model, messages, chat_id: str, generation_id: str,
                 temperature: float = DEFAULT_TEMPERATURE, max_tokens: int = DEFAULT_MAX_TOKENS,
                 parent=None):
        super().__init__(parent)
        self.api_key = api_key
        self.model = model
        self.messages = messages
        self.chat_id = chat_id
        self.generation_id = generation_id
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._stop = False
        self._session = None
        self._response = None


    def stop(self):
        self._stop = True
        # Best-effort abort of the HTTP connection
        try:
            if self._response is not None:
                self._response.close()
        except Exception:
            pass
        try:
            if self._session is not None:
                self._session.close()
        except Exception:
            pass

    def run(self):
        try:
            self._session = requests.Session()
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            msgs = self._prepare_messages()
            last_err = None

            if self._stop:
                self.stopped.emit("")
                return

            # 1) Non-stream (same style as original working client)
            reply, err = self._try_nonstream(headers, {
                "model": self.model,
                "messages": msgs,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            })
            if self._stop:
                self.stopped.emit(reply or "")
                return
            if reply:
                self.reply_ready.emit(reply)
                return
            last_err = err

            if self._stop:
                self.stopped.emit("")
                return

            # 2) Non-stream without system hint (some proxies reject system role)
            plain_msgs = [m for m in self.messages if m.get("role") != "system"]
            reply, err = self._try_nonstream(headers, {
                "model": self.model,
                "messages": plain_msgs,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            })
            if self._stop:
                self.stopped.emit(reply or "")
                return
            if reply:
                self.reply_ready.emit(reply)
                return
            last_err = err or last_err

            if self._stop:
                self.stopped.emit("")
                return

            # 3) Streaming attempt
            reply, err = self._try_stream(headers, {
                "model": self.model,
                "messages": plain_msgs,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "stream": True,
            })

            if self._stop:
                self.stopped.emit(reply or "")
                return
            if reply:
                self.reply_ready.emit(reply)
                return
            last_err = err or last_err

            if self._stop:
                self.stopped.emit("")
                return
            self.error.emit(last_err or "Empty response from server")
        except requests.exceptions.ConnectionError:
            if self._stop:
                self.stopped.emit("")
            else:
                self.error.emit("conn")
        except requests.exceptions.Timeout:
            if self._stop:
                self.stopped.emit("")
            else:
                self.error.emit("timeout")
        except Exception as e:
            if self._stop:
                self.stopped.emit("")
            else:
                self.error.emit(str(e))
        finally:
            try:
                if self._session is not None:
                    self._session.close()
            except Exception:
                pass
            self._session = None
            self._response = None

    def _prepare_messages(self):
        msgs = []
        for m in self.messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            if role == "system":
                continue
            msgs.append({"role": role, "content": content})
        # Prepend hint as system if possible; many OpenAI-compatible proxies accept it
        return [{"role": "system", "content": SYSTEM_HINT}] + msgs

    def _extract_text(self, data):
        """Extract assistant text from many possible OpenAI-compatible shapes."""
        if data is None:
            return ""
        if isinstance(data, str):
            return data
        if not isinstance(data, dict):
            return ""

        # Direct fields some proxies use
        for key in ("content", "text", "response", "output", "answer"):
            val = data.get(key)
            if isinstance(val, str) and val.strip():
                return val

        choices = data.get("choices")
        if not isinstance(choices, list) or len(choices) == 0:
            # error object?
            err = data.get("error")
            if isinstance(err, dict) and err.get("message"):
                return ""  # signal empty; caller will use error message
            if isinstance(err, str):
                return ""
            return ""

        first = choices[0]
        if not isinstance(first, dict):
            return ""

        # stream delta
        delta = first.get("delta")
        if isinstance(delta, dict):
            for key in ("content", "text", "reasoning_content"):
                val = delta.get(key)
                if isinstance(val, str) and val:
                    return val

        # normal message
        msg = first.get("message")
        if isinstance(msg, dict):
            for key in ("content", "text", "reasoning_content"):
                val = msg.get(key)
                if isinstance(val, str) and val.strip():
                    return val
            # content can be a list of parts
            parts = msg.get("content")
            if isinstance(parts, list):
                bits = []
                for p in parts:
                    if isinstance(p, str):
                        bits.append(p)
                    elif isinstance(p, dict) and p.get("text"):
                        bits.append(str(p["text"]))
                if bits:
                    return "".join(bits)

        for key in ("content", "text"):
            val = first.get(key)
            if isinstance(val, str) and val.strip():
                return val
        return ""

    def _try_nonstream(self, headers, payload):
        try:
            if self._stop:
                return None, "stopped"
            sess = self._session or requests
            r = sess.post(API_URL, headers=headers, json=payload, timeout=180)
            self._response = r
            if self._stop:
                try:
                    r.close()
                except Exception:
                    pass
                return None, "stopped"
            body_preview = (r.text or "")[:300]
            if r.status_code >= 400:
                return None, f"HTTP {r.status_code}: {body_preview}"
            try:
                data = r.json()
            except Exception:
                return None, f"Non-JSON response: {body_preview}"
            # Server-side error object
            if isinstance(data, dict) and data.get("error"):
                err = data["error"]
                msg = err.get("message") if isinstance(err, dict) else str(err)
                return None, f"API error: {msg}"
            text = self._extract_text(data)
            if text and str(text).strip():
                return str(text).strip(), None
            return None, f"Empty content. Raw: {body_preview}"
        except requests.exceptions.ConnectionError:
            if self._stop:
                return None, "stopped"
            raise
        except requests.exceptions.Timeout:
            if self._stop:
                return None, "stopped"
            raise
        except Exception as e:
            if self._stop:
                return None, "stopped"
            return None, str(e)

    def _try_stream(self, headers, payload):
        try:
            if self._stop:
                return None, "stopped"
            sess = self._session or requests
            r = sess.post(API_URL, headers=headers, json=payload, timeout=180, stream=True)
            self._response = r
            if r.status_code >= 400:
                return None, f"HTTP {r.status_code} (stream): {(r.text or '')[:200]}"
            if not r.encoding:
                r.encoding = "utf-8"
            full = []
            for line in r.iter_lines(decode_unicode=True):

                if self._stop:
                    try:
                        r.close()
                    except Exception:
                        pass
                    break
                if not line:
                    continue
                s = line.strip()
                if s.startswith("data:"):
                    data_str = s[5:].strip()
                elif s.startswith("{") or s.startswith("["):
                    data_str = s  # some proxies send raw JSON lines
                else:
                    continue
                if data_str == "[DONE]":
                    break
                try:
                    data = json.loads(data_str)
                except json.JSONDecodeError:
                    continue
                piece = self._extract_text(data)
                if piece:
                    full.append(piece)
                    if not self._stop:
                        self.chunk.emit(piece)
            reply = "".join(full).strip()
            if self._stop:
                return (reply, "stopped") if reply else (None, "stopped")
            return (reply, None) if reply else (None, "Empty stream")
        except requests.exceptions.ConnectionError:
            if self._stop:
                return None, "stopped"
            raise
        except requests.exceptions.Timeout:
            if self._stop:
                return None, "stopped"
            raise
        except Exception as e:
            if self._stop:
                return None, "stopped"
            return None, str(e)


class TestWorker(QThread):
    # Renamed from "finished" so we do NOT shadow QThread.finished
    result_ready = Signal(str)
    error = Signal(str)

    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key

    def run(self):
        try:
            r = requests.get(MODELS_URL, headers={"Authorization": f"Bearer {self.api_key}"}, timeout=8)
            r.raise_for_status()
            models = [m["id"] for m in r.json().get("data", [])]
            self.result_ready.emit("\n• ".join(models))
        except Exception as e:
            self.error.emit(str(e))


class FileLoadWorker(QThread):
    progress = Signal(int, str)
    # Renamed from "finished" so we do NOT shadow QThread.finished
    result_ready = Signal(dict)
    error = Signal(str)

    def __init__(self, path: Path):
        super().__init__()
        self.path = path

    def run(self):
        try:
            size = self.path.stat().st_size
            if size > MAX_FILE_SIZE:
                self.error.emit("too_large")
                return
            is_image = self.path.suffix.lower() in IMAGE_EXT
            name = self.path.name
            # Real progress: read in chunks
            chunks = []
            read = 0
            chunk_size = max(64 * 1024, size // 20 or 1)
            with open(self.path, "rb") as f:
                while True:
                    part = f.read(chunk_size)
                    if not part:
                        break
                    chunks.append(part)
                    read += len(part)
                    pct = min(95, int(read * 100 / max(size, 1)))
                    self.progress.emit(pct, name)
            data = b"".join(chunks)
            if is_image:
                b64 = base64.b64encode(data).decode("ascii")
                mime = mimetypes.guess_type(str(self.path))[0] or "image/png"
                result = {"type": "image", "name": name, "base64": b64, "mime": mime}
            else:
                try:
                    text = data.decode("utf-8", errors="ignore")
                except Exception:
                    text = f"[Binary file: {name}]"
                result = {"type": "text", "name": name, "text": text}
            self.progress.emit(100, name)
            self.result_ready.emit(result)
        except Exception as e:
            self.error.emit(str(e))




class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.lang = "en"
        self.theme = "dark"  # "dark" | "light"
        self.temperature = DEFAULT_TEMPERATURE
        self.max_tokens = DEFAULT_MAX_TOKENS
        self.api_key_visible = False
        self.attached_files = []
        self.pending_loads = 0
        self.chats = []
        self.current_chat_id = None
        self.worker = None
        self.test_worker = None
        self.key_locked = False
        self._load_workers = []
        self._thinking_active = False
        # Per-chat stream buffers: chat_id -> {"text": str, "buffer": str}
        self._stream_data = {}
        self._stream_timer = QTimer(self)
        self._stream_timer.setInterval(120)
        self._stream_timer.timeout.connect(self._flush_stream)
        self._code_store = {}  # id -> source code for Copy buttons
        self._scroll_positions = {}  # chat_id -> int (scrollbar value)
        self._user_near_bottom = True  # smart auto-scroll
        # Per-generation isolation: reply only applies to the chat that started it
        self._active_chat_id = None       # chat_id that owns the current worker
        self._active_generation_id = None  # uuid of current generation
        self._cancelled_generations = set()  # generation_ids that were stopped
        self._workers_by_chat = {}  # chat_id -> ApiWorker (latest for that chat)
        # Strong refs to every worker still alive — prevents "QThread destroyed while running"
        self._live_workers = set()


        self.setAcceptDrops(True)

        self.resize(1280, 860)
        self.setMinimumSize(980, 680)

        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        main = QVBoxLayout(root)
        main.setContentsMargins(14, 10, 14, 10)
        main.setSpacing(8)

        # Top bar
        topbar = QFrame()
        topbar.setObjectName("topbar")
        top_layout = QHBoxLayout(topbar)
        top_layout.setContentsMargins(12, 6, 12, 6)
        logo = QLabel("✦")
        logo.setStyleSheet("color:#21c6ff;font-size:22pt;font-weight:700;")
        self.title_lbl = QLabel("GLM Chat Improved V 1.0")
        self.title_lbl.setStyleSheet("font-size:13pt;font-weight:700;color:#f4f8ff;")
        self.accent_lbl = QLabel("│  ZCode Local Client")
        self.accent_lbl.setStyleSheet("color:#86a8e8;")
        top_layout.addWidget(logo)
        top_layout.addWidget(self.title_lbl)
        top_layout.addWidget(self.accent_lbl)
        top_layout.addStretch()
        self.lang_label = QLabel()
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English", "فارسی"])
        self.lang_combo.currentIndexChanged.connect(self.change_language)
        top_layout.addWidget(self.lang_label)
        top_layout.addWidget(self.lang_combo)
        self.window_status = QLabel()
        self.window_status.setStyleSheet("color:#48baff;font-size:9pt;margin-left:10px;")
        top_layout.addWidget(self.window_status)
        main.addWidget(topbar)

        # Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # ===== Sidebar (تمیز و پایدار) =====
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setMinimumWidth(250)
        sidebar.setMaximumWidth(340)
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(12, 12, 12, 12)
        side_layout.setSpacing(8)

        self.chats_title = QLabel()
        self.chats_title.setStyleSheet("font-weight:700;color:#8db8ff;font-size:12pt;")
        side_layout.addWidget(self.chats_title)

        self.new_chat_btn = QPushButton()
        self.new_chat_btn.clicked.connect(self.create_new_chat)
        side_layout.addWidget(self.new_chat_btn)

        self.chat_list = QListWidget()
        self.chat_list.setSpacing(2)
        self.chat_list.itemClicked.connect(self.on_chat_selected)
        self.chat_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.chat_list.customContextMenuRequested.connect(self.show_chat_context_menu)
        side_layout.addWidget(self.chat_list, 1)

        self.creator_lbl = QLabel()
        self.creator_lbl.setStyleSheet("color:#5f7fb9;font-size:9pt;")
        self.creator_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        side_layout.addWidget(self.creator_lbl)
        splitter.addWidget(sidebar)

        # Right side
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)

        # Hero
        hero = QFrame()
        hero.setObjectName("hero")
        hero_layout = QHBoxLayout(hero)
        hero_layout.setContentsMargins(18, 12, 18, 12)
        star = QLabel("✦")
        star.setStyleSheet("font-size:36pt;color:#12baff;")
        brand_stack = QVBoxLayout()
        self.brand_lbl = QLabel()
        self.brand_lbl.setObjectName("brand")
        self.subtitle_lbl = QLabel()
        self.subtitle_lbl.setObjectName("subtitle")
        brand_stack.addWidget(self.brand_lbl)
        brand_stack.addWidget(self.subtitle_lbl)
        hero_layout.addWidget(star)
        hero_layout.addLayout(brand_stack)
        hero_layout.addStretch()
        right_layout.addWidget(hero)

        # Settings
        settings = QFrame()
        settings.setObjectName("settings")
        sv = QVBoxLayout(settings)
        sv.setContentsMargins(14, 12, 14, 12)
        sv.setSpacing(8)
        key_row = QHBoxLayout()
        self.key_label = QLabel()
        self.key_label.setObjectName("sectionLabel")
        self.key_input = QLineEdit()
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_input.setClearButtonEnabled(True)
        self.eye_btn = QPushButton("👁")
        self.eye_btn.setObjectName("iconButton")
        self.eye_btn.setFixedWidth(42)
        self.eye_btn.clicked.connect(self.toggle_api_visibility)
        key_row.addWidget(self.key_label)
        key_row.addWidget(self.key_input, 1)
        key_row.addWidget(self.eye_btn)
        sv.addLayout(key_row)
        control_row = QHBoxLayout()
        self.model_label = QLabel()
        self.model_label.setObjectName("sectionLabel")
        self.model_combo = QComboBox()
        self.model_combo.addItems(AVAILABLE_MODELS)
        self.model_combo.setMinimumWidth(160)
        self.test_btn = QPushButton()
        self.test_btn.clicked.connect(self.test_connection)
        self.change_key_btn = QPushButton()
        self.change_key_btn.clicked.connect(self.unlock_api_key)
        self.change_key_btn.setVisible(False)
        self.clear_btn = QPushButton()
        self.clear_btn.setObjectName("danger")
        self.clear_btn.clicked.connect(self.clear_current_chat)
        control_row.addWidget(self.model_label)
        control_row.addWidget(self.model_combo)
        control_row.addWidget(self.test_btn)
        control_row.addWidget(self.change_key_btn)
        control_row.addStretch()
        control_row.addWidget(self.clear_btn)
        sv.addLayout(control_row)
        # Theme row
        theme_row = QHBoxLayout()
        self.theme_label = QLabel()
        self.theme_label.setObjectName("sectionLabel")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        theme_row.addWidget(self.theme_label)
        theme_row.addWidget(self.theme_combo)
        theme_row.addStretch()
        sv.addLayout(theme_row)
        right_layout.addWidget(settings)



        # Chat
        chat_panel = QFrame()
        chat_panel.setObjectName("chatPanel")
        chat_layout = QVBoxLayout(chat_panel)
        chat_layout.setContentsMargins(4, 4, 4, 4)
        self.chat = QTextBrowser()
        self.chat.setObjectName("chat")
        self.chat.setOpenExternalLinks(False)
        self.chat.setOpenLinks(False)  # critical: don't navigate to copy:… as a document
        self.chat.anchorClicked.connect(self._on_chat_link)
        self.chat.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.chat.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.chat.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.chat.document().setDocumentMargin(8)
        chat_layout.addWidget(self.chat)
        right_layout.addWidget(chat_panel, 1)

        # ChatGPT-style copy toast (small label, auto-hides)
        self._copy_toast = QLabel(self.chat)
        self._copy_toast.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._copy_toast.setStyleSheet("""
            QLabel {
                background: #1e293b;
                color: #e2e8f0;
                border: 1px solid #334155;
                border-radius: 20px;
                padding: 8px 18px;
                font-size: 12px;
                font-weight: 600;
            }
        """)
        self._copy_toast.hide()
        self._copy_toast_timer = QTimer(self)
        self._copy_toast_timer.setSingleShot(True)
        self._copy_toast_timer.timeout.connect(self._hide_copy_feedback)

        # Attachments
        self.files_frame = QFrame()
        self.files_frame.setVisible(False)
        files_outer = QVBoxLayout(self.files_frame)
        files_outer.setContentsMargins(6, 6, 6, 6)
        files_outer.setSpacing(4)
        self.files_label = QLabel()
        files_outer.addWidget(self.files_label)
        self.attach_container = QVBoxLayout()
        self.attach_container.setSpacing(3)
        files_outer.addLayout(self.attach_container)
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setRange(0, 100)
        files_outer.addWidget(self.progress)
        right_layout.addWidget(self.files_frame)

        # Composer
        composer = QFrame()
        composer.setObjectName("composer")
        composer_layout = QHBoxLayout(composer)
        composer_layout.setContentsMargins(10, 8, 10, 8)
        self.attach_btn = QPushButton("＋")
        self.attach_btn.setFixedWidth(46)
        self.attach_btn.clicked.connect(self.pick_files)
        self.message_input = QTextEdit()
        self.message_input.setObjectName("composerText")
        self.message_input.setFixedHeight(70)
        self.stop_btn = QPushButton("■")
        self.stop_btn.setObjectName("danger")
        self.stop_btn.setMinimumWidth(70)
        self.stop_btn.setVisible(False)
        self.stop_btn.clicked.connect(self.stop_generation)
        self.send_btn = QPushButton()
        self.send_btn.setObjectName("primary")
        self.send_btn.setMinimumWidth(110)
        self.send_btn.clicked.connect(self.send_message)
        composer_layout.addWidget(self.attach_btn)
        composer_layout.addWidget(self.message_input, 1)
        composer_layout.addWidget(self.stop_btn)
        composer_layout.addWidget(self.send_btn)
        right_layout.addWidget(composer)

        splitter.addWidget(right)
        splitter.setStretchFactor(1, 1)
        main.addWidget(splitter, 1)

        # Status
        footer = QFrame()
        footer.setObjectName("statusbar")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(6, 6, 6, 0)
        self.status_dot = QLabel("●")
        self.status_dot.setObjectName("greenDot")
        self.status_label = QLabel()
        self.status_label.setObjectName("status")
        version = QLabel(f"GLM Chat Improved V 1.0  •  Agh4Saeed  •  {datetime.now():%Y}")
        version.setStyleSheet("color:#5f7fb9;")
        footer_layout.addWidget(self.status_dot)
        footer_layout.addWidget(self.status_label)
        footer_layout.addStretch()
        footer_layout.addWidget(version)
        main.addWidget(footer)

        self.message_input.installEventFilter(self)
        self.setStyleSheet(APP_QSS)

        # Smart auto-scroll: track whether user is near bottom
        self.chat.verticalScrollBar().valueChanged.connect(self._on_scroll_changed)

        # Keyboard shortcuts
        QShortcut(QKeySequence("Ctrl+N"), self, self.create_new_chat)
        QShortcut(QKeySequence("Ctrl+L"), self, self.clear_current_chat)
        QShortcut(QKeySequence("Escape"), self, self.stop_generation)

        self.load_config()
        self.load_history()
        self.apply_language()
        self._apply_theme()
        if not self.chats:
            self.create_new_chat()
        else:
            self.select_chat(self.chats[0]["id"])

    # ---------- Config ----------

    def _get_api_key(self):
        if HAS_KEYRING:
            try:
                k = keyring.get_password("glm_chat", "api_key")
                if k:
                    return k
            except Exception:
                pass
        if CONFIG_FILE.exists():
            try:
                cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
                return cfg.get("api_key", "") or ""
            except Exception:
                pass
        return ""

    def _base_config(self):
        return {
            "lang": self.lang,
            "theme": self.theme,
        }


    def _store_api_key(self, key: str):
        cfg = self._base_config()
        if HAS_KEYRING:
            try:
                if key:
                    keyring.set_password("glm_chat", "api_key", key)
                else:
                    try:
                        keyring.delete_password("glm_chat", "api_key")
                    except Exception:
                        pass
                cfg["api_key_stored"] = "keyring"
                CONFIG_FILE.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
                return
            except Exception:
                pass
        try:
            cfg["api_key"] = key
            CONFIG_FILE.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

    def load_config(self):
        if CONFIG_FILE.exists():
            try:
                cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
                lang = cfg.get("lang", "en")
                if lang in ("en", "fa"):
                    self.lang = lang
                    self.lang_combo.blockSignals(True)
                    self.lang_combo.setCurrentIndex(0 if lang == "en" else 1)
                    self.lang_combo.blockSignals(False)
                theme = cfg.get("theme", "dark")
                if theme in ("dark", "light"):
                    self.theme = theme
                    self.theme_combo.blockSignals(True)
                    self.theme_combo.setCurrentIndex(0 if theme == "dark" else 1)
                    self.theme_combo.blockSignals(False)
            except Exception:
                pass
        key = self._get_api_key()
        if key:
            self.key_input.setText(key)
            self.lock_api_key(silent=True)

    def save_config(self):
        self._store_api_key(self.key_input.text().strip())

    def _on_theme_changed(self, index):
        self.theme = "dark" if index == 0 else "light"
        self._apply_theme()
        self.save_config()


    def _apply_theme(self):
        self.setStyleSheet(APP_QSS if self.theme == "dark" else APP_QSS_LIGHT)


    def lock_api_key(self, silent=False):
        self.key_locked = True
        self.key_input.setEnabled(False)
        self.eye_btn.setEnabled(False)
        self.test_btn.setVisible(False)
        self.change_key_btn.setVisible(True)
        if not silent:
            self._set_status(self.t("status_connected"), is_error=False)
        self.save_config()

    def unlock_api_key(self):
        self.key_locked = False
        self.key_input.setEnabled(True)
        self.eye_btn.setEnabled(True)
        self.test_btn.setVisible(True)
        self.change_key_btn.setVisible(False)
        self._set_status(self.t("status_ready"), is_error=False)
        self.key_input.setFocus()

    # ---------- i18n ----------
    def t(self, key, **kwargs):
        """App translation helper (not Qt's QObject.tr)."""
        text = T[self.lang].get(key, key)
        return text.format(**kwargs) if kwargs else text

    def change_language(self, index):
        self.lang = "en" if index == 0 else "fa"
        self.save_config()
        self.apply_language()

    def apply_language(self):
        self.setWindowTitle(self.t("window_title"))
        self.title_lbl.setText(self.t("brand"))
        self.brand_lbl.setText(self.t("brand"))
        self.subtitle_lbl.setText(self.t("subtitle"))
        self.window_status.setText(self.t("local_client"))
        self.lang_label.setText(self.t("lang"))
        self.key_label.setText(self.t("api_key"))
        self.key_input.setPlaceholderText(self.t("api_placeholder"))
        self.model_label.setText(self.t("model"))
        self.test_btn.setText(self.t("test"))
        self.change_key_btn.setText(self.t("change_key"))
        self.clear_btn.setText(self.t("clear"))
        self.send_btn.setText(self.t("send"))
        self.stop_btn.setText(self.t("stop"))
        self.message_input.setPlaceholderText(self.t("composer_ph"))
        self.attach_btn.setToolTip(self.t("attach_tip"))
        self.files_label.setText(self.t("files_label"))
        self.chats_title.setText(self.t("chats"))
        self.new_chat_btn.setText(self.t("new_chat"))
        self.creator_lbl.setText(self.t("creator"))
        self.theme_label.setText(self.t("theme"))

        # Refresh theme combo labels without changing index
        idx = self.theme_combo.currentIndex()
        self.theme_combo.blockSignals(True)
        self.theme_combo.clear()
        self.theme_combo.addItems([self.t("theme_dark"), self.t("theme_light")])
        self.theme_combo.setCurrentIndex(idx)
        self.theme_combo.blockSignals(False)
        if self.key_locked:
            self._set_status(self.t("status_connected"), is_error=False)
        else:
            self._set_status(self.t("status_ready"), is_error=False)
        # Full RTL for Persian
        app = QApplication.instance()
        if self.lang == "fa":
            self.chat.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
            if app:
                app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        else:
            self.chat.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            if app:
                app.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        # Translate untitled chat titles
        untitled_en = T["en"]["untitled"]
        untitled_fa = T["fa"]["untitled"]
        for c in self.chats:
            if not c.get("titled") or c.get("title") in (untitled_en, untitled_fa, "New Chat", "چت جدید"):
                c["title"] = self.t("untitled")
                c["titled"] = False
        self.refresh_chat_list()
        if self.current_chat_id:
            self.render_current_chat()
        else:
            self.render_welcome()


    # ---------- History ----------
    def load_history(self):
        if HISTORY_FILE.exists():
            try:
                self.chats = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
            except Exception:
                self.chats = []
        else:
            self.chats = []

    def save_history(self):
        try:
            tmp = HISTORY_FILE.with_suffix(".tmp")
            tmp.write_text(json.dumps(self.chats, ensure_ascii=False, indent=2), encoding="utf-8")
            os.replace(tmp, HISTORY_FILE)
        except Exception:
            pass

    def refresh_chat_list(self):
        """لیست کاملاً تمیز و یکدست – فقط عنوان"""
        self.chat_list.clear()
        for chat in sorted(self.chats, key=lambda c: c.get("updated", ""), reverse=True):
            title = chat.get("title") or self.t("untitled")
            # کوتاه کردن عنوان خیلی بلند
            if len(title) > 38:
                title = title[:36] + "…"
            item = QListWidgetItem(title)
            item.setData(Qt.ItemDataRole.UserRole, chat["id"])
            item.setSizeHint(QSize(0, 42))  # ارتفاع ثابت و یکدست
            self.chat_list.addItem(item)
            if chat["id"] == self.current_chat_id:
                self.chat_list.setCurrentItem(item)

    def show_chat_context_menu(self, pos):
        item = self.chat_list.itemAt(pos)
        if not item:
            return
        menu = QMenu(self)
        delete_action = QAction(self.t("delete_chat"), self)
        delete_action.triggered.connect(lambda: self.delete_chat(item.data(Qt.ItemDataRole.UserRole)))
        menu.addAction(delete_action)
        menu.exec(self.chat_list.mapToGlobal(pos))

    def delete_chat(self, chat_id):
        self.chats = [c for c in self.chats if c["id"] != chat_id]
        self.save_history()
        if self.current_chat_id == chat_id:
            if self.chats:
                self.select_chat(self.chats[0]["id"])
            else:
                self.create_new_chat()
        else:
            self.refresh_chat_list()

    def create_new_chat(self):
        # Save draft attachments of current chat before switching
        self._save_draft_attachments()
        chat_id = str(uuid.uuid4())
        chat = {
            "id": chat_id,
            "title": self.t("untitled"),
            "titled": False,
            "messages": [],
            "updated": datetime.now().isoformat(),
            "draft_attachments": [],
        }
        self.chats.insert(0, chat)
        self.current_chat_id = chat_id
        self.save_history()
        self.refresh_chat_list()
        self.render_welcome()
        self.clear_attachments()
        self._user_near_bottom = True

    def on_chat_selected(self, item):
        self.select_chat(item.data(Qt.ItemDataRole.UserRole))

    def _save_draft_attachments(self):
        """Persist current composer attachments into the active chat draft."""
        if not self.current_chat_id:
            return
        for c in self.chats:
            if c["id"] == self.current_chat_id:
                c["draft_attachments"] = list(self.attached_files)
                break

    def _load_draft_attachments(self, chat_id):
        self.attached_files = []
        for c in self.chats:
            if c["id"] == chat_id:
                self.attached_files = list(c.get("draft_attachments") or [])
                break
        self._rebuild_attach_list()

    def select_chat(self, chat_id):
        # Save scroll + draft of previous chat
        if self.current_chat_id and self.current_chat_id != chat_id:
            sb = self.chat.verticalScrollBar()
            self._scroll_positions[self.current_chat_id] = sb.value()
            self._save_draft_attachments()
        self.current_chat_id = chat_id
        self._load_draft_attachments(chat_id)
        self.render_current_chat()
        # Restore scroll position
        pos = self._scroll_positions.get(chat_id)
        if pos is not None:
            self.chat.verticalScrollBar().setValue(pos)
            self._on_scroll_changed(pos)
        else:
            self._user_near_bottom = True
            sb = self.chat.verticalScrollBar()
            sb.setValue(sb.maximum())
        self.refresh_chat_list()
        # Sync Send/Stop buttons with the generation state of the *visible* chat
        w = self._workers_by_chat.get(chat_id)
        if w and w.isRunning() and w.generation_id not in self._cancelled_generations:
            self.worker = w
            self.send_btn.setEnabled(False)
            self.send_btn.setVisible(False)
            self.stop_btn.setVisible(True)
            model_name = self.model_combo.currentText()
            self._set_status(self.t("status_thinking", model=model_name), is_error=False)
        else:
            # Not generating in this chat — show Send
            self.send_btn.setEnabled(True)
            self.send_btn.setVisible(True)
            self.stop_btn.setVisible(False)
            ready = self.t("status_ready") if not self.key_locked else self.t("status_connected")
            self._set_status(ready, is_error=False)
            # Keep self.worker pointing at any still-running worker for cleanup,
            # but Stop only acts on the visible chat's worker
            running = next(
                (x for x in self._workers_by_chat.values()
                 if x.isRunning() and x.generation_id not in self._cancelled_generations),
                None,
            )
            self.worker = running


    def get_current_chat(self):
        for c in self.chats:
            if c["id"] == self.current_chat_id:
                return c
        return None

    def render_current_chat(self):
        chat = self.get_current_chat()
        if not chat or not chat["messages"]:
            self.render_welcome()
            return
        self.chat.clear()
        self._thinking_active = False
        for msg in chat["messages"]:
            self._render_bubble(
                msg["role"],
                msg.get("display") or msg["content"],
                is_error=bool(msg.get("is_error")),
                is_stopped=bool(msg.get("is_stopped")),
                ts=msg.get("ts"),
            )
        # If this chat still has an active generation, show thinking again
        w = self._workers_by_chat.get(chat["id"])
        if w and w.isRunning() and w.generation_id not in self._cancelled_generations:
            self.show_thinking_bubble()
        if self._user_near_bottom:
            self.chat.verticalScrollBar().setValue(self.chat.verticalScrollBar().maximum())


    def render_welcome(self):
        dir_attr = 'dir="rtl"' if self.lang == "fa" else 'dir="ltr"'
        self.chat.setHtml(f"""
        <html><body style="font-family:Segoe UI,Tahoma;color:#dceaff;" {dir_attr}>
        <div style="height:100px"></div>
        <div align="center">
          <div style="font-size:48px;color:#08baff;">◎</div>
          <div style="font-size:19px;font-weight:700;color:#8db8ff;margin-top:8px;">{self.t("welcome_title")}</div>
          <p style="font-size:13px;color:#7e9fd8;line-height:1.75;max-width:520px;margin:12px auto;">{self.t("welcome_body")}</p>
        </div></body></html>
        """)

    def _fix_bidi(self, text: str) -> str:
        """Insert Unicode LRM/RLM marks so mixed FA+EN order stays correct in RTL/LTR.
        Only runs when Persian characters are present; avoids breaking markdown syntax.
        """
        persian_chars = len(re.findall(r'[آ-یءۀةؤئأإآ]', text))
        if persian_chars == 0:
            return text  # pure Latin — no need for bidi fixes
        LRM = "\u200E"  # Left-to-Right Mark
        RLM = "\u200F"  # Right-to-Left Mark
        # Protect inline code first
        def wrap_code(m):
            return LRM + m.group(0) + LRM
        text = re.sub(r'`[^`\n]+`', wrap_code, text)
        # Latin / number runs — exclude markdown-significant chars (* _ [ ] ( ))
        def wrap_latin(m):
            s = m.group(0)
            if not re.search(r'[A-Za-z0-9]', s):
                return s
            return LRM + s + LRM
        text = re.sub(
            r'(?<![آ-یءۀةؤئأإآ])([A-Za-z0-9][A-Za-z0-9_./\\:+\-#@%=<>{},;!?]{0,})(?![آ-یءۀةؤئأإآ])',
            wrap_latin,
            text,
        )
        latin_chars = len(re.findall(r'[A-Za-z]', text))
        if persian_chars > latin_chars:
            text = RLM + text
        return text


    def _format_code_block(self, lang: str, code: str) -> str:
        """ChatGPT-style code card: language label + Copy link + dark monospace body."""
        cid = uuid.uuid4().hex[:10]
        self._code_store[cid] = code
        lang_label = (lang or "code").strip() or "code"
        # Cap store growth
        if len(self._code_store) > 200:
            for k in list(self._code_store.keys())[:50]:
                del self._code_store[k]
        escaped = html.escape(code.rstrip("\n"))
        tip = html.escape(self.t("copy_code"))
        # ChatGPT-style: language left, gray icon-only copy on the right (not a blue link)
        # Use fixed-width icon chars so Copy ↔ checkmark does not jump layout
        return (
            f'<table width="100%" cellspacing="0" cellpadding="0" style="margin:12px 0;" dir="ltr">'
            f'<tr><td style="background:#1e1e2e;border:1px solid #45475a;border-radius:10px;">'
            f'<table width="100%" cellspacing="0" cellpadding="0">'
            f'<tr>'
            f'<td style="padding:8px 12px;background:#181825;border-bottom:1px solid #313244;">'
            f'<span style="color:#a6adc8;font-size:11px;font-family:Consolas,monospace;">{html.escape(lang_label)}</span>'
            f'</td>'
            f'<td align="right" width="36" style="padding:8px 12px;background:#181825;border-bottom:1px solid #313244;">'
            f'<a href="copy:{cid}" title="{tip}" '
            f'style="color:#a6adc8;font-size:14px;text-decoration:none;font-family:Segoe UI,sans-serif;">'
            f'❐</a>'
            f'</td>'
            f'</tr>'
            f'<tr><td colspan="2" style="padding:12px 14px;">'
            f'<pre style="margin:0;color:#cdd6f4;font-family:Consolas,\'Courier New\',monospace;'
            f'font-size:12.5px;line-height:1.55;white-space:pre-wrap;">{escaped}</pre>'
            f'</td></tr></table></td></tr></table>'
        )

    def _md_to_html(self, text: str) -> str:
        """Markdown → HTML with ChatGPT-like fenced code blocks and Copy buttons."""
        blocks = []

        def _save_fence(m):
            lang = m.group(1) or ""
            code = m.group(2)
            idx = len(blocks)
            blocks.append(self._format_code_block(lang, code))
            return f"\n%%CODEBLOCK{idx}%%\n"

        # Extract fenced code first (before any escaping)
        work = re.sub(r"```(\w*)\r?\n([\s\S]*?)```", _save_fence, text)

        # Bidi-fix only prose segments — never touch %%CODEBLOCKn%% tokens
        parts = re.split(r"(%%CODEBLOCK\d+%%)", work)
        for i, part in enumerate(parts):
            if not re.fullmatch(r"%%CODEBLOCK\d+%%", part):
                parts[i] = self._fix_bidi(part)
        work = "".join(parts)

        if HAS_MARKDOWN:
            try:
                # Avoid double-processing fences we already extracted
                body = md_lib.markdown(work, extensions=["tables", "nl2br", "sane_lists"])
            except Exception:
                body = None
        else:
            body = None

        if body is None:
            body = html.escape(work)
            body = re.sub(r"`([^`]+)`", r'<code style="background:#313244;color:#f5e0dc;padding:1px 5px;border-radius:4px;font-family:Consolas,monospace;font-size:12px;" dir="ltr">\1</code>', body)
            body = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", body)
            body = re.sub(r"(?m)^### (.+)$", r"<b style='font-size:14px;'>\1</b>", body)
            body = re.sub(r"(?m)^## (.+)$", r"<b style='font-size:15px;'>\1</b>", body)
            body = body.replace("\n", "<br>")

        for i, html_block in enumerate(blocks):
            token = f"%%CODEBLOCK{i}%%"
            # markdown may wrap token in <p>
            body = body.replace(f"<p>{token}</p>", html_block)
            body = body.replace(token, html_block)
        return body

    def _on_chat_link(self, url: QUrl):
        """Handle Copy links inside code blocks; open normal http(s) links externally."""
        s = url.toString()
        if s.startswith("copy:"):
            cid = s[5:]
            code = self._code_store.get(cid, "")
            if code:
                QApplication.clipboard().setText(code)
                self._set_status(self.t("copied"), is_error=False)
                self._flash_copy_feedback(cid)
            return
        if s.startswith("http://") or s.startswith("https://"):
            QDesktopServices.openUrl(url)

    def _flash_copy_feedback(self, cid: str):
        """ChatGPT-style: icon ❐ → ✓ (same size), tooltip Copied, restore after 2s."""
        copied_lbl = self.t("copied")
        tip_copied = html.escape(copied_lbl)
        doc_html = self.chat.toHtml()
        # Swap only the icon character; keep fixed single-glyph width
        pattern = rf'(<a\s+href="copy:{re.escape(cid)}"[^>]*>)(.*?)(</a>)'
        new_html = re.sub(
            pattern,
            rf'\1✓\3',
            doc_html,
            count=1,
            flags=re.IGNORECASE | re.DOTALL,
        )
        # Also bump title to "Copied" when possible
        new_html = new_html.replace(
            f'href="copy:{cid}" title="{html.escape(self.t("copy_code"))}"',
            f'href="copy:{cid}" title="{tip_copied}"',
            1,
        )
        if new_html != doc_html:
            sb = self.chat.verticalScrollBar()
            pos = sb.value()
            self.chat.setHtml(new_html)
            sb.setValue(pos)
            self._pending_copy_restore = (cid, pos)
        # Optional tiny toast (non-blocking), ChatGPT mainly relies on icon change
        self._copy_toast.setText(f"✓  {copied_lbl}")
        self._copy_toast.adjustSize()
        cw = self.chat.width()
        ch = self.chat.height()
        tw = self._copy_toast.width()
        th = self._copy_toast.height()
        self._copy_toast.move(max(8, (cw - tw) // 2), max(8, ch - th - 24))
        self._copy_toast.show()
        self._copy_toast.raise_()
        self._copy_toast_timer.start(2000)

    def _hide_copy_feedback(self):
        """Restore copy icon ❐ and hide toast."""
        self._copy_toast.hide()
        pending = getattr(self, "_pending_copy_restore", None)
        if not pending:
            return
        cid, pos = pending
        self._pending_copy_restore = None
        tip = html.escape(self.t("copy_code"))
        doc_html = self.chat.toHtml()
        pattern = rf'(<a\s+href="copy:{re.escape(cid)}"[^>]*>)(.*?)(</a>)'
        new_html = re.sub(
            pattern,
            rf'\1❐\3',
            doc_html,
            count=1,
            flags=re.IGNORECASE | re.DOTALL,
        )
        new_html = re.sub(
            rf'href="copy:{re.escape(cid)}" title="[^"]*"',
            f'href="copy:{cid}" title="{tip}"',
            new_html,
            count=1,
        )
        if new_html != doc_html:
            sb = self.chat.verticalScrollBar()
            self.chat.setHtml(new_html)
            sb.setValue(pos)

    def _render_bubble(self, role, display_text, is_thinking=False, is_error=False,
                       is_stopped=False, ts=None):
        """Render a chat bubble using Qt-safe table layout + bidi fixes."""
        text = str(display_text) if display_text is not None else ""
        is_user = role == "user"
        if role == "assistant" and not is_thinking and not is_error and not is_stopped:
            # Markdown + code cards first (preserve ``` fences); apply light bidi on plain parts
            safe = self._md_to_html(text)
        else:
            text = self._fix_bidi(text)
            safe = html.escape(text).replace("\n", "<br>")

        display_role = self.t("you") if is_user else self.model_combo.currentText()
        if ts:
            try:
                stamp = datetime.fromisoformat(ts).strftime("%H:%M")
            except Exception:
                stamp = datetime.now().strftime("%H:%M")
        else:
            stamp = datetime.now().strftime("%H:%M")
        # Optional length hint for assistant replies
        char_hint = ""
        if role == "assistant" and not is_thinking and not is_error and not is_stopped and text:
            char_hint = f' · {self.t("chars", n=len(text))}'
        dir_attr = 'dir="auto"'

        if is_thinking:
            color = "#67e8f9"
            bg = "#0a1f3a"
            border = "#0e7490"
            role_label = self.t("processing")
            body_color = "#a5f3fc"
            border_style = "dashed"
        elif is_stopped:
            color = "#fbbf24"
            bg = "#1c1917"
            border = "#a16207"
            role_label = self.t("status_stopped")
            body_color = "#fde68a"
            border_style = "dashed"
        elif is_error:
            color = "#fb7185"
            bg = "#2a1220"
            border = "#be123c"
            role_label = "⚠ Error"
            body_color = "#fecdd3"
            border_style = "solid"
        elif is_user:
            color = "#38bdf8"
            bg = "#0c2348"
            border = "#1e40af"
            role_label = display_role
            body_color = "#f1f5f9"
            border_style = "solid"
        else:
            color = "#c4b5fd"
            bg = "#131c38"
            border = "#4c1d95"
            role_label = display_role
            body_color = "#f1f5f9"
            border_style = "solid"

        block = f"""
        <table width="100%" cellspacing="0" cellpadding="0" style="margin:10px 0;" {dir_attr}>
          <tr>
            <td style="background:{bg};border:1px {border_style} {border};border-radius:12px;
                       padding:12px 15px;">
              <div style="color:{color};font-weight:700;font-size:12px;">
                {role_label}
                <span style="color:#64748b;font-weight:400;font-size:10.5px;"> · {stamp}{char_hint}</span>
              </div>
              <div style="margin-top:7px;color:{body_color};font-size:13.5px;line-height:1.7;
                          word-wrap:break-word;" {dir_attr}>{safe}</div>
            </td>
          </tr>
        </table>
        """
        cursor = self.chat.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertHtml(block)
        self.chat.setTextCursor(cursor)
        if self._user_near_bottom:
            self.chat.ensureCursorVisible()
            sb = self.chat.verticalScrollBar()
            sb.setValue(sb.maximum())


    def show_thinking_bubble(self):
        """Insert a temporary thinking indicator inside the chat (not saved to history)."""
        self._thinking_active = True
        model = self.model_combo.currentText()
        text = self.t("thinking_bubble", model=model)
        self._render_bubble("assistant", text, is_thinking=True)

    def remove_thinking_bubble(self):
        """Remove the last thinking bubble by re-rendering real messages."""
        if getattr(self, "_thinking_active", False):
            self._thinking_active = False
            self.render_current_chat()

    def _slim_for_history(self, content):
        """Strip base64 image payloads and truncate large text before saving to disk."""
        if isinstance(content, list):
            slim = []
            for p in content:
                if isinstance(p, dict) and p.get("type") == "image_url":
                    name = "image"
                    url = (p.get("image_url") or {}).get("url", "")
                    if isinstance(url, str) and url.startswith("data:"):
                        name = "embedded-image"
                    slim.append({"type": "text", "text": f"[Attached image: {name}]"})
                elif isinstance(p, dict) and p.get("type") == "text":
                    t = p.get("text", "")
                    if isinstance(t, str) and len(t.encode("utf-8", errors="ignore")) > MAX_TEXT_IN_HISTORY:
                        # Keep head for history; full content was already sent to the API
                        head = t[:MAX_TEXT_IN_HISTORY]
                        slim.append({
                            "type": "text",
                            "text": head + "\n\n" + self.t("history_trimmed"),
                        })
                    else:
                        slim.append(p)
                else:
                    slim.append(p)
            return slim
        if isinstance(content, str) and len(content.encode("utf-8", errors="ignore")) > MAX_TEXT_IN_HISTORY:
            return content[:MAX_TEXT_IN_HISTORY] + "\n\n" + self.t("history_trimmed")
        return content

    def append_message(self, role, api_content, display_content=None, is_error=False, is_stopped=False):
        """Append to the *current* chat and update UI (for user messages & current-view replies)."""
        chat = self.get_current_chat()
        if chat is None:
            return
        self._append_to_chat_id(
            chat["id"], role, api_content, display_content,
            is_error=is_error, is_stopped=is_stopped
        )

    def _append_to_chat_id(self, chat_id, role, api_content, display_content=None,
                           is_error=False, is_stopped=False):
        """Append a message to a specific chat by id. UI updates only if that chat is visible."""
        if display_content is None:
            display_content = api_content if isinstance(api_content, str) else str(api_content)
        chat = None
        for c in self.chats:
            if c["id"] == chat_id:
                chat = c
                break
        if chat is None:
            return
        now_iso = datetime.now().isoformat()
        chat["messages"].append({
            "role": role,
            "content": self._slim_for_history(api_content),
            "display": display_content,
            "is_error": bool(is_error),
            "is_stopped": bool(is_stopped),
            "ts": now_iso,
        })
        # Cap history length per chat
        if len(chat["messages"]) > MAX_HISTORY_MESSAGES:
            chat["messages"] = chat["messages"][-MAX_HISTORY_MESSAGES:]
        chat["updated"] = now_iso
        if role == "user" and not chat.get("titled", False):
            chat["title"] = self._make_smart_title(display_content)
            chat["titled"] = True
        self.save_history()
        self.refresh_chat_list()
        # Only touch the visible chat UI
        if self.current_chat_id == chat_id:
            try:
                if getattr(self, "_thinking_active", False):
                    self._thinking_active = False
                    self.render_current_chat()
                    return
                self._render_bubble(
                    role, display_content,
                    is_error=is_error, is_stopped=is_stopped, ts=now_iso
                )
            except Exception:
                self.chat.append(f"\n[{role}] {display_content}\n")


    def _make_smart_title(self, text: str) -> str:
        text = str(text).strip()
        if text.startswith("📎") or text.startswith("🖼"):
            return text[:42]
        words = text.replace("\n", " ").split()
        title = " ".join(words[:6])
        if len(title) > 40:
            title = title[:40] + "…"
        return title or self.t("untitled")

    # ---------- Files ----------
    def pick_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select files or images", "",
            "All files (*.*);;Images (*.png *.jpg *.jpeg *.gif *.webp *.bmp);;Code (*.py *.php *.js *.ts *.java *.c *.cpp *.html *.css *.json *.md)"
        )
        for f in files:
            self.start_file_load(Path(f))

    def start_file_load(self, path: Path):
        if not path.exists() or not path.is_file():
            return
        self.pending_loads += 1
        self.send_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.files_frame.setVisible(True)
        self.status_label.setText(self.t("uploading"))
        worker = FileLoadWorker(path)
        worker.progress.connect(self.on_load_progress)
        worker.result_ready.connect(self.on_load_finished)
        worker.error.connect(self.on_load_error)
        self._track_worker(worker)
        self._load_workers.append(worker)
        worker.start()



    def on_load_progress(self, pct, name):
        self.progress.setValue(pct)
        self.status_label.setText(self.t("status_uploading", name=name, pct=pct))

    def on_load_finished(self, file_dict):
        self.attached_files.append(file_dict)
        self.pending_loads = max(0, self.pending_loads - 1)
        self._rebuild_attach_list()
        if self.pending_loads == 0:
            self.progress.setVisible(False)
            self.send_btn.setEnabled(True)
            self.status_label.setText(self.t("file_added", name=file_dict["name"]))

    def on_load_error(self, err):
        self.pending_loads = max(0, self.pending_loads - 1)
        if err == "too_large":
            QMessageBox.warning(self, "File", self.t("file_too_large", name="file"))
        else:
            QMessageBox.warning(self, "File", str(err))
        if self.pending_loads == 0:
            self.progress.setVisible(False)
            self.send_btn.setEnabled(True)

    def _rebuild_attach_list(self):
        while self.attach_container.count():
            item = self.attach_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for idx, f in enumerate(self.attached_files):
            row = QWidget()
            lay = QHBoxLayout(row)
            lay.setContentsMargins(4, 2, 4, 2)
            icon = "🖼" if f["type"] == "image" else "📄"
            lbl = QLabel(f"{icon}  {f['name']}")
            lbl.setStyleSheet("color:#c7d7f5;")
            lay.addWidget(lbl, 1)
            del_btn = QPushButton("×")
            del_btn.setObjectName("delBtn")
            del_btn.setFixedSize(26, 26)
            del_btn.clicked.connect(lambda checked=False, i=idx: self.remove_attachment(i))
            lay.addWidget(del_btn)
            self.attach_container.addWidget(row)
        self.files_frame.setVisible(bool(self.attached_files) or self.pending_loads > 0)

    def remove_attachment(self, index):
        if 0 <= index < len(self.attached_files):
            self.attached_files.pop(index)
            self._rebuild_attach_list()
            if not self.attached_files and self.pending_loads == 0:
                self.files_frame.setVisible(False)

    def clear_attachments(self):
        self.attached_files.clear()
        self.pending_loads = 0
        self._rebuild_attach_list()
        self.progress.setVisible(False)
        self.files_frame.setVisible(False)
        if self.current_chat_id:
            for c in self.chats:
                if c["id"] == self.current_chat_id:
                    c["draft_attachments"] = []
                    break

    def build_api_and_display(self, user_text: str):

        display_parts = []
        content_list = []

        if user_text.strip():
            display_parts.append(user_text.strip())
            content_list.append({"type": "text", "text": user_text.strip()})

        for f in self.attached_files:
            if f["type"] == "image":
                display_parts.append(self.t("sent_image", name=f["name"]))
                content_list.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:{f['mime']};base64,{f['base64']}"}
                })
            else:
                display_parts.append(self.t("sent_file", name=f["name"]))
                lang = Path(f["name"]).suffix.lstrip(".") or "text"
                content_list.append({
                    "type": "text",
                    "text": f"\n\n===== Attached file: {f['name']} =====\n```{lang}\n{f['text']}\n```\n===== End of file ====="
                })

        if not user_text.strip() and self.attached_files:
            content_list.insert(0, {"type": "text", "text": "Please analyze / improve / expand the attached file(s)."})

        display_content = "\n".join(display_parts) if display_parts else "(empty)"

        if len(content_list) == 1 and content_list[0]["type"] == "text":
            api_content = content_list[0]["text"]
        else:
            api_content = content_list

        return api_content, display_content

    # Drag & Drop
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            local = url.toLocalFile()
            if local:
                path = Path(local)
                if path.is_file():
                    self.start_file_load(path)

    def eventFilter(self, obj, event):
        if obj is self.message_input and event.type() == QEvent.Type.KeyPress:
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and not (
                event.modifiers() & Qt.KeyboardModifier.ShiftModifier
            ):
                self.send_message()
                return True
        return super().eventFilter(obj, event)

    # Actions
    def toggle_api_visibility(self):
        self.api_key_visible = not self.api_key_visible
        self.key_input.setEchoMode(
            QLineEdit.EchoMode.Normal if self.api_key_visible else QLineEdit.EchoMode.Password
        )
        self.eye_btn.setText("🙈" if self.api_key_visible else "👁")

    def test_connection(self):
        key = self.key_input.text().strip()
        if not key:
            QMessageBox.warning(self, "API Key", self.t("key_empty"))
            return
        self.test_btn.setEnabled(False)
        self.status_label.setText("Testing..." if self.lang == "en" else "در حال تست...")
        # Cancel previous test if still running
        if self.test_worker is not None and self.test_worker.isRunning():
            try:
                self.test_worker.quit()
            except Exception:
                pass
        self.test_worker = TestWorker(key)
        self.test_worker.result_ready.connect(self.on_test_ok)
        self.test_worker.error.connect(self.on_test_error)
        self._track_worker(self.test_worker)
        self.test_worker.start()



    def on_test_ok(self, models_str):
        self.test_btn.setEnabled(True)
        self.lock_api_key()
        # Populate model combo from server list
        models = [m.strip().lstrip("•").strip() for m in models_str.replace("\n", "•").split("•") if m.strip()]
        if models:
            current = self.model_combo.currentText()
            self.model_combo.clear()
            self.model_combo.addItems(models)
            idx = self.model_combo.findText(current)
            if idx >= 0:
                self.model_combo.setCurrentIndex(idx)
        QMessageBox.information(self, "Test", self.t("test_ok", models=models_str))

    def on_test_error(self, err):
        self.test_btn.setEnabled(True)
        self._set_status(self.t("status_failed") + " — " + str(err)[:80], is_error=True)
        QMessageBox.critical(self, "Error", self.t("test_fail", error=err))

    def clear_current_chat(self):
        if QMessageBox.question(
            self, self.t("clear_title"), self.t("clear_msg"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes:
            chat = self.get_current_chat()
            if chat:
                chat["messages"] = []
                chat["title"] = self.t("untitled")
                chat["titled"] = False
                self.save_history()
            self.clear_attachments()
            self.render_welcome()
            self.refresh_chat_list()
            self._set_status(self.t("status_cleared"), is_error=False)

    def _set_status(self, text, is_error=False):
        """Update status bar text and visual state (color of label + dot)."""
        self.status_label.setText(text)
        self.status_label.setProperty("error", "true" if is_error else "false")
        self.status_dot.setProperty("error", "true" if is_error else "false")
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)
        self.status_dot.style().unpolish(self.status_dot)
        self.status_dot.style().polish(self.status_dot)

    def send_message(self):
        if self.pending_loads > 0:
            return
        text = self.message_input.toPlainText().strip()
        if not text and not self.attached_files:
            return
        key = self.key_input.text().strip()
        if not key:
            QMessageBox.warning(self, "API Key", self.t("key_empty"))
            return

        chat = self.get_current_chat()
        if not chat:
            return

        # If this chat already has a running generation, stop it first
        old_worker = self._workers_by_chat.get(chat["id"])
        if old_worker and old_worker.isRunning():
            self._cancel_worker(old_worker)

        api_content, display_content = self.build_api_and_display(text)
        self.append_message("user", api_content, display_content)
        self.message_input.clear()
        self.clear_attachments()

        # Only last 20 messages to API (avoids huge base64 / context)
        recent = chat["messages"][-20:] if chat else []
        messages_for_api = [{"role": m["role"], "content": m["content"]} for m in recent]

        self.send_btn.setEnabled(False)
        self.send_btn.setVisible(False)
        self.stop_btn.setVisible(True)
        model_name = self.model_combo.currentText()
        self._set_status(self.t("status_thinking", model=model_name), is_error=False)

        # Reset per-chat stream buffers
        self._stream_data[chat["id"]] = {"text": "", "buffer": ""}
        self._thinking_active = False
        self._user_near_bottom = True
        self.show_thinking_bubble()

        generation_id = str(uuid.uuid4())
        self._active_chat_id = chat["id"]
        self._active_generation_id = generation_id

        worker = ApiWorker(
            key, model_name, messages_for_api, chat["id"], generation_id,
            temperature=self.temperature, max_tokens=self.max_tokens,
            parent=self
        )
        worker.chunk.connect(self.on_stream_chunk)
        worker.reply_ready.connect(self.on_reply)
        worker.error.connect(self.on_error)
        worker.stopped.connect(self.on_stopped)
        self._track_worker(worker)
        self.worker = worker
        self._workers_by_chat[chat["id"]] = worker
        worker.start()

    def _stream_for(self, chat_id: str) -> dict:
        if chat_id not in self._stream_data:
            self._stream_data[chat_id] = {"text": "", "buffer": ""}
        return self._stream_data[chat_id]

    def _on_scroll_changed(self, value: int):
        sb = self.chat.verticalScrollBar()
        # Consider "near bottom" if within 80px of the end
        self._user_near_bottom = (sb.maximum() - value) < 80

    def _cancel_worker(self, worker: ApiWorker):
        """Mark generation cancelled and request stop; reply will be discarded.
        Keeps a strong ref in _live_workers until the OS thread exits.
        """
        if worker is None:
            return
        self._cancelled_generations.add(worker.generation_id)
        try:
            worker.stop()
        except Exception:
            pass

    def stop_generation(self):
        """User pressed Stop — cancel generation for the *visible* chat only."""
        chat_id = self.current_chat_id
        worker = self._workers_by_chat.get(chat_id) if chat_id else None
        if not worker or not worker.isRunning():
            self._finish_generation_ui()
            return
        self._stream_timer.stop()
        self._cancel_worker(worker)
        # Capture any partial stream text for this generation (per-chat)
        sd = self._stream_for(chat_id)
        partial = (sd.get("text", "") + sd.get("buffer", "")).strip()
        sd["text"] = ""
        sd["buffer"] = ""
        self._thinking_active = False
        # Write stopped bubble into the chat that was generating
        self.render_current_chat()
        if partial:
            msg = self.t("stopped_partial", partial=partial)
        else:
            msg = self.t("stopped_bubble")
        self._append_to_chat_id(worker.chat_id, "assistant", msg, msg, is_error=False, is_stopped=True)
        self._set_status(self.t("status_stopped"), is_error=False)
        self._finish_generation_ui()

    def _finish_generation_ui(self):
        self.send_btn.setEnabled(True)
        self.send_btn.setVisible(True)
        self.stop_btn.setVisible(False)
        self.message_input.setFocus()
        self._thinking_active = False
        self._stream_timer.stop()

    def _is_worker_valid(self, worker) -> bool:
        """True if this worker's generation is still the active one and not cancelled."""
        if worker is None:
            return False
        if worker.generation_id in self._cancelled_generations:
            return False
        return True

    def on_stream_chunk(self, piece: str):
        """Buffer tokens per-chat; only paint if viewing that chat."""
        worker = self.sender()
        if not isinstance(worker, ApiWorker) or not self._is_worker_valid(worker):
            return
        if not piece:
            return
        sd = self._stream_for(worker.chat_id)
        sd["buffer"] += piece
        # Only stream into UI when user is viewing the same chat
        if self.current_chat_id != worker.chat_id:
            return
        if not self._stream_timer.isActive():
            self._stream_timer.start()

    def _flush_stream(self):
        chat_id = self.current_chat_id
        if not chat_id:
            self._stream_timer.stop()
            return
        sd = self._stream_for(chat_id)
        if not sd.get("buffer"):
            self._stream_timer.stop()
            return
        worker = self._workers_by_chat.get(chat_id)
        if not self._is_worker_valid(worker) or self.current_chat_id != getattr(worker, "chat_id", None):
            sd["buffer"] = ""
            self._stream_timer.stop()
            return
        buf = sd["buffer"]
        sd["buffer"] = ""
        if getattr(self, "_thinking_active", False):
            self._thinking_active = False
            self.render_current_chat()
            sd["text"] = ""
        sd["text"] = sd.get("text", "") + buf
        chat = self.get_current_chat()
        if chat is None:
            return
        self.chat.clear()
        for msg in chat["messages"]:
            self._render_bubble(
                msg["role"],
                msg.get("display") or msg["content"],
                is_error=bool(msg.get("is_error")),
                is_stopped=bool(msg.get("is_stopped")),
                ts=msg.get("ts"),
            )
        self._render_bubble("assistant", sd["text"])
        if self._user_near_bottom:
            sb = self.chat.verticalScrollBar()
            sb.setValue(sb.maximum())


    def on_reply(self, reply):
        worker = self.sender()
        try:
            if not isinstance(worker, ApiWorker):
                worker = self.worker
            # Discard late / cancelled replies so they never leak into another chat
            if not self._is_worker_valid(worker):
                return
            self._flush_stream()
            sd = self._stream_for(worker.chat_id)
            final = (reply or sd.get("text", "") or "").strip()
            self._thinking_active = False
            sd["text"] = ""
            sd["buffer"] = ""
            if final:
                self._append_to_chat_id(worker.chat_id, "assistant", final, final)
            elif self.current_chat_id == worker.chat_id:
                self.render_current_chat()
            if self.current_chat_id == worker.chat_id:
                ready = self.t("status_ready") if not self.key_locked else self.t("status_connected")
                self._set_status(ready, is_error=False)
                if self._user_near_bottom:
                    sb = self.chat.verticalScrollBar()
                    sb.setValue(sb.maximum())
        except Exception as e:
            self._set_status(f"UI error: {e}", is_error=True)
        finally:
            self._cleanup_worker(worker)
            if self.worker is worker or self.current_chat_id == getattr(worker, "chat_id", None):
                self._finish_generation_ui()
            if worker and getattr(worker, "chat_id", None):
                sd = self._stream_for(worker.chat_id)
                sd["text"] = ""
                sd["buffer"] = ""

    def on_stopped(self, partial: str):
        """Worker finished after user pressed Stop (may carry partial text)."""
        worker = self.sender()
        try:
            if not isinstance(worker, ApiWorker):
                return
            # stop_generation already wrote the stopped bubble; just clean up
            if worker.generation_id not in self._cancelled_generations:
                self._cancelled_generations.add(worker.generation_id)
                partial = (partial or "").strip()
                if partial:
                    msg = self.t("stopped_partial", partial=partial)
                else:
                    msg = self.t("stopped_bubble")
                self._append_to_chat_id(worker.chat_id, "assistant", msg, msg, is_stopped=True)
        except Exception:
            pass
        finally:
            self._cleanup_worker(worker)
            if self.worker is worker or self.current_chat_id == getattr(worker, "chat_id", None):
                self._finish_generation_ui()
            if worker and getattr(worker, "chat_id", None):
                sd = self._stream_for(worker.chat_id)
                sd["text"] = ""
                sd["buffer"] = ""

    def on_error(self, err):
        worker = self.sender()
        try:
            if not isinstance(worker, ApiWorker):
                worker = self.worker
            if not self._is_worker_valid(worker):
                return
            if err == "conn":
                msg = self.t("conn_error")
                status_msg = self.t("status_error_conn")
            elif err == "timeout":
                msg = self.t("timeout")
                status_msg = self.t("status_error_timeout")
            else:
                # Friendlier API error display
                err_s = str(err)
                if err_s.startswith("HTTP 401") or "unauthorized" in err_s.lower():
                    msg = self.t("generic_error", error="Invalid API Key (401)")
                elif err_s.startswith("HTTP 429"):
                    msg = self.t("generic_error", error="Rate limited (429) — wait a moment")
                elif err_s.startswith("HTTP 5"):
                    msg = self.t("generic_error", error=f"Server error — {err_s[:80]}")
                else:
                    msg = self.t("generic_error", error=err_s)
                status_msg = self.t("status_error_detail", error=str(err)[:120])
            self._thinking_active = False
            if worker and getattr(worker, "chat_id", None):
                sd = self._stream_for(worker.chat_id)
                sd["text"] = ""
                sd["buffer"] = ""
            self._append_to_chat_id(
                worker.chat_id, "assistant", f"⚠ {msg}", f"⚠ {msg}", is_error=True
            )
            if self.current_chat_id == worker.chat_id:
                self._set_status(status_msg, is_error=True)
        except Exception as e:
            self._set_status(f"UI error: {e}", is_error=True)
        finally:
            self._cleanup_worker(worker)
            if self.worker is worker or self.current_chat_id == getattr(worker, "chat_id", None):
                self._finish_generation_ui()
            if worker and getattr(worker, "chat_id", None):
                sd = self._stream_for(worker.chat_id)
                sd["text"] = ""
                sd["buffer"] = ""

            self._stream_buffer = ""

    def _track_worker(self, worker: QThread):
        """Keep a strong reference until the OS thread has exited.
        Connects to QThread.finished so deleteLater is called only after run() returns.
        """
        if worker is None:
            return
        self._live_workers.add(worker)
        worker.finished.connect(lambda w=worker: self._on_thread_really_finished(w))


    def _cleanup_worker(self, worker):
        """Drop chat mapping / UI pointer. Does NOT destroy the QThread yet —
        that happens only in _on_thread_really_finished after the OS thread exits.
        """
        if worker is None:
            return
        cid = getattr(worker, "chat_id", None)
        if cid and self._workers_by_chat.get(cid) is worker:
            del self._workers_by_chat[cid]
        if self.worker is worker:
            self.worker = None
        if self._active_generation_id == getattr(worker, "generation_id", None):
            self._active_generation_id = None
            self._active_chat_id = None
        # Cap cancelled set size
        if len(self._cancelled_generations) > 100:
            self._cancelled_generations = set(list(self._cancelled_generations)[-50:])

    def _on_thread_really_finished(self, worker):
        """QThread.finished — OS thread is done; safe to drop the last strong ref."""
        try:
            self._live_workers.discard(worker)
        except Exception:
            pass
        # Remove from load-workers list if present
        try:
            if worker in self._load_workers:
                self._load_workers.remove(worker)
        except Exception:
            pass
        if self.test_worker is worker:
            self.test_worker = None
        # Also ensure chat map is clear if signal order was unusual
        try:
            self._cleanup_worker(worker)
        except Exception:
            pass
        try:
            worker.deleteLater()
        except Exception:
            pass

    def closeEvent(self, event):
        # Stop every live worker (including cancelled ones still winding down)
        for w in list(self._live_workers):
            try:
                if hasattr(w, "stop"):
                    self._cancelled_generations.add(getattr(w, "generation_id", ""))
                    w.stop()
                else:
                    # TestWorker / FileLoadWorker have no stop(); just request quit
                    w.quit()
            except Exception:
                pass
        for w in list(self._live_workers):
            try:
                if w.isRunning():
                    w.wait(2000)
            except Exception:
                pass
        self._live_workers.clear()
        self._workers_by_chat.clear()
        self._load_workers.clear()
        self.worker = None
        self.test_worker = None
        self._stream_timer.stop()
        super().closeEvent(event)



def main():
    app = QApplication(sys.argv)
    app.setApplicationName("GLM Chat Improved V 1.0 • Agh4Saeed")
    app.setFont(QFont("Segoe UI", 10))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()