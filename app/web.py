import json
import requests
from fastapi import FastAPI, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from app.config import cfg
from app.scanner import build
from app.overrides import load_json, save_json, add_unique, remove_value

DATA_DIR = "/app/data"
RESULTS_FILE = f"{DATA_DIR}/results.json"
OVERRIDES_FILE = f"{DATA_DIR}/overrides.json"

RADARR_ENABLED = cfg("radarr", "enabled")
RADARR_URL = cfg("radarr", "url")
RADARR_API_KEY = cfg("radarr", "api_key")
RADARR_ROOT = cfg("radarr", "root_folder_path")
RADARR_PROFILE = int(cfg("radarr", "quality_profile_id"))
RADARR_MONITORED = cfg("radarr", "monitored")

app = FastAPI()

app.mount("/static", StaticFiles(directory="/app/static"), name="static")


def read_results():

    try:
        with open(RESULTS_FILE) as f:
            return json.load(f)
    except Exception:
        return None


@app.get("/", response_class=HTMLResponse)
def index():

    with open("/app/static/index.html") as f:
        return f.read()


@app.get("/api/results")
def api_results():

    data = read_results()

    if data is None:
        data = build()

    return data


@app.post("/api/scan")
def api_scan():

    return build()


@app.post("/api/radarr/add")
def radarr_add(payload: dict = Body(...)):

    if not RADARR_ENABLED:
        return {"ok": False, "error": "RADARR disabled"}

    tmdb_id = int(payload.get("tmdb"))
    title = payload.get("title")

    body = {
        "title": title,
        "tmdbId": tmdb_id,
        "qualityProfileId": RADARR_PROFILE,
        "rootFolderPath": RADARR_ROOT,
        "monitored": RADARR_MONITORED,
        "addOptions": {
            "searchForMovie": False
        }
    }

    headers = {
        "X-Api-Key": RADARR_API_KEY
    }

    print("RADARR REQUEST", body)

    r = requests.post(
        f"{RADARR_URL}/api/v3/movie",
        json=body,
        headers=headers,
        timeout=20
    )

    print("RADARR RESPONSE", r.status_code, r.text)

    if r.status_code not in (200, 201):
        return {"ok": False, "error": r.text}

    return {"ok": True}