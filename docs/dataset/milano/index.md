# Dataset: Milano (GTFS static)
Back to catalog: [catalog](https://lorenzodiaz2.github.io/ADM_Project/)

Identifier:
- [https://lorenzodiaz2.github.io/ADM_Project/dataset/milano/](https://lorenzodiaz2.github.io/ADM_Project/dataset/milano/)

Source:
- [https://www.amat-mi.it/it/servizi/pubblicazione-orari-trasporto-pubblico-locale-formato-gtfs/](https://www.amat-mi.it/it/servizi/pubblicazione-orari-trasporto-pubblico-locale-formato-gtfs/)

Downloaded:
- 2026-01-22

Local file:
- data/raw/milan_gtfs.zip

License:
- CC BY 4.0 [https://creativecommons.org/licenses/by/4.0/](https://creativecommons.org/licenses/by/4.0/)
- The usage license is defined by the original data provider and is referenced by the dataset metadata (see the official source page).
- This project republishes metadata and provides a demonstration access API; it does not modify or override the original license.

Publisher / editor:
- Direzione Mobilita, Ambiente e Energia

Geographic coverage:
- Milano

Refresh rate:
- fortnightly

Notes:
- GTFS feed; includes extra files not used in core import

Distributions:
- Local API (dev): [http://127.0.0.1:8000/api/catalog/milano/](http://127.0.0.1:8000/api/catalog/milano/)

### Reuse and scope

This dataset is published as GTFS Static (Schedule), i.e., CSV tables packaged as a ZIP archive, following the community standard GTFS schedule specification.
- Imported scope in this project (demo subset):
- GTFS files: agency.txt, stops.txt, routes.txt
- Database tables populated: Agency, Stop, Route (for the Milano feed)

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
- [http://127.0.0.1:8000/api/catalog/milano.jsonld](http://127.0.0.1:8000/api/catalog/milano.jsonld)

Metadata (JSON API):
- [http://127.0.0.1:8000/api/catalog/milano/](http://127.0.0.1:8000/api/catalog/milano/)

Routes list (JSON API):
- [http://127.0.0.1:8000/api/routes/?feed=milano](http://127.0.0.1:8000/api/routes/?feed=milano)

Stop search (JSON API):
- [http://127.0.0.1:8000/api/stops/search/?feed=milano&q=TERM](http://127.0.0.1:8000/api/stops/search/?feed=milano&q=TERM)

Human-readable landing page (persistent identifier):
- [https://lorenzodiaz2.github.io/ADM_Project/dataset/milano/](https://lorenzodiaz2.github.io/ADM_Project/dataset/milano/)
