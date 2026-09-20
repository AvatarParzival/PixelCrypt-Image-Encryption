"""PixelCrypt Image Encryption desktop application."""

from __future__ import annotations

import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk

from pixel_cipher import process_image


APP_NAME = "PixelCrypt Image Encryption"
SUPPORTED_IMAGES = [
    ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.tif *.tiff *.webp"),
    ("All files", "*.*"),
]


class PixelCryptApp:
    """Tkinter interface for reversible pixel encryption and decryption."""

    BG = "#111827"
    PANEL = "#1F2937"
    SURFACE = "#273449"
    BORDER = "#40506A"
    TEXT = "#F9FAFB"
    MUTED = "#AEB9C9"
    ACCENT = "#5E9FE8"
    ACCENT_HOVER = "#78B0ED"
    SUCCESS = "#72BC8F"
    WARNING = "#EAC26B"

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("980x650")
        self.root.minsize(820, 580)
        self.root.configure(bg=self.BG)

        self.input_path = tk.StringVar()
        self.key_var = tk.StringVar()
        self.show_key = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value="Select an image to begin")
        self.preview_photo: ImageTk.PhotoImage | None = None

        self._configure_styles()
        self._build_interface()

    def _configure_styles(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("App.TFrame", background=self.BG)
        style.configure("Panel.TFrame", background=self.PANEL)
        style.configure(
            "Accent.TButton",
            background=self.ACCENT,
            foreground="white",
            borderwidth=0,
            font=("Arial", 11, "bold"),
            padding=(18, 12),
        )
        style.map("Accent.TButton", background=[("active", self.ACCENT_HOVER)])
        style.configure(
            "Secondary.TButton",
            background=self.SURFACE,
            foreground=self.TEXT,
            bordercolor=self.BORDER,
            font=("Arial", 11, "bold"),
            padding=(18, 12),
        )
        style.map("Secondary.TButton", background=[("active", self.BORDER)])
        style.configure(
            "Input.TEntry",
            fieldbackground=self.SURFACE,
            foreground=self.TEXT,
            insertcolor=self.TEXT,
            bordercolor=self.BORDER,
            padding=10,
        )

    def _build_interface(self) -> None:
        shell = ttk.Frame(self.root, style="App.TFrame", padding=(40, 30))
        shell.pack(fill="both", expand=True)

        tk.Label(
            shell,
            text="PIXELCRYPT",
            bg=self.BG,
            fg=self.ACCENT,
            font=("Arial", 11, "bold"),
        ).pack(anchor="w")
        tk.Label(
            shell,
            text="Image Encryption",
            bg=self.BG,
            fg=self.TEXT,
            font=("Arial", 30, "bold"),
        ).pack(anchor="w", pady=(4, 4))
        tk.Label(
            shell,
            text="Apply a reversible, key-based transformation to image pixels.",
            bg=self.BG,
            fg=self.MUTED,
            font=("Arial", 11),
        ).pack(anchor="w", pady=(0, 24))

        body = ttk.Frame(shell, style="App.TFrame")
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=5)
        body.columnconfigure(1, weight=6)
        body.rowconfigure(0, weight=1)

        preview_panel = ttk.Frame(body, style="Panel.TFrame", padding=22)
        preview_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        tk.Label(
            preview_panel,
            text="IMAGE PREVIEW",
            bg=self.PANEL,
            fg=self.MUTED,
            font=("Arial", 10, "bold"),
        ).pack(anchor="w")

        self.preview_label = tk.Label(
            preview_panel,
            text="No image selected\n\nChoose a PNG, JPEG, BMP, GIF, TIFF, or WebP file.",
            bg=self.SURFACE,
            fg=self.MUTED,
            font=("Arial", 11),
            justify="center",
            relief="flat",
            highlightthickness=1,
            highlightbackground=self.BORDER,
        )
        self.preview_label.pack(fill="both", expand=True, pady=(14, 0))

        controls = ttk.Frame(body, style="Panel.TFrame", padding=24)
        controls.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

        self._label(controls, "Input image").pack(anchor="w")
        path_row = ttk.Frame(controls, style="Panel.TFrame")
        path_row.pack(fill="x", pady=(8, 20))
        self.path_entry = ttk.Entry(
            path_row,
            textvariable=self.input_path,
            state="readonly",
            style="Input.TEntry",
            font=("Arial", 10),
        )
        self.path_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(
            path_row,
            text="Browse",
            command=self._choose_image,
            style="Secondary.TButton",
        ).pack(side="left", padx=(10, 0))

        self._label(controls, "Encryption key").pack(anchor="w")
        key_row = ttk.Frame(controls, style="Panel.TFrame")
        key_row.pack(fill="x", pady=(8, 8))
        self.key_entry = ttk.Entry(
            key_row,
            textvariable=self.key_var,
            show="•",
            style="Input.TEntry",
            font=("Arial", 11),
        )
        self.key_entry.pack(side="left", fill="x", expand=True)
        ttk.Checkbutton(
            key_row,
            text="Show",
            variable=self.show_key,
            command=self._toggle_key,
        ).pack(side="left", padx=(12, 0))

        tk.Label(
            controls,
            text="Use exactly the same key to restore the image. Lost keys cannot be recovered.",
            bg=self.PANEL,
            fg=self.MUTED,
            justify="left",
            wraplength=410,
            font=("Arial", 10),
        ).pack(anchor="w", pady=(0, 24))

        actions = ttk.Frame(controls, style="Panel.TFrame")
        actions.pack(fill="x")
        self.encrypt_button = ttk.Button(
            actions,
            text="Encrypt image",
            command=lambda: self._start_operation("encrypted"),
            style="Accent.TButton",
        )
        self.encrypt_button.pack(side="left", fill="x", expand=True)
        self.decrypt_button = ttk.Button(
            actions,
            text="Decrypt image",
            command=lambda: self._start_operation("decrypted"),
            style="Secondary.TButton",
        )
        self.decrypt_button.pack(side="left", fill="x", expand=True, padx=(10, 0))

        notice = tk.Frame(
            controls,
            bg="#332E22",
            highlightthickness=1,
            highlightbackground="#6B5C32",
            padx=14,
            pady=12,
        )
        notice.pack(fill="x", pady=(24, 0))
        tk.Label(
            notice,
            text="Educational algorithm",
            bg="#332E22",
            fg=self.WARNING,
            font=("Arial", 10, "bold"),
        ).pack(anchor="w")
        tk.Label(
            notice,
            text="PixelCrypt demonstrates reversible XOR pixel manipulation. Do not use it as a replacement for audited file-encryption software.",
            bg="#332E22",
            fg=self.TEXT,
            justify="left",
            wraplength=400,
            font=("Arial", 10),
        ).pack(anchor="w", pady=(4, 0))

        self.progress = ttk.Progressbar(controls, mode="indeterminate")
        self.progress.pack(fill="x", pady=(26, 10))
        tk.Label(
            controls,
            textvariable=self.status_var,
            bg=self.PANEL,
            fg=self.SUCCESS,
            justify="left",
            font=("Arial", 10, "bold"),
        ).pack(anchor="w")

    def _label(self, parent: tk.Misc, text: str) -> tk.Label:
        return tk.Label(
            parent,
            text=text,
            bg=self.PANEL,
            fg=self.TEXT,
            font=("Arial", 11, "bold"),
        )

    def _toggle_key(self) -> None:
        self.key_entry.configure(show="" if self.show_key.get() else "•")

    def _choose_image(self) -> None:
        selected = filedialog.askopenfilename(title="Select an image", filetypes=SUPPORTED_IMAGES)
        if not selected:
            return
        self.input_path.set(selected)
        self._load_preview(selected)
        self.status_var.set(f"Selected: {Path(selected).name}")

    def _load_preview(self, path: str) -> None:
        try:
            with Image.open(path) as image:
                preview = image.convert("RGBA")
                preview.thumbnail((360, 420), Image.Resampling.LANCZOS)
                self.preview_photo = ImageTk.PhotoImage(preview)
            self.preview_label.configure(image=self.preview_photo, text="")
        except Exception as error:
            self.preview_photo = None
            self.preview_label.configure(image="", text="Preview unavailable")
            messagebox.showerror("Image error", f"The selected file could not be opened.\n\n{error}")

    def _start_operation(self, suffix: str) -> None:
        source_text = self.input_path.get().strip()
        key = self.key_var.get()

        if not source_text:
            messagebox.showinfo("Image required", "Select an image before continuing.")
            return
        if not key:
            messagebox.showinfo("Key required", "Enter a key before continuing.")
            self.key_entry.focus_set()
            return

        source = Path(source_text)
        default_name = f"{source.stem}_{suffix}.png"
        destination = filedialog.asksaveasfilename(
            title=f"Save {suffix} image",
            defaultextension=".png",
            initialfile=default_name,
            filetypes=[("PNG image", "*.png")],
        )
        if not destination:
            return

        self._set_busy(True)
        self.status_var.set(f"Creating {suffix} image…")
        worker = threading.Thread(
            target=self._run_operation,
            args=(source, Path(destination), key, suffix),
            daemon=True,
        )
        worker.start()

    def _run_operation(self, source: Path, destination: Path, key: str, suffix: str) -> None:
        try:
            process_image(source, destination, key)
        except Exception as error:
            self.root.after(0, self._operation_failed, str(error))
        else:
            self.root.after(0, self._operation_complete, destination, suffix)

    def _set_busy(self, busy: bool) -> None:
        state = "disabled" if busy else "normal"
        self.encrypt_button.configure(state=state)
        self.decrypt_button.configure(state=state)
        if busy:
            self.progress.start(10)
        else:
            self.progress.stop()

    def _operation_complete(self, destination: Path, suffix: str) -> None:
        self._set_busy(False)
        self.status_var.set(f"Saved: {destination.name}")
        messagebox.showinfo(
            "Operation complete",
            f"The {suffix} image was saved successfully.\n\n{destination}",
        )

    def _operation_failed(self, error: str) -> None:
        self._set_busy(False)
        self.status_var.set("Operation failed")
        messagebox.showerror("Operation failed", error)


def main() -> None:
    root = tk.Tk()
    PixelCryptApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
