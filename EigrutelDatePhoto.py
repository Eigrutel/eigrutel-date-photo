# -*- coding: utf-8 -*-
# Eigrutel Lab — Atelier d'outils libres pour la bande dessinée
# Programme conçu et développé par Simon Léturgie dans le cadre d'Eigrutel BD Academy.
# Nom : Date Photo | Version : 1.0.0 | Date : 18-09-2026
# Code : GNU AGPL v3.0 ou version ultérieure.
# Documentation et modèles : CC BY-SA 4.0, sauf mention contraire.
# Marques, logos et signes distinctifs Eigrutel / Eigrutel Lab /
# Eigrutel BD Academy : réservés.
"""Date Photo: local EXIF-based renaming and chronological filing.

Python >= 3.10, Pillow required; pillow-heif optional for HEIC/HEIF.
Standalone: no ui_common module is required. No network calls.
File planning and execution are separated from Tk. Worker threads never call Tk.
"""
from __future__ import annotations

import errno
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image

try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
    HEIF_AVAILABLE = True
except ImportError:
    HEIF_AVAILABLE = False

APP_TITLE = "Date Photo"
VERSION = "1.0.0"
VALID_MIN_DATE = date(1990, 1, 1)
SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}
if HEIF_AVAILABLE:
    SUPPORTED_EXTS |= {".heic", ".heif"}
DATE_PREFIX_RE = re.compile(r"^\d{4}_\d{2}_\d{2}_")

# All user-facing prose is paired; filesystem names stay stable across languages.
TEXT = {
    "subtitle": ("Dater et classer les photos à partir de leurs métadonnées", "Date and organize photos using their metadata"),
    "datewarning": ("Date EXIF erronée = date erronée dans le résultat. Le programme ne peut pas vérifier la date réelle de prise de vue.", "Incorrect EXIF date = incorrect date in the result. The application cannot verify the actual capture date."),
    "source": ("Dossier source", "Source folder"),
    "choose": ("Choisir…", "Browse…"),
    "sub": ("Inclure les sous-dossiers", "Include subfolders"),
    "target": ("Dossier parent de destination (classement)", "Destination parent folder (filing)"),
    "hint": ('Classement : photos_annees / année / année_mois. Les fichiers sont déplacés.', 'Filing: photos_annees / year / year_month. Files are moved.'),
    "stay": ("Les fichiers restent dans leur dossier actuel.", "Files stay in their current folders."),
    "mode": ("Traitement", "Operation"),
    "prefix_only": ("Préfixer sans classer", "Add date prefix only"),
    "classer": ("Préfixer et classer", "Add date prefix and organize"),
    "analyze": ("Analyser / Actualiser", "Analyze / Refresh"),
    "apply": ("Appliquer", "Apply"),
    "stop": ("Arrêter", "Stop"),
    "open": ("Ouvrir le dossier", "Open folder"),
    "ready": ("Choisissez un dossier, puis analysez avant d’appliquer.", "Choose a folder, then analyze before applying."),
    "changed": ("Réglages modifiés : relancez l’analyse.", "Settings changed: analyze again."),
    "scan": ("Analyse en cours… {n} fichiers", "Analyzing… {n} files"),
    "running": ("Traitement… {n}/{total}", "Processing… {n}/{total}"),
    "summary": ("{total} fichiers · {dated} datés · {planned} à traiter · {errors} erreurs", "{total} files · {dated} dated · {planned} to process · {errors} errors"),
    "done": ("{n} fichiers traités · {errors} erreurs. Relancez l’analyse avant un nouveau traitement.", "{n} files processed · {errors} errors. Analyze again before processing."),
    "stopped": ("Arrêt demandé : l’opération du fichier en cours se termine.", "Stop requested: the current file operation will finish."),
    "cancelled": ("Analyse interrompue. Aucun fichier modifié. Relancez l’analyse.", "Analysis stopped. No files changed. Analyze again."),
    "invalid": ("Choisissez un dossier source existant.", "Choose an existing source folder."),
    "missing": ("Ce dossier n’existe pas encore.", "This folder does not exist yet."),
    "confirm": ("Appliquer les {n} opérations affichées ?\n\n{mode}\n\nLe contenu des images et les métadonnées ne sont pas modifiés. Il n’y a pas d’annulation automatique.", "Apply the {n} displayed operations?\n\n{mode}\n\nImage content and metadata are not modified. There is no automatic undo."),
    "error": ("Erreur", "Error"),
    "closebusy": ("Un traitement est en cours. Utilisez Arrêter, puis attendez sa fin avant de fermer.", "An operation is running. Use Stop and wait for it to finish before closing."),
    "manual": ("Manuel et informations", "Manual and information"),
    "close": ("Fermer", "Close"),
    "file": ("Fichier source", "Source file"),
    "dest": ("Destination prévue", "Planned destination"),
    "status": ("État", "Status"),
    "planned": ("À traiter", "Planned"),
    "unchanged": ("Déjà préfixé — inchangé", "Already prefixed — unchanged"),
    "undated": ("Sans date valide — inchangé", "No valid date — unchanged"),
    "failed": ("Lecture impossible", "Cannot read file"),
    "moved": ("Traité", "Processed"),
    "execerror": ("Erreur de traitement", "Processing error"),
    "changedfile": ("Le fichier a changé depuis l’analyse ; analysez à nouveau.", "File changed since analysis; analyze again."),
    "heif": ("HEIC/HEIF : disponibles", "HEIC/HEIF: available"),
    "noheif": ("HEIC/HEIF : installer pillow-heif pour les activer", "HEIC/HEIF: install pillow-heif to enable"),
}

