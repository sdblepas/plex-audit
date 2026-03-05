import time
import json
import requests
import os

from app.config import cfg

TMDB_API_KEY = cfg("tmdb", "api_key")
TMDB_MIN_DELAY = float(cfg("tmdb", "min_delay"))

CACHE_FILE = "/app/data/tmdb_cache.json"


def load_cache():
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_cache(cache):
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)

    tmp = CACHE_FILE + ".tmp"

    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

    os.replace(tmp, CACHE_FILE)


class TMDB:

    def __init__(self):

        if not TMDB_API_KEY:
            raise RuntimeError("TMDB api_key missing in config.yml")

        self.s = requests.Session()
        self.cache = load_cache()

    def get(self, url):

        if url in self.cache:
            return self.cache[url]

        try:
            r = self.s.get(url, timeout=20)
        except requests.RequestException:
            return None

        if r.status_code != 200:
            return None

        data = r.json()

        self.cache[url] = data

        time.sleep(TMDB_MIN_DELAY)

        return data

    def flush(self):
        save_cache(self.cache)

    def movie(self, tmdb_id):
        return self.get(
            f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={TMDB_API_KEY}"
        )

    def collection(self, cid):
        return self.get(
            f"https://api.themoviedb.org/3/collection/{cid}?api_key={TMDB_API_KEY}"
        )

    def top_rated(self, page):
        return self.get(
            f"https://api.themoviedb.org/3/movie/top_rated?api_key={TMDB_API_KEY}&page={page}"
        )

    def search_person(self, name):

        q = requests.utils.quote(name)

        return self.get(
            f"https://api.themoviedb.org/3/search/person?api_key={TMDB_API_KEY}&query={q}"
        )

    def person_credits(self, pid):

        return self.get(
            f"https://api.themoviedb.org/3/person/{pid}/movie_credits?api_key={TMDB_API_KEY}"
        )

    @staticmethod
    def poster_url(path, size="w342"):

        if not path:
            return None

        return f"https://image.tmdb.org/t/p/{size}{path}"