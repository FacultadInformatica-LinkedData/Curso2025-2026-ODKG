from rdflib import Graph

g = Graph()
g.parse("C:/Users/paula/Desktop/Master/Primer_cuatri/Open Data and Knowledge Graphs/Curso2025-2026-ODKG/HandsOn/Group09/rdf/pedestrian-counting-system-sensor-locations-enriched-updated.ttl", format="ttl")

q = """
PREFIX wgs84_pos: <http://www.w3.org/2003/01/geo/wgs84_pos#>
PREFIX us: <https://smartcity.linkeddata.es/lcc/ontology/urban-sensors#>

SELECT ?location ?lat ?long
WHERE {
  ?location a us:Location ;
            wgs84_pos:lat ?lat ;
            wgs84_pos:long ?long .
}
LIMIT 5
"""

for row in g.query(q):
    print(row)
