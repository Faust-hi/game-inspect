"""Linux local launcher. Installs in-project; owns and stops only its children."""
from __future__ import annotations

import argparse
import http.client
import json
import os
from pathlib import Path
import shutil
import signal
import socket
import subprocess
import sys
import time
import webbrowser

ROOT = Path(__file__).resolve().parents[1]


def run(command, cwd=ROOT):
    subprocess.run([str(part) for part in command], cwd=cwd, check=True)


def preflight(service):
    if not sys.platform.startswith('linux'):
        raise RuntimeError('This launcher is for Linux. On Windows use start.bat.')
    if sys.version_info < (3, 11):
        raise RuntimeError('Python 3.11+ required; select it with DSS_PYTHON=python3.13.')
    if service != 'backend':
        if not shutil.which('node') or not shutil.which('npm'):
            raise RuntimeError('Install Node.js 22+ and npm. See README.md -> Linux.')
        version = subprocess.check_output(['node', '-p', 'process.versions.node'], text=True).strip()
        if int(version.split('.')[0]) < 22:
            raise RuntimeError(f'Node.js {version} found; use Node.js 22+ (LTS recommended).')


def commands(root, service):
    result = []
    if service != 'frontend':
        result.append(('backend', [str(root / '.venv-linux/bin/python'), '-m', 'uvicorn',
                                   'app.main:app', '--host', '127.0.0.1', '--port', '8000'], root / 'backend', 8000))
    if service != 'backend':
        # Launch Node directly: no npm/shell intermediate process to orphan.
        result.append(('frontend', ['node', str(root / 'frontend/node_modules/vite/bin/vite.js'),
                                    '--host', '127.0.0.1', '--port', '5173', '--strictPort'], root / 'frontend', 5173))
    return result


def check_ports(services):
    for name, _, _, port in services:
        with socket.socket() as probe:
            if sys.platform.startswith('linux'):
                probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                probe.bind(('127.0.0.1', port))
            except OSError as error:
                raise RuntimeError(f'{name}: port {port} is occupied or unavailable. No existing process was stopped.') from error


def prepare(root, service, skip_install):
    python = root / '.venv-linux/bin/python'
    if not skip_install:
        if service != 'frontend':
            if not python.is_file():
                try:
                    run([sys.executable, '-m', 'venv', root / '.venv-linux'], root)
                except subprocess.CalledProcessError as error:
                    raise RuntimeError('Cannot create venv. On Mint/Kali/Ubuntu/Debian install python3-venv, then retry.') from error
            lock = root / 'backend/requirements.lock'
            requirements = lock if lock.is_file() else root / 'backend/requirements.txt'
            run([python, '-m', 'pip', 'install', '--disable-pip-version-check', '-r', requirements], root)
        if service != 'backend':
            command = 'ci' if (root / 'frontend/package-lock.json').is_file() else 'install'
            run(['npm', command], root / 'frontend')
    if service != 'frontend':
        if not python.is_file():
            raise RuntimeError('Linux venv is missing. Run bash start.sh without --skip-install.')
        run([python, '-c', 'import sys, uvicorn; assert sys.version_info >= (3, 11)'], root)
    if service != 'backend' and not (root / 'frontend/node_modules/vite/bin/vite.js').is_file():
        raise RuntimeError('Vite is missing. Run bash start.sh without --skip-install.')


def ready(name, port):
    connection = http.client.HTTPConnection('127.0.0.1', port, timeout=1)
    try:
        connection.request('GET', '/api/health' if name == 'backend' else '/')
        response = connection.getresponse()
        body = response.read(128 * 1024)
        if response.status != 200:
            return False
        if name == 'backend':
            data = json.loads(body)
            return isinstance(data, dict) and data.get('status') == 'ok' and data.get('ready') is True and bool(data.get('version'))
        return b'id="root"' in body and b'/@vite/client' in body
    except (OSError, ValueError, http.client.HTTPException):
        return False
    finally:
        connection.close()


def stop(children):
    # Every service has its own session. Never signal the launcher's group or
    # a process found merely by port/name; descendants belong to our sessions.
    for child in children:
        try:
            os.killpg(child.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    deadline = time.monotonic() + 5
    for child in children:
        try:
            child.wait(timeout=max(0, deadline - time.monotonic()))
        except subprocess.TimeoutExpired:
            pass
    for child in children:
        try:
            os.killpg(child.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        child.wait()


def serve(services, open_browser=True, timeout=90):
    children = []
    try:
        for name, command, cwd, _ in services:
            print(f'Starting {name}...', flush=True)
            children.append(subprocess.Popen(command, cwd=cwd, start_new_session=True))
        deadline = time.monotonic() + timeout
        while True:
            for child in children:
                if child.poll() is not None:
                    raise RuntimeError(f'A service exited (code {child.returncode}). See output above.')
            if all(ready(name, port) for name, _, _, port in services):
                break
            if time.monotonic() >= deadline:
                raise RuntimeError(f'Services did not become ready within {timeout} seconds. See output above.')
            time.sleep(0.3)
        for name, _, _, port in services:
            print(f'{name}: http://127.0.0.1:{port}' + ('/api/docs' if name == 'backend' else ''), flush=True)
        if open_browser and any(name == 'frontend' for name, *_ in services):
            try:
                webbrowser.open('http://127.0.0.1:5173')
            except webbrowser.Error:
                print('Open the frontend URL in your browser manually.', flush=True)
        print('Press Ctrl+C to stop the services.', flush=True)
        while all(child.poll() is None for child in children):
            time.sleep(0.3)
        raise RuntimeError('A service stopped. Stopping the other service as well.')
    finally:
        stop(children)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skip-install', action='store_true', help='Use already installed dependencies')
    parser.add_argument('--no-browser', action='store_true', help='Do not open a browser (e.g. SSH)')
    parser.add_argument('--check', action='store_true', help='Check runtimes and ports without installing or starting')
    parser.add_argument('--service', choices=['all', 'backend', 'frontend'], default='all')
    args = parser.parse_args(argv)
    # Treat terminal close and SIGTERM like Ctrl+C, including owned cleanup.
    def interrupted(_signum, _frame):
        raise KeyboardInterrupt
    for sig in (signal.SIGTERM, signal.SIGHUP) if os.name == 'posix' else ():
        signal.signal(sig, interrupted)
    try:
        preflight(args.service)
        services = commands(ROOT, args.service)
        check_ports(services)
        if args.check:
            print('Runtime versions and ports OK. Dependencies and actual service startup not checked.')
            return 0
        prepare(ROOT, args.service, args.skip_install)
        check_ports(services)
        serve(services, not args.no_browser)
        return 0
    except KeyboardInterrupt:
        return 130
    except (OSError, RuntimeError, subprocess.CalledProcessError, ValueError) as error:
        print(f'Startup failed: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
