#task07.py
# **Task 07: Querying RDF(s)**


#!pip install rdflib
import urllib.request
url = 'https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/refs/heads/master/Assignment4/course_materials/python/validation.py'
urllib.request.urlretrieve(url, 'validation.py')
github_storage = "https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/master/Assignment4/course_materials"


from validation import Report

from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS
# Do not change the name of the variables
g = Graph()
g.namespace_manager.bind('ns', Namespace("http://somewhere#"), override=False)
g.parse(github_storage+"/rdf/data06.ttl", format="TTL")
report = Report()

# TASK 7.1a 
result = []

classes = set(g.subjects(RDF.type, RDFS.Class))

for c in sorted(classes, key=lambda x: str(x)):
    supercs = list(g.objects(c, RDFS.subClassOf))
    if supercs:
        for sc in supercs:
            result.append((c, sc))
    else:
        result.append((c, None))
        
# Visualize the results
for r in result:
  print(r)

## Validation: Do not remove
report.validate_07_1a(result)

# TASK 7.1b
query = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?c ?sc
WHERE {
  ?c a rdfs:Class .
  OPTIONAL { ?c rdfs:subClassOf ?sc }
  BIND(STR(COALESCE(?sc, "")) AS ?scs)
}
ORDER BY STR(?c) ?scs
"""

for r in g.query(query):
  print(r.c, r.sc)


## Validation: Do not remove
report.validate_07_1b(query,g)

# TASK 7.2a
ns = Namespace("http://oeg.fi.upm.es/def/people#")

# trova tutte le sottoclassi (chiusura transitiva) di ns:Person
to_visit = {ns.Person}
all_types = set()

while to_visit:
    t = to_visit.pop()
    if t in all_types:
        continue
    all_types.add(t)
    # aggiungi le sottoclassi dirette di t
    for sub in g.subjects(RDFS.subClassOf, t):
        to_visit.add(sub)

# raccogli gli individui tipizzati come una delle classi trovate
individuals = []
for t in all_types:
    for ind in g.subjects(RDF.type, t):
        individuals.append(ind)

# rimuovi duplicati mantenendo ordine deterministico
individuals = sorted(set(individuals), key=lambda x: str(x))

# visualize results
for i in individuals:
  print(i)

# validation. Do not remove
report.validate_07_02a(individuals)

# TASK 7.2b
query = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ns:   <http://oeg.fi.upm.es/def/people#>
SELECT ?ind
WHERE {
  ?ind a ?t .
  ?t rdfs:subClassOf* ns:Person .
}
ORDER BY STR(?ind)
"""

for r in g.query(query):
  print(r.ind)
# Visualize the results

## Validation: Do not remove
report.validate_07_02b(g, query)

# Task 7.3
query = """
PREFIX : <http://oeg.fi.upm.es/def/people#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?name ?type WHERE {
  ?entity :knows :Rocky .
  ?entity rdfs:label ?name .
  ?entity a ?type .
}
"""
# Visualize the results
for r in g.query(query):
  print(r.name, r.type)

## Validation: Do not remove
report.validate_07_03(g, query)

# Task 7.4
query = """
PREFIX : <http://oeg.fi.upm.es/def/people#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?name WHERE {
  {
    ?person :hasColleague ?colleague .
    ?colleague :ownsPet ?pet .
    ?pet a :Animal .
  }
  UNION
  {
    ?person :hasColleague ?colleague .
    ?colleague :hasColleague ?colleague2 .
    ?colleague2 :ownsPet ?pet2 .
    ?pet2 a :Animal .
  }
  ?person rdfs:label ?name .
}
"""
for r in g.query(query):
  print(r.name)

## Validation: Do not remove
report.validate_07_04(g,query)
report.save_report("_Task_07")


