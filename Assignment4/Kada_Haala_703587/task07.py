import urllib.request
url = 'https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/refs/heads/master/Assignment4/course_materials/python/validation.py'
urllib.request.urlretrieve(url, 'validation.py')
github_storage = "https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/master/Assignment4/course_materials"

from validation import Report

from rdflib import Graph, Namespace, Literal, RDF, RDFS
from rdflib import RDF, RDFS
# Do not change the name of the variables
g = Graph()
g.namespace_manager.bind('ns', Namespace("http://somewhere#"), override=False)
g.parse(github_storage+"/rdf/data06.ttl", format="TTL")
report = Report()


result = [] #list of tuples
for s,p,o in g.triples((None, RDF.type, RDFS.Class)):
  o2 = g.value(subject=s, predicate=RDFS.subClassOf, object=None)
  result.append((s, o2))

for r in result:
  print(r)

## Validation: Do not remove
report.validate_07_1a(result)

query =  "SELECT ?c ?sc " \
"WHERE { " \
" ?c a rdfs:Class . " \
" OPTIONAL { ?c rdfs:subClassOf ?sc . } " \
"}"
"""SELECT ?c ?sc
WHERE {
  ?c a rdfs:Class .
  OPTIONAL { ?c rdfs:subClassOf ?sc . }
}"""

print(query)

for r in g.query(query):
  print(r.c, r.sc)


## Validation: Do not remove
report.validate_07_1b(query,g)


ns = Namespace("http://oeg.fi.upm.es/def/people#")


# DFS for retrieving all subclasses of person class
individuals = []
classes_to_check = []
class_stack = [ns.Person]
while len(class_stack) > 0:
  c = class_stack.pop()
  classes_to_check.append(c)
  for subC in g.subjects(predicate=RDFS.subClassOf, object=c):
    class_stack.append(subC)


for c in classes_to_check:
  for s,p,o in g.triples((None, RDF.type, c)):
    individuals.append(s)

# validation. Do not remove
report.validate_07_02a(individuals)

query =  """
SELECT ?ind
WHERE {
  ?ind a ?c .
  ?c rdfs:subClassOf* ontology:Person .
}"""

## Validation: Do not remove
report.validate_07_02b(g, query)

query =  """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX : <http://oeg.fi.upm.es/def/people#>
SELECT ?name ?type
WHERE {
  ?person :knows :Rocky .
  ?person rdf:type ?type .
  ?person rdfs:label ?name .
}
"""
## Validation: Do not remove
report.validate_07_03(g, query)

query =  """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX : <http://oeg.fi.upm.es/def/people#>

SELECT DISTINCT ?name
WHERE {
  {
    ?person :hasColleague ?colleague .
    ?colleague :ownsPet ?pet .
    ?pet rdf:type :Animal .
    ?person rdfs:label ?name .
  }
  UNION
  {
    ?person :hasColleague ?colleague1 .
    ?colleague1 :hasColleague ?colleague2 .
    ?colleague2 :ownsPet ?pet2 .
    ?pet2 rdf:type :Animal .
    ?person rdfs:label ?name .
  }
}
"""
## Validation: Do not remove
report.validate_07_04(g,query)
report.save_report("_Task_07")