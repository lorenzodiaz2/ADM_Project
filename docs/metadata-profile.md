* Titolo: “ADM_Project Metadata Profile (JSON-LD)”
* Sezione “Vocabularies used”
  * DCAT: per Catalog, Dataset, Distribution
  * DCTERMS: title, description, identifier, license, publisher, modified
  * PROV-O: wasDerivedFrom (provenance)
  * FOAF: name (publisher name)

* Sezione “Field mapping”
  * Dataset identifier -> dct:identifier and @id
  * Dataset title -> dct:title
  * Dataset description -> dct:description
  * Landing page -> dcat:landingPage
  * License -> dct:license
  * Publisher -> dct:publisher (foaf:Agent con foaf:name)
  * Provenance/source -> prov:wasDerivedFrom
  * Distributions -> dcat:distribution (con dcat:accessURL)