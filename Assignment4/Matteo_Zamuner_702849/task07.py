import urllib.request
url = 'https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/refs/heads/master/Assignment4/course_materials/python/validation.py'
urllib.request.urlretrieve(url, 'validation.py')
github_storage = "https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/master/Assignment4/course_materials"

from validation import Report

"""First let's read the RDF file"""

from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS
# Do not change the name of the variables
g = Graph()
g.namespace_manager.bind('ns', Namespace("http://somewhere#"), override=False)
g.parse(github_storage+"/rdf/data06.ttl", format="TTL")
report = Report()

"""**TASK 7.1a: For all classes, list each classURI. If the class belogs to another class, then list its superclass.**
**Do the exercise in RDFLib returning a list of Tuples: (class, superclass) called "result". If a class does not have a super class, then return None as the superclass**
"""

result = []

class_uris = set(g.subjects(RDF.type, RDFS.Class))

for cls in sorted(class_uris, key=lambda x: str(x)):
  super_class = list(g.objects(cls, RDFS.subClassOf))
  result.append((cls, super_class[0] if super_class else None))

# Visualize the results
for item in result:
  print(item)

## Validation: Do not remove
report.validate_07_1a(result)

"""**TASK 7.1b: Repeat the same exercise in SPARQL, returning the variables ?c (class) and ?sc (superclass)**"""

query =  """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?c ?sc
WHERE {
  ?c a rdfs:Class .
  OPTIONAL {
    ?c rdfs:subClassOf ?sc .
  }
}
ORDER BY ?c
"""

for result_row in g.query(query):
  print(result_row.c, result_row.sc)

## Validation: Do not remove
report.validate_07_1b(query,g)

"""**TASK 7.2a: List all individuals of "Person" with RDFLib (remember the subClasses). Return the individual URIs in a list called "individuals"**"""

ns = Namespace("http://oeg.fi.upm.es/def/people#")

person_types = {ns.Person}
all_types = set()

while person_types:
  current_type = person_types.pop()
  if current_type in all_types:
    continue
  all_types.add(current_type)
  for sub_class in g.subjects(RDFS.subClassOf, current_type):
    person_types.add(sub_class)

# variable to return
individuals = []

for person_type in all_types:
  for individual in g.subjects(RDF.type, person_type):
    individuals.append(individual)

individuals = set(individuals)

# visualize results
for individual in individuals:
  print(individual)

# validation. Do not remove
report.validate_07_02a(individuals)

"""**TASK 7.2b: Repeat the same exercise in SPARQL, returning the individual URIs in a variable ?ind**"""

query =  """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ns:   <http://oeg.fi.upm.es/def/people#>

SELECT ?ind
WHERE {
  ?ind a ?class .
  ?class rdfs:subClassOf* ns:Person .
}
"""

for result_row in g.query(query):
  print(result_row.ind)
# Visualize the results

## Validation: Do not remove
report.validate_07_02b(g, query)

"""**TASK 7.3:  List the name and type of those who know Rocky (in SPARQL only). Use name and type as variables in the query**"""

query =  """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ns:   <http://oeg.fi.upm.es/def/people#>

SELECT DISTINCT ?name ?type
WHERE {
  ?person rdfs:label ?name .
  ?person ns:knows ns:Rocky .
  ?person a ?type .
}
"""

# Visualize the results
for result_row in g.query(query):
  print(result_row.name, result_row.type)

## Validation: Do not remove
report.validate_07_03(g, query)

"""**Task 7.4: List the name of those entities who have a colleague with a dog, or that have a collegue who has a colleague who has a dog (in SPARQL). Return the results in a variable called name**"""

query =  """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ns:   <http://oeg.fi.upm.es/def/people#>

SELECT DISTINCT ?name
WHERE {
  ?person rdfs:label ?name .
  {
    ?person ns:hasColleague ?colleague .
    ?colleague ns:ownsPet ?dog .
    ?dog rdf:type ?Animal .
  }
  UNION
  {
    ?person ns:hasColleague ?colleague1 .
    ?colleague1 ns:hasColleague ?colleague2 .
    ?colleague2 ns:ownsPet ?dog .
    ?dog rdf:type ?Animal .
  }
}
"""

# Visualize the results
for result_row in g.query(query):
  print(result_row.name)

## Validation: Do not remove
report.validate_07_04(g,query)
report.save_report("_Task_07")