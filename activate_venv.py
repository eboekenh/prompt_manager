import os
import platform
import subprocess
from pathlib import Path
import sys

venv_path = Path("venv")

def create_venv():
    """Yeni bir venv oluşturur"""
    print("⚙️  'venv' bulunamadı, şimdi oluşturuluyor...")
    try:
        subprocess.check_call([sys.executable, "-m", "venv", "venv"])
        print("✅ venv oluşturuldu.")
    except Exception as e:
        print("❌ venv oluşturulamadı:", e)
        sys.exit(1)

def activate_venv():
    """venv'i aktive eder"""
    system = platform.system()

    if system == "Windows":
        activate_script = venv_path / "Scripts" / "activate.bat"
        if not activate_script.exists():
            print("❌ Windows için activate.bat bulunamadı.")
            sys.exit(1)
        print("🔵 Windows ortamı bulundu. venv aktive ediliyor...")
        subprocess.call(["cmd.exe", "/K", str(activate_script)])

    elif system in ("Linux", "Darwin"):  # Darwin = MacOS
        activate_script = venv_path / "bin" / "activate"
        if not activate_script.exists():
            print("❌ Linux/Mac için activate script bulunamadı.")
            sys.exit(1)
        print("🟢 Linux/Mac ortamı bulundu. venv aktive ediliyor...")
        subprocess.call(["bash", "-i", "-c", f"source {activate_script} && exec bash"])

    else:
        print(f"❌ Desteklenmeyen sistem: {system}")

if __name__ == "__main__":
    if not venv_path.exists():
        create_venv()
    activate_venv()
