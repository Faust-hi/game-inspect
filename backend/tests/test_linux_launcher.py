"""Launcher failures must not open a browser or leave owned services behind."""
import importlib.util
from pathlib import Path
import socket
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('linux_launcher', ROOT / 'tools/launch_linux.py')
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)


def test_occupied_port_is_rejected_without_touching_owner():
    with socket.socket() as owner:
        owner.bind(('127.0.0.1', 0))
        owner.listen()
        port = owner.getsockname()[1]
        with pytest.raises(RuntimeError, match='occupied'):
            launcher.check_ports([('backend', [], ROOT, port)])
        with socket.create_connection(('127.0.0.1', port), timeout=1):
            assert owner.fileno() != -1


@pytest.mark.parametrize('status,body,expected', [
    (200, b'{"status":"ok","ready":true,"version":"1"}', True),
    (503, b'{"status":"ok","ready":true,"version":"1"}', False),
    (200, b'{"status":"degraded","ready":false,"version":"1"}', False),
    (200, b'[]', False), (200, b'<html>other application</html>', False),
])
def test_backend_readiness_requires_successful_health(monkeypatch, status, body, expected):
    class Connection:
        closed = False
        def request(self, *_): pass
        def getresponse(self): return self
        def read(self, *_): return body
        def close(self): self.closed = True
    connection = Connection()
    connection.status = status
    monkeypatch.setattr(launcher.http.client, 'HTTPConnection', lambda *a, **k: connection)
    assert launcher.ready('backend', 8000) is expected
    assert connection.closed


def test_failed_npm_install_is_not_ignored_even_with_existing_node_modules(tmp_path, monkeypatch):
    frontend = tmp_path / 'frontend'
    (frontend / 'node_modules').mkdir(parents=True)
    (frontend / 'package-lock.json').write_text('{}')
    calls = []
    def fail(command, cwd):
        calls.append((command, cwd))
        raise subprocess.CalledProcessError(1, command)
    monkeypatch.setattr(launcher, 'run', fail)
    with pytest.raises(subprocess.CalledProcessError):
        launcher.prepare(tmp_path, 'frontend', False)
    assert calls == [(['npm', 'ci'], frontend)]


def test_install_uses_linux_venv_and_locked_requirements_with_spaces(tmp_path, monkeypatch):
    root = tmp_path / 'project with spaces'
    (root / 'backend').mkdir(parents=True)
    (root / 'backend/requirements.lock').write_text('uvicorn==0.52.4')
    python = root / '.venv-linux/bin/python'
    python.parent.mkdir(parents=True)
    python.touch()
    calls = []
    monkeypatch.setattr(launcher, 'run', lambda command, cwd: calls.append((command, cwd)))
    launcher.prepare(root, 'backend', False)
    assert calls[0][0][0] == python
    assert calls[0][0][-1] == root / 'backend/requirements.lock'
    assert all('.venv/Scripts' not in str(command) for command, _ in calls)


def test_early_service_exit_stops_sibling_without_opening_browser(monkeypatch):
    class Child:
        returncode = 1
        def poll(self): return 1
    children, stopped, opened = [], [], []
    def spawn(*a, **kwargs):
        assert kwargs['start_new_session'] is True
        child = Child()
        children.append(child)
        return child
    monkeypatch.setattr(launcher.subprocess, 'Popen', spawn)
    monkeypatch.setattr(launcher, 'stop', lambda items: stopped.extend(items))
    monkeypatch.setattr(launcher.webbrowser, 'open', lambda url: opened.append(url))
    with pytest.raises(RuntimeError, match='exited'):
        launcher.serve([('backend', [], ROOT, 8000), ('frontend', [], ROOT, 5173)])
    assert len(stopped) == 2 and stopped == children
    assert not opened


@pytest.mark.skipif(sys.platform != 'linux', reason='Actual Linux process-group cleanup')
def test_linux_cleanup_terminates_launched_processes():
    child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'], start_new_session=True)
    try:
        launcher.stop([child])
        assert child.poll() is not None
    finally:
        if child.poll() is None:
            child.kill()
            child.wait()
