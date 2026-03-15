/* ============================================================
   config.js — Config tab renderer, save, cache management
============================================================ */

function _ageStr(s){
  if (s < 3600)  return `${Math.floor(s/60)}m ago`
  if (s < 86400) return `${Math.floor(s/3600)}h ago`
  return `${Math.floor(s/86400)}d ago`
}

async function loadCacheInfo(){
  try {
    const [info, bkp] = await Promise.all([
      api("/api/cache/info"),
      api("/api/cache/backup/info"),
    ])
    const el = document.getElementById("cache-info")
    if (!el) return

    let html = ""
    if (!info.exists){
      html += `<div>No cache yet — will be created on first scan.</div>`
    } else {
      html += `<div>Cache: <span style="color:var(--text)">${info.size_mb} MB</span> · updated <span style="color:var(--text)">${_ageStr(info.age_seconds)}</span></div>`
    }
    if (bkp.exists){
      html += `<div style="margin-top:.3rem">Backup: <span style="color:var(--text)">${bkp.size_mb} MB</span> · saved <span style="color:var(--text)">${_ageStr(bkp.age_seconds)}</span></div>`
    } else {
      html += `<div style="margin-top:.3rem;color:var(--text3)">No backup yet</div>`
    }
    el.innerHTML = html
  } catch(e) {}
}

async function backupCache(){
  const res = await api("/api/cache/backup","POST",{})
  if (res.ok){
    toast(`Cache backed up (${res.size_mb} MB)`,"success")
    loadCacheInfo()
  } else {
    toast("Backup failed: " + res.error,"error")
  }
}

async function restoreCache(){
  if (!confirm("Restore cache from backup? Current cache will be overwritten.")) return
  const res = await api("/api/cache/restore","POST",{})
  if (res.ok){
    toast(`Cache restored (${res.size_mb} MB)`,"success")
    loadCacheInfo()
  } else {
    toast("Restore failed: " + res.error,"error")
  }
}

async function clearCache(){
  if (!confirm("Clear the TMDB cache? The next scan will re-fetch all data from TMDB.")) return
  const res = await api("/api/cache/clear","POST",{})
  if (res.ok){
    toast("TMDB cache cleared","success")
    loadCacheInfo()
  } else {
    toast("Failed to clear cache: " + res.error,"error")
  }
}

function renderConfig(){
  const c     = document.getElementById("content")
  const cfg   = CONFIG||{}
  const plex  = cfg.PLEX        ||{}
  const tmdb  = cfg.TMDB        ||{}
  const radarr= cfg.RADARR      ||{}
  const cls   = cfg.CLASSICS    ||{}
  const act   = cfg.ACTOR_HITS  ||{}
  const auto  = cfg.AUTOMATION  ||{}

  const field = (id, label, value, type="text") => `
  <div class="form-group">
    <label class="form-label" for="${id}">${label}</label>
    <input class="form-input" id="${id}" type="${type}" value="${value??""}" />
  </div>`

  c.innerHTML = `
  <div style="max-width:520px">
    <div class="form-section">
      <div class="form-section-title">Plex</div>
      ${field("cfg_plex_url",   "Plex URL",     plex.PLEX_URL    ||"")}
      ${field("cfg_plex_token", "Plex Token",   plex.PLEX_TOKEN  ||"")}
      ${field("cfg_library",    "Library Name", plex.LIBRARY_NAME||"")}
    </div>

    <div class="form-section">
      <div class="form-section-title">TMDB</div>
      ${field("cfg_tmdb_key","TMDB API Key", tmdb.TMDB_API_KEY||"")}
    </div>

    <details class="form-section">
      <summary style="display:flex;align-items:center;justify-content:space-between">
        <span class="form-section-title" style="margin-bottom:0">Advanced Settings</span>
        <svg class="chevron" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--text3)" stroke-width="2"><path d="M6 9l6 6 6-6"/></svg>
      </summary>
      <div style="margin-top:1rem">
        <p style="font-size:.65rem;letter-spacing:.1em;text-transform:uppercase;color:var(--text3);margin-bottom:.75rem">Classics</p>
        ${field("cfg_classics_pages",  "Pages to fetch",    cls.CLASSICS_PAGES      ??4,    "number")}
        ${field("cfg_classics_votes",  "Minimum votes",     cls.CLASSICS_MIN_VOTES  ??5000, "number")}
        ${field("cfg_classics_rating", "Minimum rating",    cls.CLASSICS_MIN_RATING ??8.0,  "number")}
        ${field("cfg_classics_max",    "Max results",       cls.CLASSICS_MAX_RESULTS??120,  "number")}
        <p style="font-size:.65rem;letter-spacing:.1em;text-transform:uppercase;color:var(--text3);margin:1rem 0 .75rem">Actors</p>
        ${field("cfg_actor_votes", "Min votes per film",    act.ACTOR_MIN_VOTES            ??500, "number")}
        ${field("cfg_actor_max",   "Max results per actor", act.ACTOR_MAX_RESULTS_PER_ACTOR??10,  "number")}
        <p style="font-size:.65rem;letter-spacing:.1em;text-transform:uppercase;color:var(--text3);margin:1rem 0 .75rem">TMDB</p>
        ${field("cfg_tmdb_workers","Concurrent workers (1–10)", tmdb.TMDB_WORKERS??6,"number")}
        <p style="font-size:.68rem;color:var(--text3);margin-top:-.25rem;margin-bottom:.5rem">Higher = faster first scan. Default 6, max 10.</p>
        <p style="font-size:.65rem;letter-spacing:.1em;text-transform:uppercase;color:var(--text3);margin:1rem 0 .75rem">Plex Scanner</p>
        ${field("cfg_plex_page_size","Page size",               plex.PLEX_PAGE_SIZE   ??500, "number")}
        ${field("cfg_short_limit",  "Short movie limit (min)", plex.SHORT_MOVIE_LIMIT??60,  "number")}
      </div>
    </details>

    <div class="form-section">
      <div class="form-section-title">Radarr <span style="font-size:.75rem;font-weight:400;color:var(--text3)">(optional)</span></div>
      <div class="form-group" style="display:flex;align-items:center;gap:.6rem">
        <input type="checkbox" id="cfg_radarr_enabled" ${radarr.RADARR_ENABLED?"checked":""}
          style="accent-color:var(--gold);width:14px;height:14px;cursor:pointer"/>
        <label for="cfg_radarr_enabled" class="form-label" style="margin:0;cursor:pointer">Enabled</label>
      </div>
      ${field("cfg_radarr_url",     "Radarr URL",         radarr.RADARR_URL              ||"")}
      ${field("cfg_radarr_key",     "Radarr API Key",     radarr.RADARR_API_KEY          ||"")}
      ${field("cfg_radarr_root",    "Root Folder Path",   radarr.RADARR_ROOT_FOLDER_PATH ||"")}
      ${field("cfg_radarr_quality", "Quality Profile ID", radarr.RADARR_QUALITY_PROFILE_ID??6,"number")}
      <div class="form-group" style="display:flex;align-items:center;gap:.6rem">
        <input type="checkbox" id="cfg_radarr_search" ${radarr.RADARR_SEARCH_ON_ADD?"checked":""}
          style="accent-color:var(--gold);width:14px;height:14px;cursor:pointer"/>
        <label for="cfg_radarr_search" class="form-label" style="margin:0;cursor:pointer">Search &amp; download on add</label>
      </div>
    </div>

    <div class="form-section">
      <div class="form-section-title">Automation</div>
      ${field("cfg_poll_interval","Library poll interval (min, 0 = disabled)", auto.LIBRARY_POLL_INTERVAL??30,"number")}
      <p style="font-size:.68rem;color:var(--text3);margin-top:-.25rem">Cineplete will auto-scan when your Plex library size changes.</p>
    </div>

    <div class="form-section" id="cache-section">
      <div class="form-section-title">TMDB Cache</div>
      <div id="cache-info" style="font-size:.75rem;color:var(--text3);margin-bottom:.75rem">Loading…</div>
      <div style="display:flex;gap:.5rem;flex-wrap:wrap">
        <button class="btn-sm" style="font-size:.72rem;padding:5px 14px;border-color:rgba(34,197,94,.3);color:var(--green)" onclick="backupCache()">💾 Backup</button>
        <button class="btn-sm" style="font-size:.72rem;padding:5px 14px;border-color:rgba(59,130,246,.3);color:var(--blue)" onclick="restoreCache()">↩ Restore</button>
        <button class="btn-sm btn-ignore" style="font-size:.72rem;padding:5px 14px" onclick="clearCache()">🗑 Clear</button>
      </div>
    </div>

    <button class="btn-primary" onclick="saveConfig()">Save Configuration</button>
    <div id="cfgStatus" style="font-size:.75rem;color:var(--text3);margin-top:.6rem;text-align:center"></div>
  </div>`

  loadCacheInfo()
}

