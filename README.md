# Profile App

A small Flask app for creating and managing user profiles — name, photo and bio — with a clean, responsive UI that adapts to light and dark mode.

## Features

- Create, view, edit and delete profiles
- Image upload with extension whitelist (`png`, `jpg`, `jpeg`, `gif`, `webp`) and a 4 MB limit
- Gradient letter avatars when no photo is uploaded
- SQLite storage, no external services
- Automatic dark mode, responsive down to mobile

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000 — the database is created on first run.

## Routes

| Route | Method | Description |
| --- | --- | --- |
| `/` | GET | List all profiles |
| `/new` | GET, POST | Create a profile |
| `/profile/<id>` | GET | View a profile |
| `/profile/<id>/edit` | GET, POST | Update a profile |
| `/profile/<id>/delete` | POST | Delete a profile and its photo |

## Structure

```
app.py               routes, SQLite access, upload handling
templates/           base, index, form, profile
static/style.css     design tokens, layout, dark mode
static/uploads/      uploaded photos (gitignored)
```

## Notes

Uploaded files are stored on disk under `static/uploads/` with a UUID prefix. `profiles.db` and uploads are gitignored. For production use, put a real WSGI server in front of it and turn off `debug`.
