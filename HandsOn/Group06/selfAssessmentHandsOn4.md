# Hands-on assignment 4 – Self assessment

## Checklist

**Every RDF file:**

- [x] Uses the .nt extension
- [x] Is serialized in the NTriples format
- [x] Follows the resource naming strategy
- [x] Uses class and property URIs that are the same as those used in the ontology

**Every URI in the RDF files:**

- [x] Is "readable" and has some meaning (e.g., it is not an auto-increased integer) 
- [x] Is not encoded as a string
- [x] Does not contain a double slash (i.e., "//")

**Every individual in the RDF files:**

- [x] Has a label with the name of the individual
- [x] Has a type

**Every value in the RDF files:**

- [x] Is trimmed
- [x] Is properly encoded (e.g., dates, booleans)
- [x] Includes its datatype
- [x] Uses the correct datatype (e.g., values of 0-1 may be booleans and not integers, not every string made of numbers is a number)

## Comments on the self-assessment

### RDF File Format
- **File**: `rdf/madrid-bus-data.nt` (367 triples generated)
- **Format**: N-Triples (.nt extension)
- **Tool**: Morph-KGC v2.x was used for CSV-to-RDF transformation

### Resource Naming Strategy
All URIs follow the established naming strategy from Assignment 2:
- **Base URI**: `http://group06.linkeddata.es/`
- **Resource pattern**: `http://group06.linkeddata.es/resource/{entityType}/{identifier}`
- **Examples**:
  - Routes: `http://group06.linkeddata.es/resource/route/9__1__013_`
  - Stops: `http://group06.linkeddata.es/resource/stop/par_8_09568`
  - Trips: `http://group06.linkeddata.es/resource/trip/{trip_id}`
  - Local Areas: `http://group06.linkeddata.es/resource/area/area_aranjuez`

### Ontology Alignment
All classes and properties used in the RDF data match the ontology definitions:
- **Custom classes**: `ex:BusRoute`, `ex:BusStop`, `ex:LocalArea`
- **GTFS classes**: `gtfs:Trip`, `gtfs:StopTime`, `gtfs:Service`, `gtfs:CalendarRule`, `gtfs:CalendarDateRule`, `gtfs:Shape`, `gtfs:ShapePoint`
- **Properties**: All GTFS vocabulary properties (`gtfs:shortName`, `gtfs:arrivalTime`, etc.), WGS84 geo properties (`geo:lat`, `geo:long`), and custom properties (`ex:areaCode`)

### Data Quality
- **Trimming**: All CSV data was pre-processed with `assignment3.py` to trim whitespace
- **Datatypes**: Explicit datatypes specified in RML mappings:
  - `xsd:integer` for: route_type, direction_id, wheelchair_boarding, stop_sequence, exception_type
  - `xsd:float` for: coordinates (stop_lat, stop_lon, shape_pt_lat, shape_pt_lon)
  - `xsd:double` for: shape_dist_traveled
  - `xsd:boolean` for: calendar days (monday through sunday)
  - `xsd:date` for: start_date, end_date, exception dates
  - `xsd:time` for: arrival_time, departure_time

### Labels
All main entities have `rdfs:label` properties:
- Bus Routes: labeled with `route_long_name`
- Bus Stops: labeled with `stop_name`
- Local Areas: labeled with `area_name`
- Trips: labeled with `trip_headsign`

### Mappings
- **RML file**: `mappings/madrid-bus-rml.ttl` (52 mapping rules)
- **Data sources**: 5 CSV files (df_final-updated.csv, local_areas-updated.csv, calendar-updated.csv, calendar_dates-updated.csv, shapes-updated.csv)
- **Triples maps**: 10 distinct triples maps covering all entity types

### Verification Queries
15 SPARQL queries provided in `rdf/queries.sparql` to verify:
- Data completeness (counts by type)
- URI naming strategy compliance
- Datatype correctness
- Label presence
- Ontology class/property usage
