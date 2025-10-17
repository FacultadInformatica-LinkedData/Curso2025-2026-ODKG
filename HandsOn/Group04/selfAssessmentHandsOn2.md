# Self-assessment HandsOn 2 — AS2-G4

## Tasks completed
- [x] Analyse Data Set: structure, volumes, temporal coverage, schemas (OD matrices, trips per person, zones).  
- [x] Analyse Licensing: identified publisher (MITMS) and the ministry Open Data License (LDA). Proposed license options for derived data (MITMS LDA, ODbL or CC BY 4.0 depending on constraints).  
- [x] Define Resource Naming Strategy: provided base namespaces, URI patterns, content negotiation recommendations, and metadata requirements (dcterms:license, dcterms:provenance).  
- [x] Develop Ontology: created a lightweight OWL/Turtle ontology (ontology/pyspainmobility-ontology.ttl) with classes, properties and domain/range notes.  
- [x] Sample instantiation: created a small, synthetic RDF example (ontology/pyspainmobility-example.ttl) that follows the naming strategy.

## What I learned
- How the Spanish Ministry publishes mobility data and the differences between the two versions (2020–2021 vs 2022+).
- Practical mapping of tabular OD and trips-per-person records to RDF triples.
- Considerations for licensing when transforming government-published datasets into Linked Data.

## Limitations & next steps
- The example file is intentionally small and synthetic to avoid redistributing raw ministry data. For a full conversion: build a robust ETL that maps each Parquet/CSV field to RDF using the ontology and include provenance & licensing metadata.
- Host the ontology and data on an HTTP server with content negotiation and persistent URIs (replace `ccsi923.github.io/Curso2025-2026-ODKG` placeholders).
- Confirm final license choice with course instructors / institutional legal office if the derived data will be published.

Prepared by AS2-G4.
