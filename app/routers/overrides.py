"""
Ignore / Unignore / Wishlist routes.
  POST /api/ignore
  POST /api/unignore
  GET  /api/ignored
  POST /api/wishlist/add
  POST /api/wishlist/remove
"""
from fastapi import APIRouter, Body

from app.overrides import load_json, save_json, add_unique, remove_value
from app.routers._shared import OVERRIDES_FILE, _parse_tmdb_id

router = APIRouter()


# --------------------------------------------------
# Ignore / Unignore
# --------------------------------------------------

@router.post("/api/ignore")
def api_ignore(payload: dict = Body(...)):
    ov    = load_json(OVERRIDES_FILE)
    kind  = payload.get("kind")
    value = payload.get("value")

    if kind == "movie":
        tmdb_id = _parse_tmdb_id(value)
        if tmdb_id is None:
            return {"ok": False, "error": "Invalid TMDB ID"}
        add_unique(ov["ignore_movies"], tmdb_id)
        ov.setdefault("ignore_movies_meta", {})[str(tmdb_id)] = {
            "title":  payload.get("title", ""),
            "year":   payload.get("year"),
            "poster": payload.get("poster"),
        }
    elif kind == "franchise":
        add_unique(ov["ignore_franchises"], str(value))
    elif kind == "director":
        add_unique(ov["ignore_directors"], str(value))
    elif kind == "actor":
        add_unique(ov["ignore_actors"], str(value))
    else:
        return {"ok": False, "error": f"Unknown kind: {kind}"}

    save_json(OVERRIDES_FILE, ov)
    return {"ok": True}


@router.post("/api/unignore")
def api_unignore(payload: dict = Body(...)):
    ov    = load_json(OVERRIDES_FILE)
    kind  = payload.get("kind")
    value = payload.get("value")

    if kind == "movie":
        tmdb_id = _parse_tmdb_id(value)
        if tmdb_id is None:
            return {"ok": False, "error": "Invalid TMDB ID"}
        remove_value(ov["ignore_movies"], tmdb_id)
        ov.setdefault("ignore_movies_meta", {}).pop(str(tmdb_id), None)
    elif kind == "franchise":
        remove_value(ov["ignore_franchises"], str(value))
    elif kind == "director":
        remove_value(ov["ignore_directors"], str(value))
    elif kind == "actor":
        remove_value(ov["ignore_actors"], str(value))
    else:
        return {"ok": False, "error": f"Unknown kind: {kind}"}

    save_json(OVERRIDES_FILE, ov)
    return {"ok": True}


@router.get("/api/ignored")
def api_ignored():
    ov   = load_json(OVERRIDES_FILE)
    ids  = ov.get("ignore_movies", [])
    meta = ov.get("ignore_movies_meta", {})
    movies = []
    for tmdb_id in ids:
        m = meta.get(str(tmdb_id), {})
        movies.append({
            "tmdb":   tmdb_id,
            "title":  m.get("title", f"Movie {tmdb_id}"),
            "year":   m.get("year"),
            "poster": m.get("poster"),
        })
    return {
        "ok":         True,
        "movies":     movies,
        "franchises": ov.get("ignore_franchises", []),
        "directors":  ov.get("ignore_directors",  []),
        "actors":     ov.get("ignore_actors",      []),
    }


# --------------------------------------------------
# Wishlist
# --------------------------------------------------

@router.post("/api/wishlist/add")
def wishlist_add(payload: dict = Body(...)):
    ov = load_json(OVERRIDES_FILE)
    add_unique(ov["wishlist_movies"], int(payload.get("tmdb")))
    save_json(OVERRIDES_FILE, ov)
    return {"ok": True}


@router.post("/api/wishlist/remove")
def wishlist_remove(payload: dict = Body(...)):
    ov = load_json(OVERRIDES_FILE)
    remove_value(ov["wishlist_movies"], int(payload.get("tmdb")))
    save_json(OVERRIDES_FILE, ov)
    return {"ok": True}
