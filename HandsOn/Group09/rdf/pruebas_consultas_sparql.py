from rdflib import Graph

g = Graph()
g.parse("microclimate-sensors-data-enriched-updated.ttl", format="ttl")

q = """
PREFIX us: <https://smartcity.linkeddata.es/lcc/ontology/urban-sensors#>

SELECT ?sensor
WHERE {
  ?sensor a us:MicroclimateSensor .
}
"""

results = g.query(q)
for row in results:
    print(row)
