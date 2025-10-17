# Hands-on assignment 2 – Self assessment

## Checklist

**The "analysis.html" file:**

- [X] Includes the analyses performed over the data source  
- [X] Includes the licensing of the data source and the potential license of the generated dataset  
- [X] Includes the resource naming strategy  
- [X] The resource naming strategy uses a domain that is not the one given by default in Protégé  
- [X] The strategy defines different paths for ontology resources and individuals  
- [X] The strategy ensures that individuals of different classes have distinct paths  
- [X] The strategy defines property URIs independently of class URIs  

**The ontology file (`ontology/ontology.ttl`):**

- [X] Uses the `.ttl` extension and Turtle syntax  
- [X] Follows the resource naming strategy  
- [X] Contains at least one class (`ex:LinkedPlace`)  
- [X] Contains at least one object property (`ex:nearbyPlace`)  
- [X] Contains at least one datatype property (`ex:wikidataUri`, `ex:distanceMeters`)  
- [X] Defines domains and ranges for all properties  
- [X] All class names start with a capital letter  
- [X] All property names start with a non-capital letter  
- [X] Labels and comments are in English only  
- [X] No properties define multiple domains or ranges  
- [X] Contains a linking class (`ex:LinkedPlace`) that connects stops to Wikidata entities  

**The sample instantiation file (`ontology/ontology-example.ttl`):**

- [X] Uses the `.ttl` extension and Turtle syntax  
- [X] Follows the resource naming strategy  
- [X] Does not redefine ontology terms  
- [X] Includes at least one instance for each major class (Route, Stop, Trip, StopTime, LinkedPlace)  
- [X] Provides realistic data from the Madrid transportation system (actual GTFS data from CRTM)  

## Comments on the self-assessment

The ontology reuses standard vocabularies, adds only the minimal extensions (`ex:LinkedPlace`, `ex:nearbyPlace`, `ex:wikidataUri`, `ex:distanceMeters`), separates ontology and data URIs.
