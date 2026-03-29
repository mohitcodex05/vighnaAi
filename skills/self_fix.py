"""
skills/self_fix.py — Automated self-repair skill for Vighna
Can fix missing dependencies and reset configurations.
"""

import subprocess
import sys
import os


def install_missing_package(package_name: str) -> str:
    """Attempt to install a missing package via pip."""
    try:
        print(f"[Self-Fix] Attempting to install missing package: {package_name}")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", package_name],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return f"Successfully installed {package_name}. Please restart Vighna."
    except Exception as e:
        return f"Failed to install {package_name}: {e}"


def handle_module_error(traceback_text: str) -> str | None:
    """Analyze traceback and fix if it's a ModuleNotFoundError."""
    import re
    match = re.search(r"ModuleNotFoundError: No module named '([^']+)'", traceback_text)
    if match:
        pkg = match.group(1)
        # Translation map for common library → package names
        pkg_map = {
            "cv2": "opencv-python",
            "PIL": "Pillow",
            "fitz": "PyMuPDF",
            "skimage": "scikit-image",
            "yaml": "PyYAML",
        }
        install_pkg = pkg_map.get(pkg, pkg)
        return install_missing_package(install_pkg)
    return None


def reset_config() -> str:
    """Reset the knowledge.json to defaults if corrupted."""
    knowledge_path = os.path.join(os.path.dirname(__file__), "..", "memory", "knowledge.json")
    default_data = {
        "app_aliases": { "vs code": "vscode", "chrome": "chrome" },
        "work_modes": { "start work": ["vscode", "chrome"] },
        "preferences": {}
    }
    try:
        import json
        with open(knowledge_path, "w", encoding="utf-8") as f:
            json.dump(default_data, f, indent=2)
        return "Configuration has been reset to defaults."
    except Exception as e:
        return f"Failed to reset config: {e}"

METADATA = {
    "name": "self_fix",
    "description": "Diagnostics and automated repairs for Vighna.",
    "intents": ["fix", "repair", "diagnose", "install", "debug"]
}

def execute(action: str, args: dict) -> str:
    if action == "install_pkg":
        return install_missing_package(args.get("package", ""))
    if action == "reset_config":
        return reset_config()
    return "Unknown self-fix action."
