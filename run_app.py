import atexit
import os
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path


HOST = "127.0.0.1"
PORT = 8000
STARTUP_TIMEOUT_SECONDS = 30.0
READINESS_INTERVAL_SECONDS = 0.5
APP_NAME = "Smart Sustainable Campus Management"


def _is_frozen() -> bool:
    return getattr(sys, "frozen", False)


def _project_base_dir() -> Path:
    # In frozen mode, collect project files next to the executable.
    if _is_frozen():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def _log_line(message: str) -> None:
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}\n"
    print(message)
    try:
        (_project_base_dir() / "launcher.log").open("a", encoding="utf-8").write(line)
    except OSError:
        # Logging failure should never prevent app startup.
        pass


def _run_server_mode() -> int:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ssc_ms.settings")
    # For standalone apps, we want a stable environment
    os.environ["PYWEBVIEW_RUNNING"] = "1"
    
    # In frozen mode, we might want to disable debug but runserver needs --insecure for static
    # Or just keep debug for now if it's easier.
    if _is_frozen():
        os.environ["DJANGO_DEBUG"] = "False"

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        _log_line(f"Django import failed in server mode: {exc}")
        return 1

    # Using --noreload and --insecure (if we ever set debug=False)
    args = ["manage.py", "runserver", f"{HOST}:{PORT}", "--noreload"]
    try:
        execute_from_command_line(args)
        return 0
    except Exception as exc:  # pragma: no cover
        _log_line(f"Server mode crashed: {exc}")
        return 1


class DjangoServerManager:
    """Starts a local Django dev server and tracks its lifecycle."""

    def __init__(self, host: str = HOST, port: int = PORT) -> None:
        self.host = host
        self.port = port
        self.url = f"http://{host}:{port}"
        self.base_dir = _project_base_dir()
        self.manage_py = self.base_dir / "manage.py"

        self._thread: threading.Thread | None = None
        self._process: subprocess.Popen | None = None
        self._ready_event = threading.Event()
        self._error: Exception | None = None
        self._started_by_launcher = False

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return

        self._thread = threading.Thread(target=self._start_server, daemon=True)
        self._thread.start()

    def wait_until_ready(self, timeout: float = 30.0) -> None:
        is_ready = self._ready_event.wait(timeout=timeout)
        if not is_ready:
            raise RuntimeError("Timed out while waiting for the Django server to start.")

        if self._error is not None:
            raise RuntimeError("Django server failed to start.") from self._error

    def stop(self) -> None:
        if self._process is None:
            return

        if self._process.poll() is not None:
            return

        self._process.terminate()
        try:
            self._process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self._process.kill()
            self._process.wait(timeout=5)

    def _start_server(self) -> None:
        try:
            if self._is_server_ready():
                self._ready_event.set()
                return

            if self._is_port_open() and not self._is_server_ready():
                raise RuntimeError(
                    f"Port {self.port} is already in use by another process."
                )

            if _is_frozen():
                command = [sys.executable, "--runserver"]
            else:
                command = [sys.executable, str(Path(__file__).resolve()), "--runserver"]

            creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
            self._process = subprocess.Popen(
                command,
                cwd=self.base_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=creationflags,
            )
            self._started_by_launcher = True

            max_attempts = int(STARTUP_TIMEOUT_SECONDS / READINESS_INTERVAL_SECONDS)
            for _ in range(max_attempts):
                if self._process.poll() is not None:
                    stderr_out = ""
                    if self._process.stderr is not None:
                        stderr_out = self._process.stderr.read().strip()
                    stdout_out = ""
                    if self._process.stdout is not None:
                        stdout_out = self._process.stdout.read().strip()
                    details = stderr_out or stdout_out or "No process output captured."
                    raise RuntimeError(f"Django server process exited unexpectedly: {details}")

                if self._is_server_ready():
                    self._ready_event.set()
                    return

                time.sleep(READINESS_INTERVAL_SECONDS)

            raise RuntimeError("Django server did not become ready in time.")
        except Exception as exc:
            self._error = exc
            self._ready_event.set()

    def _is_port_open(self) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            return sock.connect_ex((self.host, self.port)) == 0

    def _is_server_ready(self) -> bool:
        try:
            with urllib.request.urlopen(self.url, timeout=1.0) as response:
                return 200 <= response.status < 500
        except (urllib.error.URLError, TimeoutError, ConnectionError, ValueError):
            return False


def main() -> int:
    try:
        import webview
    except ImportError:
        _log_line("PyWebView is not installed. Run: pip install pywebview")
        return 1

    server = DjangoServerManager(host=HOST, port=PORT)
    atexit.register(server.stop)

    try:
        _log_line(f"Starting {APP_NAME}...")
        server.start()
        server.wait_until_ready(timeout=STARTUP_TIMEOUT_SECONDS)
        time.sleep(0.5)  # Let it stabilize

        webview.create_window(
            APP_NAME,
            server.url,
            width=1280,
            height=820,
            resizable=True,
            min_size=(800, 600),
        )
        _log_line(f"Opening window at {server.url}")
        webview.start(debug=False)
        return 0
    except Exception as exc:
        _log_line(f"Failed to launch desktop app: {exc}")
        return 1
    finally:
        if server._started_by_launcher:
            server.stop()


if __name__ == "__main__":
    if "--runserver" in sys.argv:
        raise SystemExit(_run_server_mode())
    raise SystemExit(main())
