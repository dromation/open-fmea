from __future__ import annotations

import os
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path
from socketserver import ThreadingMixIn
from wsgiref.simple_server import WSGIRequestHandler, WSGIServer, make_server


class ThreadingWSGIServer(ThreadingMixIn, WSGIServer):
    daemon_threads = True


class QuietRequestHandler(WSGIRequestHandler):
    def log_message(self, format: str, *args) -> None:
        return


def runtime_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parent


def data_dir() -> Path:
    base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
    if base:
        return Path(base) / "OpenFMEA"
    return Path.home() / ".open_fmea"


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def configure_environment() -> Path:
    root = runtime_root()
    for package_root in (root / "domain", root / "django_app"):
        package_path = str(package_root)
        if package_path not in sys.path:
            sys.path.insert(0, package_path)

    app_data = data_dir()
    app_data.mkdir(parents=True, exist_ok=True)
    db_path = app_data / "open_fmea_demo.sqlite3"

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "open_fmea_project.settings")
    os.environ.setdefault("OPEN_FMEA_DEBUG", "1")
    os.environ.setdefault("OPEN_FMEA_SECRET_KEY", "open-fmea-demo-local-only")
    os.environ["OPEN_FMEA_DB_PATH"] = str(db_path)
    return db_path


def prepare_database() -> None:
    import django
    from django.core.management import call_command

    django.setup()
    call_command("migrate", interactive=False, verbosity=0)
    call_command("seed_demo", verbosity=0)


def main() -> int:
    db_path = configure_environment()
    prepare_database()

    from django.core.wsgi import get_wsgi_application

    application = get_wsgi_application()
    port = free_port()
    url = f"http://127.0.0.1:{port}/"
    server = make_server(
        "127.0.0.1",
        port,
        application,
        server_class=ThreadingWSGIServer,
        handler_class=QuietRequestHandler,
    )

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    if os.environ.get("OPEN_FMEA_NO_BROWSER") != "1":
        webbrowser.open(url)

    print("Open FMEA demo is running.", flush=True)
    print(f"URL: {url}", flush=True)
    print(f"Database: {db_path}", flush=True)
    print("Close this window to stop the demo server.", flush=True)

    try:
        while thread.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
        server.server_close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