MANUAL = (
"""DATE PHOTO — MANUEL

1. Principe
Date Photo ajoute un préfixe AAAA_MM_JJ_ au nom des photos :
IMG_4587.jpg → 2023_09_23_IMG_4587.jpg.
L’application travaille localement, sans compte ni transmission de données.

2. Date utilisée
Priorité : DateTimeOriginal (prise de vue), puis DateTimeDigitized
(numérisation), puis DateTime (modification EXIF). La première date valide
est retenue, y compris dans le sous-répertoire EXIF. Une date valide se situe
entre le 1er janvier 1990 et aujourd’hui inclus. Les dates du système de
fichiers ne sont jamais utilisées. Les photos sans date valide restent en place.
La date EXIF de modification n’est pas nécessairement la date de prise de vue.
ATTENTION : si les métadonnées indiquent une date erronée mais valide, le
préfixe et les dossiers de classement reprendront cette date erronée.
Le programme ne peut pas vérifier la date réelle de prise de vue.

3. Deux modes
Préfixer sans classer (par défaut) : renomme dans le dossier actuel.
Préfixer et classer : déplace vers le dossier parent choisi, dans
photos_annees / AAAA / AAAA_MM / AAAA_MM_JJ_nom.ext.
Un préfixe AAAA_MM_JJ_ déjà présent est conservé, sans vérifier sa concordance
avec les métadonnées. En mode préfixage seul, le fichier reste inchangé.

4. Marche à suivre
Choisissez la source et l’option sous-dossiers. Choisissez le mode et, pour
le classement, la destination. Cliquez sur Analyser et consultez le tableau.
Appliquer demande confirmation. Modifier les réglages invalide l’analyse.
Un suffixe _001, _002… distingue les noms en conflit dès l’aperçu.
Si la destination devient occupée après l’analyse, le fichier est laissé
en place et une erreur est affichée : aucun fichier existant n’est écrasé.

5. Arrêt et erreurs
Échap ou Arrêter interrompt après le fichier en cours. Les opérations déjà
réalisées restent effectuées. Les erreurs apparaissent dans le tableau ;
le traitement continue pour les autres fichiers. Il n’y a pas d’annulation
automatique : gardez une sauvegarde avant un classement important.
Le contenu des images est copié à l’identique, sans réencodage.
Les liens symboliques et les dossiers de destination sont exclus du parcours.

6. Formats et dépendances
JPEG, PNG, WebP, TIFF avec Pillow. HEIC/HEIF avec pillow-heif, facultatif.
Un format accepté ne garantit pas la présence d’une date EXIF.
Installation : py -m pip install Pillow
HEIC/HEIF : py -m pip install pillow-heif
Lancement : py EigrutelDatePhoto.py
F1 : manuel. Échap : arrêter. Double-clic sur une ligne : ouvrir son dossier.
FR/EN change l’interface et le manuel ; les noms des dossiers restent identiques.

7. Eigrutel Lab
Programme conçu et développé par Simon Léturgie dans le cadre d’Eigrutel BD Academy.
Version 1.0.0 — 18-09-2026
Code : GNU AGPL v3.0 ou version ultérieure.
Documentation et modèles : CC BY-SA 4.0, sauf mention contraire.
Marques, logos et signes distinctifs Eigrutel / Eigrutel Lab /
Eigrutel BD Academy : réservés.
""",
"""DATE PHOTO — MANUAL

1. Purpose
Date Photo adds a YYYY_MM_DD_ prefix to photo filenames:
IMG_4587.jpg → 2023_09_23_IMG_4587.jpg.
The application works locally, without accounts or data transmission.

2. Date selection
Priority: DateTimeOriginal (capture), then DateTimeDigitized (digitization),
then DateTime (EXIF modification). The first valid date is used, including
values in the EXIF subdirectory. Valid dates range from January 1, 1990,
through today. Filesystem timestamps are never used. Photos without a valid
date are left in place. The EXIF modification date is not necessarily the
capture date.
WARNING: if metadata contains an incorrect but valid date, the filename prefix
and filing folders will use that incorrect date. The application cannot
verify the actual capture date.

3. Two modes
Add date prefix only (default): rename within the current folder.
Add date prefix and organize: move into the selected parent folder, under
photos_annees / YYYY / YYYY_MM / YYYY_MM_DD_name.ext.
An existing YYYY_MM_DD_ prefix is preserved without checking it against
metadata. In prefix-only mode, such files remain unchanged.

4. Workflow
Select a source and choose whether to include subfolders. Select the mode
and, for filing, a destination. Click Analyze and review the table.
Apply asks for confirmation. Changing settings invalidates the analysis.
A _001, _002… suffix resolves filename conflicts in the preview.
If a destination becomes occupied after analysis, the file stays in place
and an error is shown: existing files are never overwritten.

5. Stopping and errors
Escape or Stop stops after the current file. Completed operations remain
in effect. Errors appear in the table; other files continue processing.
There is no automatic undo: keep a backup before reorganizing many files.
Image content is copied unchanged, without re-encoding.
Symbolic links and destination folders are excluded from traversal.

6. Formats and dependencies
JPEG, PNG, WebP, TIFF through Pillow. HEIC/HEIF through optional pillow-heif.
A supported format does not guarantee that an EXIF date is present.
Install: py -m pip install Pillow
HEIC/HEIF: py -m pip install pillow-heif
Launch: py EigrutelDatePhoto.py
F1: manual. Escape: stop. Double-click a row: open its folder.
FR/EN changes the interface and manual; folder names stay identical.

7. Eigrutel Lab
Designed and developed by Simon Léturgie as part of Eigrutel BD Academy.
Version 1.0.0 — 2026-09-18
Code: GNU AGPL v3.0 or later.
Documentation and templates: CC BY-SA 4.0, unless otherwise specified.
Eigrutel / Eigrutel Lab / Eigrutel BD Academy trademarks, logos and
distinctive signs: reserved.
""")