async function saveConfig(){
  const v  = id => document.getElementById(id)?.value?.trim()||""
  const vi = id => parseInt(v(id))||0
  const vf = id => parseFloat(v(id))||0

  const payload = {
    PLEX:{
      PLEX_URL:         v("cfg_plex_url"),
      PLEX_TOKEN:       v("cfg_plex_token"),
      LIBRARY_NAME:     v("cfg_library"),
      PLEX_PAGE_SIZE:   vi("cfg_plex_page_size"),
      SHORT_MOVIE_LIMIT:vi("cfg_short_limit"),
    },
    TMDB:{ TMDB_API_KEY: v("cfg_tmdb_key"), TMDB_WORKERS: vi("cfg_tmdb_workers") },
    CLASSICS:{
      CLASSICS_PAGES:      vi("cfg_classics_pages"),
      CLASSICS_MIN_VOTES:  vi("cfg_classics_votes"),
      CLASSICS_MIN_RATING: vf("cfg_classics_rating"),
      CLASSICS_MAX_RESULTS:vi("cfg_classics_max"),
    },
    ACTOR_HITS:{
      ACTOR_MIN_VOTES:             vi("cfg_actor_votes"),
      ACTOR_MAX_RESULTS_PER_ACTOR: vi("cfg_actor_max"),
    },
    RADARR:{
      RADARR_ENABLED:           document.getElementById("cfg_radarr_enabled")?.checked||false,
      RADARR_URL:               v("cfg_radarr_url"),
      RADARR_API_KEY:           v("cfg_radarr_key"),
      RADARR_ROOT_FOLDER_PATH:  v("cfg_radarr_root"),
      RADARR_QUALITY_PROFILE_ID:vi("cfg_radarr_quality"),
      RADARR_SEARCH_ON_ADD:     document.getElementById("cfg_radarr_search")?.checked||false,
    },
    AUTOMATION:{
      LIBRARY_POLL_INTERVAL: vi("cfg_poll_interval"),
    },
  }

  const res = await api("/api/config","POST",payload)
  const st  = document.getElementById("cfgStatus")
  if (res.ok){
    st.textContent = "✓ Saved"
    st.style.color = "var(--green)"
    toast("Configuration saved","success")
    if (res.configured){
      CONFIGURED = true
      CONFIG     = await api("/api/config")
      await loadResults()
    }
  } else {
    st.textContent = "✗ Error saving"
    st.style.color = "var(--red)"
    toast("Error saving config","error")
  }
}