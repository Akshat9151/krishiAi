import os
import time
import requests


BASE = os.getenv("BASE_URL", "http://127.0.0.1:8000")


def wait_for_health(timeout_seconds: int = 10) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            r = requests.get(f"{BASE}/health", timeout=1.5)
            if r.status_code == 200:
                print("HEALTH:", r.json())
                return
        except Exception:
            pass
        time.sleep(0.3)
    raise RuntimeError("Server did not become healthy in time")


def main() -> None:
    # health
    wait_for_health()

    # root
    r = requests.get(f"{BASE}/")
    print("ROOT:", r.status_code, r.text)

    # register
    payload = {"username": "demo", "password": "secret123"}
    r = requests.post(f"{BASE}/auth/register", json=payload)
    print("REGISTER:", r.status_code, r.text)

    # login
    r = requests.post(f"{BASE}/auth/login", json=payload)
    print("LOGIN:", r.status_code, r.text)

    # predict-crop
    body = {
        "soil_type": "clay",
        "season": "monsoon",
        "location": "MH",
        "temperature": 26,
        "humidity": 80,
    }
    r = requests.post(f"{BASE}/predict-crop", json=body)
    print("PREDICT:", r.status_code, r.text)


if __name__ == "__main__":
    main()

