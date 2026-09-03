"""Регрессионные проверки раздачи статических файлов.

Исторически catch-all маршрут склеивал путь из URL с каталогом сборки напрямую
и проверял только is_file(), из-за чего по сети были доступны файлы вне
frontend/dist: база данных, .env, исходники. Эти тесты фиксируют, что путь
всегда остаётся внутри каталога сборки.
"""
from __future__ import annotations

import pathlib

import pytest

BACKEND_DIR = pathlib.Path(__file__).resolve().parents[1]
PROJECT_DIR = BACKEND_DIR.parent
FRONTEND_DIST = PROJECT_DIR / "frontend" / "dist"

# Файлы, которые ни при каких условиях не должны покидать пределы процесса.
SENSITIVE = [
    ("gamedev_dss.db", b"SQLite format 3"),
    ("requirements.txt", b"fastapi"),
    ("app/main.py", b"FastAPI"),
]

# Варианты обхода, которые нужно перекрыть: обычные, URL-encoded и
# double-encoded сегменты «..», а также абсолютные пути Windows и POSIX.
TRAVERSAL_PATHS = [
    "../backend/gamedev_dss.db",
    "..%2Fbackend%2Fgamedev_dss.db",
    "%2e%2e%2fbackend%2fgamedev_dss.db",
    "%2e%2e/%2e%2e/backend/gamedev_dss.db",
    "%252e%252e%252fbackend%252fgamedev_dss.db",
    "..%5Cbackend%5Cgamedev_dss.db",
    "....//backend/gamedev_dss.db",
    "..;/backend/gamedev_dss.db",
    "/../backend/gamedev_dss.db",
    "//../backend/gamedev_dss.db",
    "/backend/gamedev_dss.db",
    "C:/Users/user/Desktop/game-inspect/backend/gamedev_dss.db",
    "..\\backend\\gamedev_dss.db",
    "../../../backend/app/main.py",
    "..%2F..%2Fbackend%2Frequirements.txt",
]


pytestmark = pytest.mark.skipif(
    not FRONTEND_DIST.exists(),
    reason="frontend не собран — статическая раздача не зарегистрирована",
)


def test_frontend_build_exists():
    """Проверки имеют смысл только при наличии сборки."""
    assert (FRONTEND_DIST / "index.html").is_file()


@pytest.mark.parametrize("path", TRAVERSAL_PATHS)
def test_traversal_paths_never_return_sensitive_files(client, path):
    response = client.get(f"/{path}")
    body = response.content
    for _name, marker in SENSITIVE:
        assert marker not in body, f"Путь «{path}» раскрыл содержимое защищённого файла"


@pytest.mark.parametrize("path", TRAVERSAL_PATHS)
def test_traversal_paths_fall_back_to_spa_index(client, path):
    """Неизвестный путь — это клиентский маршрут, поэтому отдаётся index.html."""
    response = client.get(f"/{path}")
    assert response.status_code == 200
    assert b"<div id=\"root\"></div>" in response.content


def test_static_asset_is_still_served(client):
    """Обычные файлы сборки должны отдаваться без изменений."""
    assets = sorted((FRONTEND_DIST / "assets").glob("*.js"))
    assert assets, "в сборке нет JS-файлов — нечего проверять"
    asset = assets[0]
    response = client.get(f"/assets/{asset.name}")
    assert response.status_code == 200
    assert response.content == asset.read_bytes()


def test_index_is_served_at_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"<div id=\"root\"></div>" in response.content


def test_client_route_falls_back_to_index(client):
    """Клиентские маршруты приложения не должны давать 404."""
    for route in ("solutions", "basket", "hardware", "admin"):
        response = client.get(f"/{route}")
        assert response.status_code == 200, route
        assert b"<div id=\"root\"></div>" in response.content


# ---------------------------------------------------------------------------
# Прямые проверки функции безопасного пути
# ---------------------------------------------------------------------------
def test_safe_static_path_accepts_nested_file():
    from app.staticfiles_safe import safe_static_path

    asset = sorted((FRONTEND_DIST / "assets").glob("*.js"))[0]
    resolved = safe_static_path(FRONTEND_DIST, f"assets/{asset.name}")
    assert resolved == asset.resolve()


def test_safe_static_path_rejects_escape():
    from app.staticfiles_safe import safe_static_path

    for candidate in (
        "../backend/gamedev_dss.db",
        "assets/../../../backend/gamedev_dss.db",
        "/etc/passwd",
        "C:\\Windows\\win.ini",
        "",
        "..",
        "%2e%2e%2fbackend",
    ):
        assert safe_static_path(FRONTEND_DIST, candidate) is None, candidate


def test_safe_static_path_rejects_disallowed_extension(tmp_path):
    """Файл с неразрешённым расширением внутри сборки не выдаётся."""
    from app.staticfiles_safe import safe_static_path

    (tmp_path / "secret.env").write_text("ADMIN_TOKEN=secret", encoding="utf-8")
    assert safe_static_path(tmp_path, "secret.env") is None


def test_safe_static_path_rejects_symlink_outside_root(tmp_path):
    """Символическая ссылка, ведущая за пределы каталога сборки, отвергается."""
    from app.staticfiles_safe import safe_static_path

    root = tmp_path / "dist"
    root.mkdir()
    outside = tmp_path / "private.txt"
    outside.write_text("секретно", encoding="utf-8")
    link = root / "link.txt"
    try:
        link.symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("создание символических ссылок недоступно")
    if not link.is_symlink():
        # Windows без прав разработчика создаёт не ссылку, а обычный файл:
        # в таком окружении сценарий проверить нельзя.
        pytest.skip("символическая ссылка не создана — сценарий недоступен")
    assert safe_static_path(root, "link.txt") is None
