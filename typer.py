from __future__ import annotations

import ctypes
import queue
import sys
import threading
import time
from ctypes import wintypes
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk


if ctypes.sizeof(ctypes.c_void_p) == 8:
    ULONG_PTR = ctypes.c_ulonglong
else:
    ULONG_PTR = ctypes.c_ulong


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.c_ushort),
        ("wScan", ctypes.c_ushort),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ULONG_PTR),
    ]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ULONG_PTR),
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", ctypes.c_ulong),
        ("wParamL", ctypes.c_ushort),
        ("wParamH", ctypes.c_ushort),
    ]


class INPUT_UNION(ctypes.Union):
    # Размер INPUT определяется самым крупным вариантом union (MOUSEINPUT).
    # Если оставить только KEYBDINPUT, SendInput на 64-bit Windows вернёт ERROR_INVALID_PARAMETER (87).
    _fields_ = [
        ("mi", MOUSEINPUT),
        ("ki", KEYBDINPUT),
        ("hi", HARDWAREINPUT),
    ]


class INPUT(ctypes.Structure):
    _anonymous_ = ("union",)
    _fields_ = [("type", ctypes.c_ulong), ("union", INPUT_UNION)]


INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
VK_RETURN = 0x0D
VK_SHIFT = 0x10
VK_CONTROL = 0x11
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_NOREPEAT = 0x4000
WM_HOTKEY = 0x0312
HOTKEY_START = 1
HOTKEY_STOP = 2

user32 = ctypes.windll.user32


def _send_key(vk: int = 0, scan: int = 0, unicode_key: bool = False) -> None:
    flags = KEYEVENTF_UNICODE if unicode_key else 0
    key_down = (INPUT * 1)(INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(vk, scan, flags, 0, 0)))
    sent = user32.SendInput(1, key_down, ctypes.sizeof(INPUT))
    if sent != 1:
        raise ctypes.WinError()

    key_up = (INPUT * 1)(INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(vk, scan, flags | KEYEVENTF_KEYUP, 0, 0)))
    sent = user32.SendInput(1, key_up, ctypes.sizeof(INPUT))
    if sent != 1:
        error = ctypes.WinError()
        user32.SendInput(1, key_up, ctypes.sizeof(INPUT))
        raise error


def type_character(character: str) -> None:
    if character == "\n":
        _send_key(vk=VK_RETURN)
        return

    # SendInput принимает UTF-16 code units, поэтому это работает и для emoji.
    encoded = character.encode("utf-16-le", errors="surrogatepass")
    for index in range(0, len(encoded), 2):
        code_unit = int.from_bytes(encoded[index:index + 2], "little")
        _send_key(scan=code_unit, unicode_key=True)


class GlobalHotkeys(threading.Thread):
    def __init__(self, events: queue.Queue[str]) -> None:
        super().__init__(daemon=True)
        self.events = events
        self.thread_id = 0
        self.registered_hotkeys: list[int] = []

    def run(self) -> None:
        self.thread_id = ctypes.windll.kernel32.GetCurrentThreadId()
        hotkeys = (
            (HOTKEY_START, ord("C")),
            (HOTKEY_STOP, ord("X")),
        )
        for hotkey_id, key in hotkeys:
            if user32.RegisterHotKey(None, hotkey_id, MOD_CONTROL | MOD_SHIFT | MOD_NOREPEAT, key):
                self.registered_hotkeys.append(hotkey_id)
            else:
                error_code = ctypes.get_last_error()
                self.events.put(f"hotkey_error:{hotkey_id}:{error_code}")
                break

        if len(self.registered_hotkeys) != len(hotkeys):
            for hotkey_id in self.registered_hotkeys:
                user32.UnregisterHotKey(None, hotkey_id)
            self.registered_hotkeys.clear()
            return

        message = wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(message), None, 0, 0) > 0:
            if message.message == WM_HOTKEY:
                if message.wParam == HOTKEY_START:
                    self.events.put("start")
                elif message.wParam == HOTKEY_STOP:
                    self.events.put("stop")

        for hotkey_id in self.registered_hotkeys:
            user32.UnregisterHotKey(None, hotkey_id)
        self.registered_hotkeys.clear()

    def close(self) -> None:
        if self.thread_id:
            user32.PostThreadMessageW(self.thread_id, 0x0012, 0, 0)  # WM_QUIT


class TyperApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        icon_path = Path(getattr(sys, "_MEIPASS", Path(__file__).parent)) / "icon.png"
        if icon_path.is_file():
            try:
                self._window_icon = tk.PhotoImage(file=str(icon_path))
                self.root.iconphoto(True, self._window_icon)
            except tk.TclError:
                self._window_icon = None
        self.root.title("Typer — ввод текста по горячей клавише")
        self.root.geometry("650x440")
        self.root.minsize(560, 380)

        self.events: queue.Queue[str] = queue.Queue()
        self.hotkeys = GlobalHotkeys(self.events)
        self.stop_event = threading.Event()
        self.worker: threading.Thread | None = None
        self.text = ""
        self.file_path = tk.StringVar(value="Файл не выбран")
        self.delay_ms = tk.StringVar(value="15")
        self.status = tk.StringVar(value="Выберите текстовый файл")

        self._build_ui()
        self.hotkeys.start()
        self.root.after(60, self._process_events)
        self.root.protocol("WM_DELETE_WINDOW", self._close)

    def _build_ui(self) -> None:
        frame = ttk.Frame(self.root, padding=18)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Автоматический ввод текста", font=("Segoe UI", 16, "bold")).pack(anchor="w")
        ttk.Label(
            frame,
            text="Загрузите TXT, поставьте курсор в нужное поле и нажмите Ctrl+Shift+C.",
            wraplength=600,
        ).pack(anchor="w", pady=(5, 16))

        file_row = ttk.Frame(frame)
        file_row.pack(fill="x")
        ttk.Button(file_row, text="Выбрать TXT…", command=self._choose_file).pack(side="left")
        ttk.Label(file_row, textvariable=self.file_path).pack(side="left", padx=10, fill="x", expand=True)

        settings = ttk.Frame(frame)
        settings.pack(fill="x", pady=14)
        ttk.Label(settings, text="Задержка между символами, мс:").pack(side="left")
        ttk.Spinbox(settings, from_=0, to=1000, increment=1, width=7, textvariable=self.delay_ms).pack(side="left", padx=8)

        ttk.Label(frame, text="Предпросмотр:").pack(anchor="w")
        preview_frame = ttk.Frame(frame)
        preview_frame.pack(fill="both", expand=True, pady=(5, 12))
        self.preview = tk.Text(preview_frame, height=10, wrap="word", state="disabled", font=("Segoe UI", 10))
        scroll = ttk.Scrollbar(preview_frame, command=self.preview.yview)
        self.preview.configure(yscrollcommand=scroll.set)
        self.preview.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        ttk.Separator(frame).pack(fill="x", pady=(0, 10))
        ttk.Label(frame, textvariable=self.status, font=("Segoe UI", 10, "bold")).pack(anchor="w")
        ttk.Label(frame, text="Старт: Ctrl+Shift+C    Остановка: Ctrl+Shift+X").pack(anchor="w", pady=(4, 0))

    def _choose_file(self) -> None:
        selected = filedialog.askopenfilename(title="Выберите текстовый файл", filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")])
        if not selected:
            return

        path = Path(selected)
        try:
            data = path.read_bytes()
        except OSError as exc:
            messagebox.showerror("Ошибка чтения файла", f"Не удалось прочитать файл:\n{exc}")
            return
        for encoding in ("utf-8-sig", "utf-16", "cp1251"):
            try:
                self.text = data.decode(encoding).replace("\r\n", "\n").replace("\r", "\n")
                break
            except UnicodeDecodeError:
                continue
        else:
            messagebox.showerror("Ошибка", "Не удалось определить кодировку файла.")
            return

        self.file_path.set(str(path))
        self.preview.configure(state="normal")
        self.preview.delete("1.0", "end")
        self.preview.insert("1.0", self.text)
        self.preview.configure(state="disabled")
        self.status.set(f"Готово: {len(self.text)} символов. Перейдите в нужное поле.")

    def _process_events(self) -> None:
        try:
            while True:
                event = self.events.get_nowait()
                if event == "start":
                    self._start_typing()
                elif event == "stop":
                    self._stop_typing()
                elif event.startswith("hotkey_error:"):
                    _, hotkey_id, error_code = event.split(":", 2)
                    hotkey_name = "Ctrl+Shift+C" if hotkey_id == str(HOTKEY_START) else "Ctrl+Shift+X"
                    messagebox.showerror(
                        "Горячая клавиша занята",
                        f"Не удалось зарегистрировать {hotkey_name} (код Windows: {error_code}). "
                        "Закройте программу, которая использует это сочетание, и перезапустите Typer.",
                    )
                elif event.startswith("progress:"):
                    done, total = event.split(":", 1)[1].split("/")
                    self.status.set(f"Печать: {done} из {total} символов. Ctrl+Shift+X — остановить.")
                elif event == "finished":
                    self.status.set("Готово: текст напечатан полностью.")
                elif event == "stopped":
                    self.status.set("Печать остановлена.")
                elif event.startswith("error:"):
                    self.status.set("Ошибка при вводе.")
                    messagebox.showerror("Ошибка ввода", event.split(":", 1)[1])
        except queue.Empty:
            pass
        self.root.after(60, self._process_events)

    def _start_typing(self) -> None:
        if not self.text:
            self.status.set("Сначала выберите непустой текстовый файл.")
            return
        if self.worker and self.worker.is_alive():
            return
        try:
            delay = max(0.0, float(self.delay_ms.get().replace(",", ".")) / 1000.0)
        except ValueError:
            self.status.set("Укажите корректную задержку в миллисекундах.")
            return

        self.stop_event.clear()
        text_to_type = self.text
        self.worker = threading.Thread(target=self._type_text, args=(delay, text_to_type), daemon=True)
        self.worker.start()

    def _type_text(self, delay: float, text: str) -> None:
        try:
            # Не начинаем ввод, пока пользователь не отпустит клавиши хоткея.
            while user32.GetAsyncKeyState(VK_CONTROL) & 0x8000 or user32.GetAsyncKeyState(VK_SHIFT) & 0x8000:
                if self.stop_event.is_set():
                    self.events.put("stopped")
                    return
                time.sleep(0.01)

            total = len(text)
            for index, character in enumerate(text, start=1):
                if self.stop_event.is_set():
                    self.events.put("stopped")
                    return
                type_character(character)
                if index == 1 or index % 25 == 0:
                    self.events.put(f"progress:{index}/{total}")
                if delay:
                    time.sleep(delay)
            self.events.put("finished")
        except Exception as exc:
            self.events.put(f"error:{exc}")

    def _stop_typing(self) -> None:
        self.stop_event.set()

    def _close(self) -> None:
        self.stop_event.set()
        self.hotkeys.close()
        self.root.after(50, self._finish_close)

    def _finish_close(self) -> None:
        if self.worker and self.worker.is_alive():
            self.root.after(50, self._finish_close)
            return
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    try:
        ttk.Style(root).theme_use("vista")
    except tk.TclError:
        pass
    TyperApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