def normalize_exif_datetime(value):
    """Decode EXIF ASCII dates, including null-padded byte strings."""
    if isinstance(value, bytes):
        value = value.decode("ascii", errors="replace")
    value = str(value or "").strip("\x00 \t\r\n")
    for fmt in ("%Y:%m:%d %H:%M:%S", "%Y:%m:%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def is_valid_date(dt):
    return dt is not None and VALID_MIN_DATE <= dt.date() <= date.today()


def read_exif_datetime(path):
    """Raise decoding/I/O errors so unreadable files are not reported as undated."""
    with Image.open(path) as img:
        exif = img.getexif()
        try:
            nested = exif.get_ifd(34665) if 34665 in exif else {}
        except (KeyError, ValueError, TypeError, OSError):
            nested = {}
        for tag in (36867, 36868, 306):
            for mapping in (nested, exif):
                dt = normalize_exif_datetime(mapping.get(tag))
                if is_valid_date(dt):
                    return dt
    return None


def add_prefix(name, dt):
    return name if DATE_PREFIX_RE.match(name) else dt.strftime("%Y_%m_%d_") + name


def path_key(path):
    # Conservative case-insensitive collision handling, also when tested on Linux.
    return str(Path(path).absolute()).casefold()


def signature(path):
    stat = path.stat()
    return stat.st_size, stat.st_mtime_ns


@dataclass
class Plan:
    src: Path
    dest: Path | None
    status: str
    fingerprint: tuple[int, int] | None = None
    detail: str = ""


class Planner:
    def __init__(self, source, include_subdirs=True, custom_target=None):
        self.source = Path(source).expanduser().resolve()
        self.include_subdirs = include_subdirs
        self.target = (Path(custom_target).expanduser().resolve() if custom_target else self.default_parent(self.source)) / "photos_annees"

    @staticmethod
    def default_parent(source):
        if source.drive.upper() == "C:":
            return Path.home() / "Documents"
        if source.drive:
            return Path(source.anchor)
        return source

    def files(self):
        def walk_error(error):
            raise error
        for folder, dirs, names in os.walk(self.source, onerror=walk_error, followlinks=False):
            parent = Path(folder)
            dirs[:] = sorted(d for d in dirs if not (parent / d).is_symlink()
                             and (parent / d).resolve() != self.target.resolve())
            for name in sorted(names):
                p = parent / name
                if p.suffix.lower() in SUPPORTED_EXTS and not p.is_symlink() and p.is_file():
                    yield p
            if not self.include_subdirs:
                break

    def scan(self, mode="prefix_only", progress=None, cancel=None):
        if mode not in ("prefix_only", "classer"):
            raise ValueError(mode)
        if not self.source.is_dir():
            raise FileNotFoundError(self.source)
        if mode == "classer" and (self.source == self.target or self.target in self.source.parents):
            raise ValueError("Source = photos_annees (destination)")
        rows, reserved, directories = [], set(), {}
        dated = 0
        for f in self.files():
            if cancel and cancel.is_set():
                break
            try:
                fingerprint = signature(f)
                dt = read_exif_datetime(f)
                if not dt:
                    row = Plan(f, None, "undated")
                else:
                    dated += 1
                    name = add_prefix(f.name, dt)
                    dest = f.with_name(name) if mode == "prefix_only" else self.target / dt.strftime("%Y") / dt.strftime("%Y_%m") / name
                    if path_key(f) == path_key(dest):
                        row = Plan(f, dest, "unchanged", fingerprint)
                    else:
                        parent = dest.parent
                        if parent not in directories:
                            directories[parent] = {p.name.casefold() for p in parent.iterdir()} if parent.exists() else set()
                        original, count = dest, 0
                        while dest.name.casefold() in directories[parent] or path_key(dest) in reserved:
                            count += 1
                            dest = original.with_name(f"{original.stem}_{count:03d}{original.suffix}")
                        reserved.add(path_key(dest))
                        row = Plan(f, dest, "planned", fingerprint)
            except (OSError, ValueError, SyntaxError) as exc:
                row = Plan(f, None, "failed", detail=str(exc))
            rows.append(row)
            if progress and len(rows) % 25 == 0:
                progress(len(rows))
        return rows, len(rows), dated

    def execute(self, plans, progress=None, cancel=None):
        """Never overwrite. Cross-device copies are exclusive and flushed before unlink."""
        done = 0
        actionable = [p for p in plans if p.status == "planned"]
        for i, p in enumerate(actionable, 1):
            if cancel and cancel.is_set():
                break
            try:
                if p.src.is_symlink() or signature(p.src) != p.fingerprint:
                    raise ValueError("changedfile")
                safe_move(p.src, p.dest)
                p.status = "moved"
                done += 1
            except (OSError, ValueError) as exc:
                p.status, p.detail = "execerror", str(exc)
            if progress:
                progress(i, len(actionable))
        return done


def safe_move(src, dest):
    """Create destination exclusively; never call shutil.move (may overwrite)."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        try:
            os.rename(src, dest)  # Windows rename refuses existing destinations.
            return
        except OSError as exc:
            if exc.errno != errno.EXDEV and getattr(exc, "winerror", None) != 17:
                raise
    else:
        try:
            os.link(src, dest)
        except OSError as exc:
            if exc.errno not in (errno.EXDEV, errno.EPERM, errno.EOPNOTSUPP):
                raise
        else:
            src.unlink()
            return
    # Cross-volume move: source remains intact if copying fails.
    created = False
    try:
        with src.open("rb") as reader, dest.open("xb") as writer:
            created = True
            shutil.copyfileobj(reader, writer, 1024 * 1024)
            writer.flush()
            os.fsync(writer.fileno())
        shutil.copystat(src, dest)
    except Exception:
        if created:
            dest.unlink(missing_ok=True)
        raise
    src.unlink()


def open_folder(path):
    if not path.is_dir():
        raise FileNotFoundError(path)
    if sys.platform == "win32":
        os.startfile(str(path))
    else:
        subprocess.Popen(["open" if sys.platform == "darwin" else "xdg-open", str(path)])


def apply_icon(root):
    """Use existing supplied icons, including PyInstaller's resource directory."""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    for name in ("favdate",):
        try:
            if (base / (name + ".png")).is_file():
                icon = tk.PhotoImage(file=str(base / (name + ".png")))
                root.iconphoto(True, icon)
                root._icon = icon
            if sys.platform == "win32" and (base / (name + ".ico")).is_file():
                root.iconbitmap(str(base / (name + ".ico")))
        except tk.TclError:
            continue
        if hasattr(root, "_icon"):
            break


class App:
    def __init__(self, root):
        self.root, self.lang = root, 0
        self.busy = False
        self.rows = []
        self.total = self.dated = 0
        self.analyzed = False
        self.events = queue.Queue()
        self.cancel = threading.Event()
        self.source, self.target = tk.StringVar(), tk.StringVar()
        self.sub, self.mode = tk.BooleanVar(value=True), tk.StringVar(value="prefix_only")
        self.status_key, self.status_values = "ready", {}
        self.labels, self.controls = [], []
        root.title(APP_TITLE)
        root.geometry("1040x740")
        root.minsize(780, 600)
        self.style()
        apply_icon(root)
        self.build()
        for var in (self.source, self.target, self.sub, self.mode):
            var.trace_add("write", self.invalidate)
        root.bind("<Escape>", lambda e: self.stop())
        root.bind("<F1>", lambda e: self.manual())
        root.protocol("WM_DELETE_WINDOW", self.close)
        self.refresh()
        root.after(100, self.poll)

    def t(self, key, **values):
        return TEXT[key][self.lang].format(**values)

    def style(self):
        s = ttk.Style(self.root)
        s.theme_use("clam")
        self.root.configure(bg="#F4F5F7")
        s.configure(".", font=("Segoe UI", 10), background="#F4F5F7", foreground="#1F232B")
        s.configure("TButton", padding=(12, 8))
        for name, color in (("Dark", "#1F3A44"), ("Red", "#7F2D30"), ("Ochre", "#C47A2C")):
            s.configure(name + ".TButton", background=color, foreground="white", borderwidth=0)
            s.map(name + ".TButton", background=[("disabled", "#D7DCE3"), ("active", color)], foreground=[("disabled", "#69737D"), ("!disabled", "white")])
        s.configure("Top.TFrame", background="#1F3A44")
        s.configure("Top.TLabel", background="#1F3A44", foreground="white")
        s.configure("Title.TLabel", background="#1F3A44", foreground="white", font=("Segoe UI", 16, "bold"))
        s.configure("TLabelframe.Label", font=("Segoe UI", 10, "bold"))
        s.configure("Treeview", background="white", fieldbackground="white", rowheight=29)
        s.configure("Treeview.Heading", background="#1F3A44", foreground="white", padding=7)
        s.map("Treeview.Heading", background=[("active", "#1F3A44")])

    def label(self, widget, key):
        self.labels.append((widget, key))
        return widget

    def button(self, parent, key, command, style="Dark.TButton"):
        b = self.label(ttk.Button(parent, command=command, style=style), key)
        self.controls.append(b)
        return b

    def build(self):
        top = ttk.Frame(self.root, style="Top.TFrame", padding=14)
        top.pack(fill="x")
        ttk.Label(top, text="DATE PHOTO", style="Title.TLabel").pack(anchor="w")
        self.label(ttk.Label(top, style="Top.TLabel"), "subtitle").pack(side="left", pady=(6, 0))
        self.language = ttk.Button(top, text="FR / EN", command=self.toggle, style="Dark.TButton")
        self.language.pack(side="right")
        ttk.Button(top, text="i", width=3, command=self.manual, style="Ochre.TButton").pack(side="right", padx=8)
        main = ttk.Frame(self.root, padding=14)
        main.pack(fill="both", expand=True)
        for key, var, chooser in (("source", self.source, self.choose_source), ("target", self.target, self.choose_target)):
            box = self.label(ttk.LabelFrame(main, padding=9), key)
            box.pack(fill="x", pady=(0, 8))
            entry = ttk.Entry(box, textvariable=var)
            entry.pack(side="left", fill="x", expand=True)
            self.controls.append(entry)
            btn = self.button(box, "choose", chooser, "Red.TButton")
            btn.pack(side="left", padx=(8, 0))
            if key == "target":
                self.target_entry, self.target_btn = entry, btn
        options = ttk.Frame(main)
        options.pack(fill="x")
        sub = self.label(ttk.Checkbutton(options, variable=self.sub), "sub")
        sub.pack(side="left")
        self.controls.append(sub)
        for mode in ("prefix_only", "classer"):
            radio = self.label(ttk.Radiobutton(options, variable=self.mode, value=mode), mode)
            radio.pack(side="left", padx=(16, 0))
            self.controls.append(radio)
        self.label(ttk.Label(main, wraplength=900, foreground="#7F2D30"), "datewarning").pack(anchor="w", pady=(8, 0))
        self.hint = ttk.Label(main, wraplength=900)
        self.hint.pack(anchor="w", pady=8)
        actions = ttk.Frame(main)
        actions.pack(fill="x", pady=(0, 10))
        self.button(actions, "analyze", self.analyze, "Red.TButton").pack(side="left")
        self.apply_btn = self.button(actions, "apply", self.run, "Red.TButton")
        self.apply_btn.pack(side="left", padx=8)
        self.button(actions, "open", self.open).pack(side="left")
        self.stop_btn = self.label(ttk.Button(actions, command=self.stop), "stop")
        self.stop_btn.pack(side="right")
        panel = ttk.Frame(main)
        panel.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(panel, columns=("file", "dest", "status"), show="headings")
        for key, width in (("file", 260), ("dest", 400), ("status", 200)):
            self.tree.column(key, width=width, minwidth=100)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vs = ttk.Scrollbar(panel, command=self.tree.yview)
        vs.grid(row=0, column=1, sticky="ns")
        hs = ttk.Scrollbar(panel, orient="horizontal", command=self.tree.xview)
        hs.grid(row=1, column=0, sticky="ew")
        self.tree.configure(yscrollcommand=vs.set, xscrollcommand=hs.set)
        panel.rowconfigure(0, weight=1)
        panel.columnconfigure(0, weight=1)
        self.tree.bind("<<TreeviewSelect>>", self.selection)
        self.tree.bind("<Double-1>", self.open_row)
        self.detail = tk.StringVar()
        ttk.Label(main, textvariable=self.detail, wraplength=940).pack(anchor="w", pady=5)
        self.progress = ttk.Progressbar(main, mode="indeterminate")
        self.progress.pack(fill="x")
        self.status = ttk.Label(main, wraplength=940)
        self.status.pack(anchor="w", pady=7)
        self.footer = ttk.Label(main)
        self.footer.pack(anchor="w")

    def set_status(self, key, **values):
        self.status_key, self.status_values = key, values
        self.status.configure(text=self.t(key, **values))

    def refresh(self):
        for widget, key in self.labels:
            widget.configure(text=self.t(key))
        for key in ("file", "dest", "status"):
            self.tree.heading(key, text=self.t(key))
        self.hint.configure(text=self.t("stay" if self.mode.get() == "prefix_only" else "hint"))
        self.footer.configure(text=f"Eigrutel Lab · {VERSION} · " + self.t("heif" if HEIF_AVAILABLE else "noheif"))
        self.set_status(self.status_key, **self.status_values)
        for widget in self.controls:
            widget.state(["disabled" if self.busy else "!disabled"])
        if self.mode.get() == "prefix_only":
            self.target_entry.state(["disabled"])
            self.target_btn.state(["disabled"])
        self.apply_btn.state(["!disabled" if not self.busy and self.analyzed and any(p.status == "planned" for p in self.rows) else "disabled"])
        self.stop_btn.state(["!disabled" if self.busy else "disabled"])
        self.language.state(["disabled" if self.busy else "!disabled"])

    def toggle(self):
        self.lang = 1 - self.lang
        self.refresh()
        self.render_rows()

    def invalidate(self, *_):
        self.analyzed = False
        self.rows = []
        self.tree.delete(*self.tree.get_children())
        self.detail.set("")
        self.set_status("changed")
        self.refresh()

    def choose_source(self):
        p = filedialog.askdirectory(parent=self.root, title=self.t("source"))
        if p:
            self.source.set(p)
            if not self.target.get():
                self.target.set(str(Planner.default_parent(Path(p))))

    def choose_target(self):
        p = filedialog.askdirectory(parent=self.root, title=self.t("target"))
        if p:
            self.target.set(p)

    def analyze(self):
        source = self.source.get().strip()
        if not source or not Path(source).is_dir():
            messagebox.showwarning(APP_TITLE, self.t("invalid"), parent=self.root)
            return
        self.rows = []
        self.analyzed = False
        self.render_rows()
        self.planner = Planner(source, self.sub.get(), self.target.get().strip() or None)
        mode = self.mode.get()
        def job():
            result = self.planner.scan(mode, lambda n: self.events.put(("scanprogress", n)), self.cancel)
            self.events.put(("scanned", result))
        self.start(job)
        self.set_status("scan", n=0)

    def run(self):
        if not self.analyzed or self.busy:
            return
        n = sum(p.status == "planned" for p in self.rows)
        if not messagebox.askyesno(APP_TITLE, self.t("confirm", n=n, mode=self.t(self.mode.get())), parent=self.root):
            return
        self.analyzed = False
        def job():
            n = self.planner.execute(self.rows, lambda i, total: self.events.put(("runprogress", (i, total))), self.cancel)
            self.events.put(("finished", n))
        self.start(job)

    def start(self, job):
        self.busy = True
        self.cancel.clear()
        self.refresh()
        self.progress.start(12)
        def worker():
            try:
                job()
            except Exception as exc:
                self.events.put(("error", str(exc)))
        threading.Thread(target=worker, daemon=True).start()

    def poll(self):
        for _ in range(150):
            try:
                kind, data = self.events.get_nowait()
            except queue.Empty:
                break
            if kind == "scanprogress":
                self.set_status("scan", n=data)
            elif kind == "runprogress":
                self.set_status("running", n=data[0], total=data[1])
            else:
                self.busy = False
                self.progress.stop()
                if kind == "scanned":
                    self.rows, self.total, self.dated = data
                    self.analyzed = not self.cancel.is_set()
                    if self.analyzed:
                        self.set_status("summary", total=self.total, dated=self.dated,
                                        planned=sum(p.status == "planned" for p in self.rows),
                                        errors=sum(p.status == "failed" for p in self.rows))
                    else:
                        self.rows = []
                        self.set_status("cancelled")
                elif kind == "finished":
                    self.set_status("done", n=data, errors=sum(p.status == "execerror" for p in self.rows))
                elif kind == "error":
                    self.analyzed = False
                    self.set_status("error")
                    messagebox.showerror(APP_TITLE, data, parent=self.root)
                self.render_rows()
                self.refresh()
        self.root.after(100, self.poll)

    def render_rows(self):
        self.tree.delete(*self.tree.get_children())
        for i, row in enumerate(self.rows):
            self.tree.insert("", "end", iid=str(i), values=(str(row.src), str(row.dest or ""), self.t(row.status)))
        self.detail.set("")

    def selection(self, _=None):
        selected = self.tree.selection()
        if selected:
            row = self.rows[int(selected[0])]
            detail = self.t("changedfile") if row.detail == "changedfile" else row.detail
            self.detail.set(detail or str(row.dest or row.src))

    def stop(self):
        if self.busy:
            self.cancel.set()
            self.set_status("stopped")

    def open(self):
        source = self.source.get().strip()
        if not source:
            return
        path = Path(source) if self.mode.get() == "prefix_only" else Planner(source, custom_target=self.target.get().strip() or None).target
        self.show_folder(path)

    def open_row(self, _=None):
        selected = self.tree.selection()
        if selected:
            row = self.rows[int(selected[0])]
            self.show_folder((row.dest if row.status == "moved" else row.src).parent)

    def show_folder(self, path):
        try:
            if not path.is_dir():
                messagebox.showinfo(APP_TITLE, self.t("missing"), parent=self.root)
                return
            open_folder(path)
        except OSError as exc:
            messagebox.showerror(APP_TITLE, str(exc), parent=self.root)

    def manual(self):
        dlg = tk.Toplevel(self.root)
        dlg.title(self.t("manual"))
        dlg.geometry("760x640")
        dlg.transient(self.root)
        apply_icon(dlg)
        frame = ttk.Frame(dlg, padding=14)
        frame.pack(fill="both", expand=True)
        text = tk.Text(frame, wrap="word", font=("Segoe UI", 11), padx=14, pady=14, relief="flat")
        scroll = ttk.Scrollbar(frame, command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        text.pack(fill="both", expand=True)
        text.insert("1.0", MANUAL[self.lang])
        text.configure(state="disabled")
        ttk.Button(dlg, text=self.t("close"), command=dlg.destroy).pack(pady=8)
        dlg.bind("<Escape>", lambda e: dlg.destroy())

    def close(self):
        if self.busy:
            messagebox.showinfo(APP_TITLE, self.t("closebusy"), parent=self.root)
        else:
            self.root.destroy()


def main():
    if sys.platform == "win32":
        import ctypes
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("EigrutelLab.DatePhoto.1")
        except (AttributeError, OSError):
            pass
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
