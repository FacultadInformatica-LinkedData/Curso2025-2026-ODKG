from rdflib import Graph

# Cargar tu TTL
g = Graph()
g.parse("results.ttl", format="turtle")

# Consulta SPARQL: todos los Bares con su nombre y dirección
query = """
PREFIX ns: <http://www.barnabikes.org/ODKG/handsOn/group10/>

SELECT ?addressName (COUNT(?station) AS ?numStations)
WHERE {
  ?station a ns:BikingStation ;
           ns:hasAddress ?addr .
  ?addr ns:addressName ?addressName .
}
GROUP BY ?addressName
HAVING (COUNT(?station) > 3)
ORDER BY DESC(?numStations)


"""

# Ejecutar consulta
for row in g.query(query):
    print(row)