"""CI acceptance: actual lock installation, both HTTP services and signal cleanup."""
import importlib.util
from pathlib import Path
import os
import signal
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('launcher', ROOT / 'tools/launch_linux.py')
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)


def main():
    launcher.check_ports(launcher.commands(ROOT, 'all'))
    with tempfile.TemporaryDirectory(prefix='dss-linux-smoke-') as directory:
        env = dict(os.environ, DATABASE_URL=f'sqlite:///{directory}/smoke.db', AUTO_SEED='true')
        log = Path(directory) / 'launcher.log'
        with log.open('w') as output:
            process = subprocess.Popen(['bash', str(ROOT / 'start.sh'), '--no-browser'],
                                       cwd=directory, env=env, stdout=output, stderr=subprocess.STDOUT)
            try:
                deadline = time.monotonic() + 360
                while not (launcher.ready('backend', 8000) and launcher.ready('frontend', 5173)):
                    if process.poll() is not None or time.monotonic() > deadline:
                        raise RuntimeError('Linux launcher did not become ready')
                    time.sleep(0.3)
                process.send_signal(signal.SIGINT)
                assert process.wait(timeout=15) == 130
                launcher.check_ports(launcher.commands(ROOT, 'all'))
                print('Linux startup: install, readiness and Ctrl+C cleanup passed.')
            finally:
                if process.poll() is None:
                    process.terminate()
                    process.wait(timeout=15)
                print(log.read_text())


if __name__ == '__main__':
    main()
