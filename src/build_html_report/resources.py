from pathlib import Path
import base64
import urllib.parse

BASE_DIR = Path(__file__).resolve().parent
RESOURCES_DIR = BASE_DIR / "resources"


def get_css():
    return _read_file(RESOURCES_DIR / "styles.css")


def get_favicon():
    return _read_svg(RESOURCES_DIR / "favicon.svg")


def get_github():
    return _read_png(RESOURCES_DIR / "github.png")


def _read_file(path, encoding="utf-8"):
    return Path(path).read_text(encoding)


def _read_png(path):
    with open(path, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode("ascii")


def _read_svg(path):
    svg = _read_file(path)
    return "data:image/svg+xml," + urllib.parse.quote(svg)
