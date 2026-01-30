# “ADM_Project Metadata Profile (JSON-LD)”
### Vocabularies used
  * [DCAT](https://www.w3.org/TR/vocab-dcat-3/): per Catalog, Dataset, Distribution
  * [DCTERMS](https://www.dublincore.org/specifications/dublin-core/dcmi-terms/): title, description, identifier, license, publisher, modified
  * [PROV-O](https://www.w3.org/TR/prov-o/): wasDerivedFrom (provenance)
  * [FOAF](https://xmlns.com/foaf/spec/): name (publisher name)

### Field mapping
  * Dataset identifier -> dct:identifier and @id
  * Dataset title -> dct:title
  * Dataset description -> dct:description
  * Landing page -> dcat:landingPage
  * License -> dct:license
  * Publisher -> dct:publisher (foaf:Agent con foaf:name)
  * Provenance/source -> prov:wasDerivedFrom
  * Distributions -> dcat:distribution (con dcat:accessURL)