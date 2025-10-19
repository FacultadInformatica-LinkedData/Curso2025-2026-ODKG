# Hands-on assignment 2 – Self assessment

## Checklist

**The "analysis.html" file:**

- [X] Includes the potential license of the dataset to be generated
- [X] Includes the resource naming strategy

**The resource naming strategy:**

- [X] Uses a domain that is not the one given by default in Protégé
- [X] Uses different paths for ontology resources (i.e., classes and properties) and individuals
- [X] Ensures that the paths for individuals of different classes are not the same
- [X] Defines individual URIs independently of class URIs

**The ontology file:**

- [X] Uses the .ttl extension
- [X] Is serialized in the Turtle format
- [X] Follows the resource naming strategy
- [X] Contains at least one class
- [X] Contains at least one object property (where the value of the property is a resource)
- [X] Contains at least one datatype property (where the value of the property is a string literal, usually typed)
- [X] Defines the domain of all the properties (the origin of the property)
- [X] Defines the range of all the properties (the destination of the property)
- [X] Defines all class names starting with a capital letter
- [X] Defines all property names starting with a non-capital letter
- [X] Does not mix labels in different languages (e.g., Spanish and English)
- [X] Does not define multiple domains or multiple ranges in properties
- [X] Contains at least one class that will be used to link to other entities

## Comments on the self-assessment

The **Madrid Bus Network Ontology** extends the GTFS vocabulary with minimal bus-specific additions:

**Classes (3):**
- `ex:BusRoute` — Specialization of `gtfs:Route` for bus services (route_type = 3)
- `ex:BusStop` — Specialization of `gtfs:Stop` for physical bus stop locations
- `ex:LocalArea` — Geographic areas (neighborhoods, districts) linked to DBpedia via `owl:sameAs`

**Properties (3):**
- `ex:areaCode` (Datatype Property) — Short alphanumeric code for local area identification (domain: `ex:LocalArea`, range: `xsd:string`)
- `ex:locatedInArea` (Object Property) — Links bus stops to their geographic area (domain: `ex:BusStop`, range: `ex:LocalArea`)
- `ex:containsStop` (Object Property) — Inverse of `ex:locatedInArea` (domain: `ex:LocalArea`, range: `ex:BusStop`)

**Design Features:**
- All three classes are mutually disjoint (preventing logical contradictions)
- Object properties are explicitly declared as inverses (enabling bidirectional queries)
- All labels and comments are in English only (no language mixing)
- Reuses standard vocabularies: GTFS, WGS84, Schema.org, DBpedia Ontology, Dublin Core
- URI strategy: `/ontology/madridbus/` for ontology terms, `/resource/` for data instances
- `ex:LocalArea` serves as the linking class, using `owl:sameAs` to connect to DBpedia entities

**Validation:**
The ontology has been validated with OOPS! (Ontology Pitfall Scanner). All critical and important pitfalls have been resolved. Minor warnings (P08) remain only for external vocabulary elements, which is expected and acceptable behavior.
