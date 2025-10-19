#!/usr/bin/env python
# coding: utf-8

# **Task 07: Querying RDF(s)**

# In[ ]:


# !pip install rdflib
import urllib.request
url = 'https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/refs/heads/master/Assignment4/course_materials/python/validation.py'
urllib.request.urlretrieve(url, 'validation.py')
github_storage = "https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/master/Assignment4/course_materials"


# In[ ]:


from validation import Report


# First let's read the RDF file

# In[ ]:


from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS
# Do not change the name of the variables
g = Graph()
g.namespace_manager.bind('ns', Namespace("http://somewhere#"), override=False)
g.parse(github_storage+"/rdf/data06.ttl", format="TTL")
report = Report()


# **TASK 7.1a: For all classes, list each classURI. If the class belogs to another class, then list its superclass.**
# **Do the exercise in RDFLib returning a list of Tuples: (class, superclass) called "result". If a class does not have a super class, then return None as the superclass**

# In[ ]:


# Task 7.1a
result = []
visited = set()
for cls in g.subjects(RDF.type, RDFS.Class):
    if cls not in visited:
        superclass = g.value(subject=cls, predicate=RDFS.subClassOf) or None
        result.append((cls, superclass))
        visited.add(cls)

result.sort(key=lambda x: str(x[0]))

for r in result:
    print(r)


# In[ ]:


## Validation: Do not remove
report.validate_07_1a(result)


# **TASK 7.1b: Repeat the same exercise in SPARQL, returning the variables ?c (class) and ?sc (superclass)**

# In[ ]:


# Task 7.1b
query = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX : <http://oeg.fi.upm.es/def/people#>
SELECT DISTINCT ?c ?sc WHERE {
  ?c a rdfs:Class .
  OPTIONAL { ?c rdfs:subClassOf ?sc }
}
"""

for r in g.query(query):
  print(r.c, r.sc)


# In[ ]:


## Validation: Do not remove
report.validate_07_1b(query,g)


# **TASK 7.2a: List all individuals of "Person" with RDFLib (remember the subClasses). Return the individual URIs in a list called "individuals"**
# 

# In[ ]:


ns = Namespace("http://oeg.fi.upm.es/def/people#")

# Task 7.2a
individuals = []
visited_classes = {ns.Person}
queue = [ns.Person]

while queue:
    current = queue.pop(0)
    for subclass in g.subjects(RDFS.subClassOf, current):
        if subclass not in visited_classes:
            visited_classes.add(subclass)
            queue.append(subclass)

for cls in visited_classes:
    for ind in g.subjects(RDF.type, cls):
        if str(ind) not in individuals:
            individuals.append(str(ind))

individuals.sort()

for i in individuals:
  print(i)


# In[ ]:


# validation. Do not remove
report.validate_07_02a(individuals)


# **TASK 7.2b: Repeat the same exercise in SPARQL, returning the individual URIs in a variable ?ind**

# In[ ]:


ns = Namespace("http://oeg.fi.upm.es/def/people#")

# Task 7.2b
query = """
PREFIX : <http://oeg.fi.upm.es/def/people#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?ind WHERE {
  ?ind a ?class .
  ?class rdfs:subClassOf* :Person .
}
"""

for r in g.query(query):
  print(r.ind)
# Visualize the results


# In[ ]:


## Validation: Do not remove
report.validate_07_02b(g, query)


# **TASK 7.3:  List the name and type of those who know Rocky (in SPARQL only). Use name and type as variables in the query**

# In[ ]:


ns = Namespace("http://oeg.fi.upm.es/def/people#")

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
# TO DO
# Visualize the results
for r in g.query(query):
  print(r.name, r.type)


# In[ ]:


## Validation: Do not remove
report.validate_07_03(g, query)


# **Task 7.4: List the name of those entities who have a colleague with a dog, or that have a collegue who has a colleague who has a dog (in SPARQL). Return the results in a variable called name**

# In[ ]:


ns = Namespace("http://oeg.fi.upm.es/def/people#")

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

# TO DO
# Visualize the results


# In[ ]:


## Validation: Do not remove
report.validate_07_04(g,query)
report.save_report("_Task_07")

