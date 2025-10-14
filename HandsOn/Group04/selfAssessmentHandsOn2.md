# Self-assessment Hands-On 2 — Group04

Group members: Group04

Assignment: Group Hands-on Assignment 2 — Linked Data generation

1. Analyse Data Set

- Datasets used: `csv/zones.csv`, `csv/flux_daily_mov.csv`.
- We inspected columns and data ranges, identified missing coordinates for some zones, and chose to include only positive flows in the sample instantiation.

2. Analyse Licensing of the Data Source

- Suggested licence: CC BY 4.0. We include provenance triples (prov:wasDerivedFrom) referencing the original CSV files and the repository as the source.

3. Define Resource Naming Strategy

- Base URI: `https://data.example.org/odkg/group04/`
- Zone URIs: `https://data.example.org/odkg/group04/zone/{zone_id}`
- Flow URIs: `https://data.example.org/odkg/group04/flow/{date}/{origin_zone_id}/{dest_zone_id}`

4. Develop Ontology

- We created a lightweight ontology `ontology/group04-ontology.ttl` including classes `ex:Zone` and `ex:Flow` and properties `ex:hasOrigin`, `ex:hasDestination`, `ex:trips`, `ex:date`, `ex:zoneId`, `ex:zoneName`, `geo:lat`, `geo:long`.

Files delivered in the `HandsOn/Group04` directory:

- `analysis.html` — analysis, licensing and naming strategy (this file)
- `ontology/group04-ontology.ttl` — ontology definition
- `ontology/group04-example.ttl` — example RDF instantiation
- `selfAssessmentHandsOn2.md` — this self-assessment
