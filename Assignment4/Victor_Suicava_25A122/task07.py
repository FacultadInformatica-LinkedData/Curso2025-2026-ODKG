# **Task 07: Querying RDF(s)**

#!pip install rdflib
import urllib.request
url = 'https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/refs/heads/master/Assignment4/course_materials/python/validation.py'
urllib.request.urlretrieve(url, 'validation.py')
github_storage = "https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/master/Assignment4/course_materials"

from validation import Report

# First let's read the RDF file

from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS
# Do not change the name of the variables
g = Graph()
g.namespace_manager.bind('ns', Namespace("http://somewhere#"), override=False)
g.parse(github_storage+"/rdf/data06.ttl", format="TTL")
report = Report()

# **TASK 7.1a: For all classes, list each classURI. If the class belogs to another class, then list its superclass.**
# **Do the exercise in RDFLib returning a list of Tuples: (class, superclass) called "result". If a class does not have a super class, then return None as the superclass**

# TO DO
result = [] #list of tuples
for r in g.subjects(RDF.type, RDFS.Class):
    # keep only your ontology classes
    if str(r).startswith("http://oeg.fi.upm.es/def/people#"):
        sc = g.value(r, RDFS.subClassOf)  # None if it doesn't have one
        result.append((r, sc))

# Visualize the results

for r in result:
  print(r)

## Validation: Do not remove
report.validate_07_1a(result)

# **TASK 7.1b: Repeat the same exercise in SPARQL, returning the variables ?c (class) and ?sc (superclass)**

query =  """

PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?c ?sc WHERE {
  ?c a rdfs:Class .
  FILTER(STRSTARTS(STR(?c), "http://oeg.fi.upm.es/def/people#"))
  OPTIONAL { ?c rdfs:subClassOf ?sc }
} 
  
  """

for r in g.query(query):
  print(r.c, r.sc)


## Validation: Do not remove
report.validate_07_1b(query,g)

# **TASK 7.2a: List all individuals of "Person" with RDFLib (remember the subClasses). Return the individual URIs in a list called "individuals"**
# 

ns = Namespace("http://oeg.fi.upm.es/def/people#")

classes = {ns.Person}
changed = True
while changed:
    changed = False
    for c in list(classes):
        for s in g.subjects(RDFS.subClassOf, c):
            if s not in classes:
                classes.add(s)
                changed = True

# variable to return
individuals = []
for cls in classes:
    for s in g.subjects(RDF.type, cls):
        individuals.append(s)



# visualize results
for i in individuals:
  print(i)

# validation. Do not remove
report.validate_07_02a(individuals)

# **TASK 7.2b: Repeat the same exercise in SPARQL, returning the individual URIs in a variable ?ind**

query =  """
PREFIX rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs:   <http://www.w3.org/2000/01/rdf-schema#>
PREFIX person: <http://oeg.fi.upm.es/def/people#>

SELECT ?ind WHERE {
  ?ind rdf:type ?cls .
  ?cls rdfs:subClassOf* person:Person .
}
"""

# Visualize the results
for r in g.query(query):
  print(r.ind)


## Validation: Do not remove
report.validate_07_02b(g, query)

# **TASK 7.3:  List the name and type of those who know Rocky (in SPARQL only). Use name and type as variables in the query**

# TO DO
query = """
PREFIX rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs:   <http://www.w3.org/2000/01/rdf-schema#>
PREFIX person: <http://oeg.fi.upm.es/def/people#>

SELECT DISTINCT ?name ?type WHERE {
    ?s person:knows person:Rocky .
    ?s rdfs:label ?name .
    ?s rdf:type ?type .
  
}
"""

for r in g.query(query):
    print(r.name, r.type)


## Validation: Do not remove
report.validate_07_03(g, query)



# **Task 7.4: List the name of those entities who have a colleague with a dog, or that have a collegue who has a colleague who has a dog (in SPARQL). Return the results in a variable called name**


# TO DO
query = """
PREFIX person: <http://oeg.fi.upm.es/def/people#>

SELECT DISTINCT ?name
WHERE {
    {
      ?p1 person:hasColleague ?p2 .
      ?p2 person:ownsPet ?pet.
      ?pet rdf:type person:Animal .
    }
    UNION 
    {
      ?p1 person:hasColleague ?p2 .
      ?p2 person:hasColleague ?p3 .
      ?p3 person:ownsPet ?pet.
      ?pet rdf:type person:Animal .
    }
    ?p1 rdfs:label ?name
  }
"""


## Visualize the results
for r in g.query(query):
    print(r.name)     



## Validation: Do not remove
report.validate_07_04(g,query)
report.save_report("_Task_07")


