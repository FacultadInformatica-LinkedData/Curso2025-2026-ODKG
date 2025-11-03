from rdflib import Graph

# Cargar tu TTL
g = Graph()
g.parse("transformed-data-with-links.ttl", format="turtle")

query1= """
  PREFIX ns: <http://www.barnabikes.org/ODKG/handsOn/group10/>

  SELECT ?bar ?barName
  WHERE {
    ?bar a ns:Bar ;
        ns:barName ?barName ;
        ns:hasAddress ?addr .
        
    ?addr ns:hasNeighborhood ?neigh .
    ?neigh ns:hasDistrict ?district .
    ?district ns:districtId 10 .
  }
"""
query2 = """
  PREFIX ns: <http://www.barnabikes.org/ODKG/handsOn/group10/>


  SELECT (COUNT(?station) AS ?numStations)
  WHERE {
    ?station a ns:BikingStation ;
            ns:hasAddress ?addr .
            
    ?addr ns:hasNeighborhood ?neigh .
    ?neigh ns:hasDistrict ?district .
    ?district ns:districtId 6 .
  }


"""

query3 = """
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

query4 = """
PREFIX ns: <http://www.barnabikes.org/ODKG/handsOn/group10/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT ?district ?wikidataLink
WHERE {
  ?district a ns:District ;
            owl:sameAs ?wikidataLink .
}
"""

# Ejecutar consulta
for query in [query1, query2, query3, query4]:
  for row in g.query(query):
      print(row)