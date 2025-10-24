# %% [markdown]
# **Task 07: Querying RDF(s)**

# %%
# !pip install rdflib
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
result = [] #list of tuples
for c in g.subjects(RDF.type, RDFS.Class):
    superclass = None
    for sc in g.objects(c, RDFS.subClassOf):
        superclass = sc
        break
    result.append((c, superclass))

# Visualize the results
for r in result:
  print(r)

# %%
## Validation: Do not remove
report.validate_07_1a(result)

# %% [markdown]
# **TASK 7.1b: Repeat the same exercise in SPARQL, returning the variables ?c (class) and ?sc (superclass)**

# %%
query =  "Select ?c ?sc where { ?c a rdfs:Class . OPTIONAL { ?c rdfs:subClassOf ?sc } }"

for r in g.query(query):
  print(r.c, r.sc)


# %%
## Validation: Do not remove
report.validate_07_1b(query,g)

# %% [markdown]
# **TASK 7.2a: List all individuals of "Person" with RDFLib (remember the subClasses). Return the individual URIs in a list called "individuals"**
# 

# %%
result = [] #list of tuples
for c in g.subjects(RDF.type, RDFS.Class):
    superclass = None
    for sc in g.objects(c, RDFS.subClassOf):
        superclass = sc
        break
    result.append((c, superclass))

# %%
ns = Namespace("http://oeg.fi.upm.es/def/people#")

def is_subclass_of(sub, parent, seen=None):
    if seen is None:
        seen = set()
    if sub == parent:
        return True
    if sub in seen:
        return False
    seen.add(sub)
    for sup in g.objects(sub, RDFS.subClassOf):
        if is_subclass_of(sup, parent, seen):
            return True
    return False


classes = [c for c in g.subjects(RDF.type, RDFS.Class) if is_subclass_of(c, ns.Person)]

individuals = []
for c in classes:
    for s in g.subjects(RDF.type, c):
        if s not in individuals:
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
from rdflib.plugins.sparql import prepareQuery

query = prepareQuery('''
  SELECT DISTINCT ?ind
  WHERE {
    ?ind a ?type .
    ?type rdfs:subClassOf* ns:Person .
  }
  ''',
  initNs = {"ns": ns})


for r in g.query(query):
  print(r.ind)

# Visualize the results

# %%
## Validation: Do not remove
report.validate_07_02b(g, query)

# %% [markdown]
# **TASK 7.3:  List the name and type of those who know Rocky (in SPARQL only). Use name and type as variables in the query**

# %%
query = prepareQuery(
  '''SELECT ?name ?type
  WHERE {
  ?x ns:knows ns:Rocky .
  ?x rdfs:label ?name .
  ?x a ?type .
  }''',
  initNs = {"ns": ns, "rdfs": RDFS})

# Visualize the results
for r in g.query(query):
  print(r.name, r.type)


# %%
## Validation: Do not remove
report.validate_07_03(g, query)

# %% [markdown]
# **Task 7.4: List the name of those entities who have a colleague with a dog, or that have a collegue who has a colleague who has a dog (in SPARQL). Return the results in a variable called name**

# %%
for s, p, o in g:
    print((s, p, o))

# %%
query = """
PREFIX ns: <http://oeg.fi.upm.es/def/people#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?name
WHERE {
  {
    ?x ns:hasColleague ?petowner .
    ?petowner ns:ownsPet ?pet .
    ?pet a ns:Animal .
    ?x rdfs:label ?name .
  }
  UNION
  {
    ?x ns:hasColleague ?y .
    ?y ns:hasColleague ?petowner .
    ?petowner ns:ownsPet ?pet .
    ?pet a ns:Animal .
    ?x rdfs:label ?name .
  }
}
"""

# Visualize the results
for r in g.query(query):
  print(r.name)

# %%
## Validation: Do not remove
report.validate_07_04(g,query)
report.save_report("_Task_07")


