# Dataset: Roma (GTFS static)
Back to catalog: [catalog](https://lorenzodiaz2.github.io/ADM_Project/)

Identifier:
- [https://lorenzodiaz2.github.io/ADM_Project/dataset/roma/](https://lorenzodiaz2.github.io/ADM_Project/dataset/roma/)

Source:
- [https://www.dati.gov.it/view-dataset/dataset?id=5bb208ed-e7ce-48c7-afc4-bf8dd15ea6fc](https://www.dati.gov.it/view-dataset/dataset?id=5bb208ed-e7ce-48c7-afc4-bf8dd15ea6fc)

Downloaded:
- 2026-01-22

Local file:
- data/raw/rome_static_gtfs.zip

License:
- CC BY 4.0 [https://creativecommons.org/licenses/by/4.0/](https://creativecommons.org/licenses/by/4.0/)
- The usage license is defined by the original data provider and is referenced by the dataset metadata (see the official source page).
- This project republishes metadata and provides a demonstration access API; it does not modify or override the original license.


Publisher / editor:
- Roma Servizi per la Mobilita

Geographic coverage:
- Roma

Refresh rate:
- daily

Notes:
- GTFS static feed

Distributions:
- Local API (dev): [http://127.0.0.1:8000/api/catalog/roma/](http://127.0.0.1:8000/api/catalog/roma/)


### Reuse and scope

- This dataset is published as GTFS Static (Schedule), i.e., CSV tables packaged as a ZIP archive, following the community standard GTFS schedule specification.

### Imported scope in this project (demo subset):

- GTFS files: agency.txt, stops.txt, routes.txt
- Database tables populated: Agency, Stop, Route (for the Roma feed)

### Out of scope (not imported / not served by this demo):
- trips.txt, stop_times.txt, calendar.txt, calendar_dates.txt
- GTFS-Realtime (delays/vehicle positions)
- routing / journey planning / maps


### Provenance and versioning

Provenance is declared using qualified references:
- Source (provenance): see the official source page linked in the metadata (prov:wasDerivedFrom / derivedFrom).
- Import timestamp: available in the JSON-LD metadata as dct:modified.
- Integrity/version: the latest imported ZIP checksum (SHA256) is reported in the JSON-LD metadata.

### Access (distributions)

Machine-readable metadata (JSON-LD):
- [http://127.0.0.1:8000/api/catalog/roma.jsonld](http://127.0.0.1:8000/api/catalog/roma.jsonld)

Metadata (JSON API):
- [http://127.0.0.1:8000/api/catalog/roma/](http://127.0.0.1:8000/api/catalog/roma/)

Routes list (JSON API):
- [http://127.0.0.1:8000/api/routes/?feed=roma](http://127.0.0.1:8000/api/routes/?feed=roma)

Stop search (JSON API):
- [http://127.0.0.1:8000/api/stops/search/?feed=roma&q=TERM](http://127.0.0.1:8000/api/stops/search/?feed=roma&q=TERM)

Human-readable landing page (persistent identifier):
- [https://lorenzodiaz2.github.io/ADM_Project/dataset/roma/](https://lorenzodiaz2.github.io/ADM_Project/dataset/roma/)