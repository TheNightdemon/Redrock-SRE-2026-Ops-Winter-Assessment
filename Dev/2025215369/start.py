import subprocess
import sys


def run() -> None:
    processes = []
    try:
        processes.append(
            subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "uvicorn",
                    "app.main:app",
                    "--host",
                    "0.0.0.0",
                    "--port",
                    "8000",
                ]
            )
        )
        processes.append(
            subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "uvicorn",
                    "webhook.main:app",
                    "--host",
                    "0.0.0.0",
                    "--port",
                    "8001",
                ]
            )
        )
        for proc in processes:
            proc.wait()
    finally:
        for proc in processes:
            if proc.poll() is None:
                proc.terminate()


if __name__ == "__main__":
    run()
