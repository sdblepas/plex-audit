import requests
import xml.etree.ElementTree as ET
from collections import defaultdict

from app.config import cfg

PLEX_URL = cfg("plex", "url")
PLEX_TOKEN = cfg("plex", "token")
LIBRARY_NAME = cfg("plex", "library_name")

SHORT_MOVIE_LIMIT = int(cfg("plex", "short_movie_limit"))
PLEX_PAGE_SIZE = int(cfg("plex", "page_size"))


def plex_get(path, params=None):

    if params is None:
        params = {}

    params["X-Plex-Token"] = PLEX_TOKEN

    r = requests.get(PLEX_URL + path, params=params, timeout=30)

    r.raise_for_status()

    return r.text


def library_key():

    xml = plex_get("/library/sections")

    root = ET.fromstring(xml)

    for d in root.findall("Directory"):

        if d.attrib.get("title") == LIBRARY_NAME:
            return d.attrib.get("key")

    raise RuntimeError("Plex library not found")


def scan_movies():

    key = library_key()

    plex_ids = set()

    directors = defaultdict(set)
    actors = defaultdict(set)

    no_tmdb_guid = []

    start = 0

    scanned = 0
    skipped_short = 0

    while True:

        xml = plex_get(
            f"/library/sections/{key}/all",
            {
                "type": "1",
                "includeGuids": "1",
                "X-Plex-Container-Start": start,
                "X-Plex-Container-Size": PLEX_PAGE_SIZE,
            },
        )

        root = ET.fromstring(xml)

        videos = root.findall("Video")

        if not videos:
            break

        for v in videos:

            scanned += 1

            duration_ms = v.attrib.get("duration")
            duration_min = int(duration_ms) / 60000 if duration_ms else 0

            if duration_min < SHORT_MOVIE_LIMIT:
                skipped_short += 1
                continue

            tmdb_id = None

            for g in v.findall("Guid"):

                gid = g.attrib.get("id")

                if gid.startswith("tmdb://"):
                    tmdb_id = int(gid.split("tmdb://")[1])
                    break

            if not tmdb_id:

                no_tmdb_guid.append({
                    "title": v.attrib.get("title"),
                    "year": v.attrib.get("year")
                })

                continue

            plex_ids.add(tmdb_id)

            for d in v.findall("Director"):

                tag = d.attrib.get("tag")

                if tag:
                    directors[tag].add(tmdb_id)

            for r in v.findall("Role"):

                tag = r.attrib.get("tag")

                if tag:
                    actors[tag].add(tmdb_id)

        start += len(videos)

    directors = {k: v for k, v in directors.items() if len(v) > 1}
    actors = {k: v for k, v in actors.items() if len(v) > 1}

    stats = {
        "scanned_items": scanned,
        "indexed_tmdb": len(plex_ids),
        "skipped_short": skipped_short,
        "directors_kept": len(directors),
        "actors_kept": len(actors),
        "no_tmdb_guid": len(no_tmdb_guid),
    }

    return plex_ids, directors, actors, stats, no_tmdb_guid