"""Build on Windows; include existing icons and offline documentation."""
from pathlib import Path
import hashlib
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
NAME = "DatePhoto-1.0.0"

def main():
    if sys.platform != "win32":
        raise SystemExit("Construire sous Windows / Build on Windows.")
    for name in ("EigrutelDatePhoto.py", "favdate.ico", "favdate.png", "Manuel-DatePhoto.html", "LICENSE", "LICENSE-DOCS"):
        if not (ROOT / name).is_file():
            raise SystemExit("Fichier absent / Missing file: " + name)
    command = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean",
               "--onefile", "--windowed", "--noupx", "--name", NAME,
               "--icon", str(ROOT / "favdate.ico"),
               "--version-file", str(ROOT / "windows-version.txt"),
               "--collect-all", "pillow_heif"]
    for name in ("favdate.ico", "favdate.png", "Manuel-DatePhoto.html", "LICENSE", "LICENSE-DOCS"):
        command.extend(["--add-data", str(ROOT / name) + ";."])
    command.append(str(ROOT / "EigrutelDatePhoto.py"))
    subprocess.run(command, cwd=ROOT, check=True)
    exe = ROOT / "dist" / (NAME + ".exe")
    if not exe.is_file() or exe.stat().st_size == 0:
        raise SystemExit("EXE absent / Missing EXE")
    digest = hashlib.sha256(exe.read_bytes()).hexdigest()
    (ROOT / "dist" / "SHA256SUMS.txt").write_text(digest + "  " + exe.name + "\n", encoding="utf-8")
    print(str(exe))

if __name__ == "__main__":
    main()
