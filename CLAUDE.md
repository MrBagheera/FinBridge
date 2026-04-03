# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview (Generated)

### Overview
FinBridge syncs investment positions from Saxo Bank to a Google Sheet via their respective APIs. It handles OAuth2 authentication with Saxo, fetches current positions and cash balance, and updates a designated section of a spreadsheet — adding new rows, updating existing ones, and removing stale entries.

### Stack
- **Language**: Python 3.11+
- **Package management**: `uv` with `hatchling` build backend (src layout)
- **Saxo Bank API**: `saxo-openapi`
- **Google Sheets**: `gspread`, `google-auth`, `google-auth-oauthlib`
- **OAuth2 flow**: `flask` (local webhook server on port 5050), `requests-oauthlib`
- **PDF extraction** (secondary utility): `pandas`, `tabula-py`

### Structure
- `src/finbridge/` — all source code
- `pyproject.toml` — project metadata, dependencies, CLI entry points
- `uv.lock` — locked dependencies
- `*.json` (gitignored) — runtime config files (e.g. `live.json`, `sim.json`)
- `~/.config/fin_bridge.json` — cached OAuth tokens (written at runtime)

### Documentation
See `README.md` for full usage instructions.

**Install:**
```bash
uv sync
```

**Run:**
```bash
finbridge <config.json>          # sync Saxo positions → Google Sheet
finbridge-export <file.pdf>      # extract tables from PDF to CSV
```

Config JSON must contain:
- `saxo_app`: `AppKey`, `AppSecret`, `OpenApiBaseUrl`, `TokenEndpoint`, `AuthorizationEndpoint`, `RedirectUrl`
- `google_sheets`: `sheet_name`, `worksheet_name`, `section_name`, `throttle_delay`
- `debug` (optional): boolean

No test suite is present.

---

## User-Provided Instructions

_This section is for your own notes and instructions to Claude. Edit it freely._