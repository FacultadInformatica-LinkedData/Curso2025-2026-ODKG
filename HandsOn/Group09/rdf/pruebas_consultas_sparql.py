from rdflib import Graph

g = Graph()
g.parse("C:/Users/paula/Desktop/Master/Primer_cuatri/Open Data and Knowledge Graphs/Curso2025-2026-ODKG/HandsOn/Group09/rdf/microclimate-sensors-data-enriched-updated-with-links.ttl", format="ttl")

q = """
PREFIX sosa: <http://www.w3.org/ns/sosa/>
PREFIX schema: <http://schema.org/>
PREFIX us: <https://smartcity.linkeddata.es/lcc/ontology/urban-sensors#>
PREFIX wgs84_pos: <http://www.w3.org/2003/01/geo/wgs84_pos#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?loc ?lat ?long ?city
WHERE {
  ?loc a us:Location ;
       wgs84_pos:lat ?lat ;
       wgs84_pos:long ?long ;
       schema:addressLocality ?city .
}
LIMIT 5
"""

for row in g.query(q):
    print(row)
