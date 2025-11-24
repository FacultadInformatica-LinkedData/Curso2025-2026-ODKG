# %% [markdown]
# **Task 07: Querying RDF(s)**

# %%
#!pip install rdflib
import urllib.request
url = 'https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/refs/heads/master/Assignment4/course_materials/python/validation.py'
urllib.request.urlretrieve(url, 'validation.py')
github_storage = "https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/master/Assignment4/course_materials"

# %%
from validation import Report

# %% [markdown]
# First let's read the RDF file

# %%
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS
# Do not change the name of the variables
g = Graph()
g.namespace_manager.bind('ns', Namespace("http://somewhere#"), override=False)
g.parse(github_storage+"/rdf/data06.ttl", format="TTL")
report = Report()

# %%
#see all the classes and subclass relationships
#im doing this to check if theres a class dog but it seems that no ?
result = []  #list of tuples    
for c in g.subjects(RDF.type, RDFS.Class):
    sc = None
    for sc in g.objects(c, RDFS.subClassOf):
        result.append((c, sc))
    if sc is None:
        result.append((c, None))

#vualize results
for r in result:
  print(r)

# %% [markdown]
# **TASK 7.1a: For all classes, list each classURI. If the class belogs to another class, then list its superclass.**
# **Do the exercise in RDFLib returning a list of Tuples: (class, superclass) called "result". If a class does not have a super class, then return None as the superclass**

# %%
#collecting all the classes in the graph
classes = set(g.subjects(RDF.type, RDFS.Class))

#and now displaying their URIs and their superclasses
result=[]
for c in classes:
    superclasses = set(g.objects(c, RDFS.subClassOf))
    if superclasses:
        for s in superclasses:
            result.append((str(c), str(s)))
    else:
        result.append((str(c), None))

# %%
# TO DO
# Visualize the results
#  #list of tuples
for r in result:
  print(r)

# %%
## Validation: Do not remove
report.validate_07_1a(result)

# %% [markdown]
# **TASK 7.1b: Repeat the same exercise in SPARQL, returning the variables ?c (class) and ?sc (superclass)**

# %%
# Alternative way using SPARQL
query =  "Select ?c ?sc where { " \
         "?c rdf:type rdfs:Class . " \
         "OPTIONAL { ?c rdfs:subClassOf ?sc } " \
         "}"

for r in g.query(query):
  print(r.c, r.sc)


# %%
## Validation: Do not remove
report.validate_07_1b(query,g)

# %% [markdown]
# **TASK 7.2a: List all individuals of "Person" with RDFLib (remember the subClasses). Return the individual URIs in a list called "individuals"**
# 

# %%
#List all individuals of "Person" with RDFLib (remember the subClasses). Return the individual URIs in a list called "individuals"
#creating the list of individuals of Persn and its subclasses
ns = Namespace("http://oeg.fi.upm.es/def/people#")
#getting all subclasses of Person recursively
def get_subclasses(c):
    subclasses = {c}
    for subclass in g.subjects(RDFS.subClassOf, c):
        subclasses.update(get_subclasses(subclass))
    return subclasses

#gettingt all subclasses of Person
s = get_subclasses(ns.Person)

#now getting all individuals of Person and its subclasses
individuals = []
for subclass in s:
    for individual in g.subjects(RDF.type, subclass):
        individuals.append(str(individual))



# %%
# visualize results
for i in individuals:
  print(i)

# %%
# validation. Do not remove
report.validate_07_02a(individuals)

# %% [markdown]
# **TASK 7.2b: Repeat the same exercise in SPARQL, returning the individual URIs in a variable ?ind**

# %%
# same but in SPARQL
query =  "PREFIX ns: <http://oeg.fi.upm.es/def/people#>" \
  "Select ?ind where { " \
         "?ind rdf:type/rdfs:subClassOf* ns:Person . " \
         "}"

for r in g.query(query):
  print(r.ind)
# Visualize the results

# %%
## Validation: Do not remove
report.validate_07_02b(g, query)

# %% [markdown]
# **TASK 7.3:  List the name and type of those who know Rocky (in SPARQL only). Use name and type as variables in the query**

# %%
query =  """PREFIX ns: <http://oeg.fi.upm.es/def/people#>
select ?name ?type  where {
  ?ind ns:knows ns:Rocky .
  ?ind rdf:type ?type .
  ?ind rdfs:label ?name .
  }"""
# TO DO
# Visualize the results
for r in g.query(query):
  print(r.name, r.type)


# %%
## Validation: Do not remove
report.validate_07_03(g, query)

# %% [markdown]
# **Task 7.4: List the name of those entities who have a colleague with a dog, or that have a collegue who has a colleague who has a dog (in SPARQL). Return the results in a variable called name**

# %%
query =  """PREFIX ns: <http://oeg.fi.upm.es/def/people#>
select DISTINCT ?name where {
  {
  ?ind ns:hasColleague ?ind2 .
  ?ind2 ns:ownsPet ?p .
  ?p rdf:type ns:Animal .
  ?ind rdfs:label ?name . }

  UNION
  {
  ?ind ns:hasColleague ?ind2 .
  ?ind2 ns:hasColleague ?ind3 .
  ?ind3 ns:ownsPet ?p .
  ?p rdf:type ns:Animal .
  ?ind rdfs:label ?name .
  }
  }
"""

for r in g.query(query):
  print(r.name)

# TO DO
# Visualize the results

# %%
## Validation: Do not remove
report.validate_07_04(g,query)
report.save_report("_Task_07")


