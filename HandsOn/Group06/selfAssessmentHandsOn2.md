# Hands-on assignment 2 – Self assessment

## Checklist

**The “analysis.html” file:**

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
- [X] Contains at least one class (`ex:Guess`)  
- [X] Contains at least one object property (`ex:madeBy`)  
- [X] Contains at least one datatype property (`ex:guessedArrivalTime`)  
- [X] Defines domains and ranges for all properties  
- [X] All class names start with a capital letter  
- [X] All property names start with a non-capital letter  
- [X] Labels and comments are in English only  
- [X] No properties define multiple domains or ranges  
- [X] Contains a linking class (`ex:Guess`) that connects users, stops, and routes  

**The sample instantiation file (`ontology/ontology-example.ttl`):**

- [X] Uses the `.ttl` extension and Turtle syntax  
- [X] Follows the resource naming strategy  
- [X] Does not redefine ontology terms  
- [X] Includes at least one instance for each major class (User, Route, Stop, Trip, StopTime, Guess)  
- [X] Provides realistic data from the Madrid transportation system (route 94022H1 from CRTM schedule PDF)  

## Comments on the self-assessment

The ontology reuses existing vocabularies (GTFS, FOAF, DCTERMS) and introduces minimal extensions for the “guessing” functionality.  
The resource naming strategy separates ontology resources under  
`http://group06.linkeddata.es/ontology/` and individual data under  
`http://group06.linkeddata.es/resource/`, following good Linked Data practices.