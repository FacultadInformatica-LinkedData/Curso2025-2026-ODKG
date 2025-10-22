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

# %% [markdown]
# **TASK 7.1a: For all classes, list each classURI. If the class belogs to another class, then list its superclass.**
# **Do the exercise in RDFLib returning a list of Tuples: (class, superclass) called "result". If a class does not have a super class, then return None as the superclass**

# %%
# TO DO
result = [] #list of tuples

for c in g.subjects(RDF.type, RDFS.Class):
    superclass = g.value(subject=c, predicate=RDFS.subClassOf)
    result.append((c, superclass if superclass else None))

# Visualize the results
for r in result:
  print(r)

# %%
## Validation: Do not remove
report.validate_07_1a(result)

# %% [markdown]
# **TASK 7.1b: Repeat the same exercise in SPARQL, returning the variables ?c (class) and ?sc (superclass)**

# %%

query =  "SELECT ?c ?sc " \
"WHERE { " \
" ?c a rdfs:Class . " \
" OPTIONAL { ?c rdfs:subClassOf ?sc . } " \
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
ns = Namespace("http://oeg.fi.upm.es/def/people#")

# variable to return
individuals = []
# list for exploring classes
classes = [ns.Person]

# explore subclasses
checked = []
while len(classes) > 0:
    c = classes.pop()
    checked.append(c)
    for subC in g.subjects(predicate=RDFS.subClassOf, object=c):
        classes.append(subC)

# look individuals in each class found
for c in checked:
    for s, p, o in g.triples((None, RDF.type, c)):
        individuals.append(s)

# visualize results
for i in individuals:
  print(i)

# %%
# validation. Do not remove
report.validate_07_02a(individuals)

# %% [markdown]
# **TASK 7.2b: Repeat the same exercise in SPARQL, returning the individual URIs in a variable ?ind**

# %%
query =  """
SELECT ?ind
WHERE {
  ?ind a ?c .
  ?c rdfs:subClassOf* ontology:Person .
}"""


for r in g.query(query):
  print(r.ind)
# Visualize the results

# %%
## Validation: Do not remove
report.validate_07_02b(g, query)

# %% [markdown]
# **TASK 7.3:  List the name and type of those who know Rocky (in SPARQL only). Use name and type as variables in the query**

# %%
# TO DO
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

# Visualize the results
for r in g.query(query):
  print(r.name, r.type)



# %%
## Validation: Do not remove
report.validate_07_03(g, query)

# %% [markdown]
# **Task 7.4: List the name of those entities who have a colleague with a dog, or that have a collegue who has a colleague who has a dog (in SPARQL). Return the results in a variable called name**

# %%
query = """
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX :    <http://oeg.fi.upm.es/def/people#>

SELECT DISTINCT ?name
WHERE {
  {
    ?person :hasColleague ?col1 .
    ?col1 :ownsPet ?pet1 .
    ?pet1 rdf:type :Animal .
    ?person rdfs:label ?name .
  }
  UNION
  {
    ?person :hasColleague ?col1 .
    ?col1 :hasColleague ?col2 .
    ?col2 :ownsPet ?pet2 .
    ?pet2 rdf:type :Animal .
    ?person rdfs:label ?name .
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

# %%



