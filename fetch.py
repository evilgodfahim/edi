import requests
import sys

FLARESOLVERR_URL = "http://localhost:8191/v1"

TARGETS = {
    "opinion_bangladesherkhabor.html": "https://www.bangladesherkhabor.net/opinion",
    "uposompadokio_protidinersangbad.html": "https://www.protidinersangbad.com/todays-newspaper/uposompadokio/"
}

for filename, url in TARGETS.items():
    payload = {
        "cmd": "request.get",
        "url": url,
        "maxTimeout": 60000
    }

    r = requests.post(FLARESOLVERR_URL, json=payload)
    data = r.json()

    # Explicit FlareSolverr error
    if "error" in data:
        print(f"FlareSolverr error for {url}:", data["error"])
        continue

    # Silent failure protection
    if "solution" not in data or "response" not in data["solution"]:
        print(f"Invalid FlareSolverr response for {url}:", data)
        continue

    html = data["solution"]["response"]

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
