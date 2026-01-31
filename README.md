# ADM_Project - FAIRTransit Hub
Public dataset catalog (GitHub Pages): https://lorenzodiaz2.github.io/ADM_Project/

Minimal GTFS data hub with:
- HTML pages for humans: dataset catalog, feed detail, stop search, route list
- JSON API endpoints with the same data

Scope:
- 2 GTFS feeds: Roma and Milano
- agency.txt, stops.txt, routes.txt (plus trips/stop_times present in DB but not required by scope)

## Requirements
- Python 3.11+ (recommended)
- Django 5.x
- SQLite (default)

## Setup (first time)
1) Create venv and install deps
   - Use PyCharm venv OR run in terminal:

pip install "Django>=5,<6"

2) Apply migrations

python manage.py makemigrations
python manage.py migrate

3) Create admin user

python manage.py createsuperuser

## Import GTFS data
GTFS zip files are stored in:
- data/raw/milan_gtfs.zip
- data/raw/rome_static_gtfs.zip

Run imports:

python manage.py import_gtfs data/raw/milan_gtfs.zip --feed Milano --limit-stop-times 20000
python manage.py import_gtfs data/raw/rome_static_gtfs.zip --feed Roma --limit-stop-times 20000

Notes:
- limit-stop-times is optional. Use 0 to import all stop_times (can be large).
- Feed slugs used in URLs:
  - Roma -> roma
  - Milano -> milano

## Run the server
Start dev server:

python manage.py runserver

Open:
http://127.0.0.1:8000/

Admin:
http://127.0.0.1:8000/admin/

## HTML Pages (human-facing)
Catalog (list feeds):
http://127.0.0.1:8000/catalog/

Feed detail (counts):
http://127.0.0.1:8000/catalog/roma/
http://127.0.0.1:8000/catalog/milano/

Stop search (select city + query):
http://127.0.0.1:8000/stops/search/
Example:
http://127.0.0.1:8000/stops/search/?feed=roma&q=termini

Route list (select city):
http://127.0.0.1:8000/routes/
Example:
http://127.0.0.1:8000/routes/?feed=milano

## JSON API (program-facing)
Catalog:
http://127.0.0.1:8000/api/catalog/

Feed detail:
http://127.0.0.1:8000/api/catalog/roma/
http://127.0.0.1:8000/api/catalog/milano/

Stop search:
http://127.0.0.1:8000/api/stops/search/?feed=roma&q=termini

Route list:
http://127.0.0.1:8000/api/routes/?feed=milano

## Data Model Notes (IDs)
- Internal primary keys are Django auto-increment IDs.
- External identifiers come from GTFS files (stop_id, route_id, etc.)
- External IDs are unique per feed via UNIQUE(feed, gtfs_id).
- For API/LOD, we can build combined external IDs like:
  feed_slug + ":" + gtfs_id
Example: "roma:1234"


## Persistent Identifier
BASE URL = https://lorenzodiaz2.github.io/ADM_Project/

Dataset:\
https://lorenzodiaz2.github.io/ADM_Project/dataset/roma/ \
https://lorenzodiaz2.github.io/ADM_Project/dataset/milano/


Stop (template links):\
https://lorenzodiaz2.github.io/ADM_Project/id/stop/roma:{stop_gtfs_id}  \
https://lorenzodiaz2.github.io/ADM_Project/id/stop/milano:{stop_gtfs_id}


Route (template links):\
https://lorenzodiaz2.github.io/ADM_Project/id/route/roma:{route_gtfs_id} \
https://lorenzodiaz2.github.io/ADM_Project/id/route/milano:{route_gtfs_id}



## Accessibility notes (dev vs production)
All resources are retrievable via HTTPS (GitHub Pages) and HTTP/HTTPS (Django API). No authentication is required.

Note: API URLs in this README (127.0.0.1) and in JSON-LD distributions refer to the local development server.
In a production deployment, set PUBLIC_API_BASE_URL to a public domain so that API distributions become globally resolvable.



## Interoperability (JSON-LD vocabularies)
* Metadata endpoints:
  * /api/catalog.jsonld
  * /api/catalog/roma.jsonld
  * /api/catalog/milano.jsonld

* Vocabularies:
  * DCAT, DCTERMS, PROV-O, FOAF
* Metadata profile:
  * [https://lorenzodiaz2.github.io/ADM_Project/metadata-profile](https://lorenzodiaz2.github.io/ADM_Project/metadata-profile)


## Licensing
- Code: MIT License (see LICENSE file in this repository).
- Datasets (Roma/Milano GTFS): licenses are defined by the original providers and are referenced in each dataset landing page and JSON-LD metadata.
  This project republishes metadata and provides an access API for demonstration; it does not modify or override the original dataset licenses.
