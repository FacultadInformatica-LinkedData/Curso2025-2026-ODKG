# Task 07: Querying RDF(s)

import urllib.request
url = 'https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/refs/heads/master/Assignment4/course_materials/python/validation.py'
urllib.request.urlretrieve(url, 'validation.py')
github_storage = "https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/master/Assignment4/course_materials"

from validation import Report

from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS

g = Graph()
g.namespace_manager.bind('ns', Namespace("http://somewhere#"), override=False)
g.parse(github_storage + "/rdf/data06.ttl", format="TTL")
report = Report()

# TASK 7.1a
result = []  # list of tuples
for s, p, o in g.triples((None, RDF.type, RDFS.Class)):
    superclass = g.value(subject=s, predicate=RDFS.subClassOf, object=None)
    result.append((s, superclass))

for r in result:
    print(r)

# Validation
report.validate_07_1a(result)

# TASK 7.1b (SPARQL)
query = """
select ?c ?sc
WHERE {
    ?c rdf:type rdfs:Class .
    OPTIONAL { ?c rdfs:subClassOf ?sc }
}
"""

for r in g.query(query):
    print(r.c, r.sc)

report.validate_07_1b(query, g)

# TASK 7.2a
ns = Namespace("http://oeg.fi.upm.es/def/people#")

individuals = []

classe = set([ns.Person])

def add_subclasse(cls):
    for subclass in g.subjects(RDFS.subClassOf, cls):
        if subclass not in classe:
            classe.add(subclass)
            add_subclasse(subclass)

add_subclasse(ns.Person)

for cls in classe:
    for indiv in g.subjects(RDF.type, cls):
        individuals.append(indiv)

for i in individuals:
    print(i)

report.validate_07_02a(individuals)

# TASK 7.2b (SPARQL)
query = """
Select ?ind
Where {
  ?ind a ?c .
  ?c rdfs:subClassOf* ontology:Person .
}
"""

for r in g.query(query):
    print(r.ind)

report.validate_07_02b(g, query)

# TASK 7.3
query = """
prefix people: <http://oeg.fi.upm.es/def/people#>

Select ?name ?type
Where {
  ?person people:knows people:Rocky .
  ?person rdfs:label ?name.
  ?person rdf:type ?type
}
"""

for r in g.query(query):
    print(r.name, r.type)

report.validate_07_03(g, query)

# TASK 7.4
query = """
PREFIX people: <http://oeg.fi.upm.es/def/people#>

select ?name
Where{
{
      ?person people:hasColleague ?colleague1 .
      ?colleague1 people:ownsPet ?pet.
      ?pet rdf:type people:Animal .
    }
    UNION
    {
      ?person people:hasColleague ?colleague1 .
      ?colleague1 people:hasColleague ?colleague2 .
      ?colleague2 people:ownsPet ?pet.
      ?pet rdf:type people:Animal .
    }

    ?person rdfs:label ?name
  }
"""

for r in g.query(query):
    print(r.name)

report.validate_07_04(g, query)
report.save_report("_Task_07")
