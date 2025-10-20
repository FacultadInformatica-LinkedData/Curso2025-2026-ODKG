from rdflib import Graph

g = Graph()
g.parse("microclimate-sensors-data-enriched-updated.ttl", format="ttl")

q = """
SELECT ?sensor
WHERE {
  ?sensor a us:MicroclimateSensor .
}
"""

results = g.query(q)
for row in results:
    print(row)
