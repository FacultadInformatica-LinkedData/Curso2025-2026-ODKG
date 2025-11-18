#!/usr/bin/env python
# coding: utf-8

# **Task 07: Querying RDF(s)**

# In[2]:


#get_ipython().system('pip install rdflib')
import urllib.request
url = 'https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/refs/heads/master/Assignment4/course_materials/python/validation.py'
urllib.request.urlretrieve(url, 'validation.py')
github_storage = "https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/master/Assignment4/course_materials"


# In[3]:


from validation import Report


# First let's read the RDF file

# In[4]:


from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS
# Do not change the name of the variables
g = Graph()
g.namespace_manager.bind('ns', Namespace("http://somewhere#"), override=False)
g.parse(github_storage+"/rdf/data06.ttl", format="TTL")
report = Report()


# **TASK 7.1a: For all classes, list each classURI. If the class belogs to another class, then list its superclass.**
# **Do the exercise in RDFLib returning a list of Tuples: (class, superclass) called "result". If a class does not have a super class, then return None as the superclass**

# In[5]:


# Step 1: Find all class URIs
classes = list(g.subjects(RDF.type, RDFS.Class))

# Step 2: For each class, find its superclass (if any)
result = []

for cls in classes:
    superclasses = list(g.objects(cls, RDFS.subClassOf))
    
    if superclasses:
        for sup in superclasses:
            result.append((str(cls), str(sup)))
    else:
        result.append((str(cls), None))

print("\n(class, superclass) pairs:")
for r in result:
    print(r)



# In[6]:


## Validation: Do not remove
report.validate_07_1a(result)


# **TASK 7.1b: Repeat the same exercise in SPARQL, returning the variables ?c (class) and ?sc (superclass)**

# In[7]:


# SPARQL query
query = """
SELECT ?c ?sc
WHERE {
  ?c a rdfs:Class .
  OPTIONAL {
    ?c rdfs:subClassOf ?sc .
    FILTER (?c != ?sc)
  }
}
"""

for r in g.query(query):
  print(r.c, r.sc)


# In[8]:


## Validation: Do not remove
report.validate_07_1b(query,g)


# **TASK 7.2a: List all individuals of "Person" with RDFLib (remember the subClasses). Return the individual URIs in a list called "individuals"**
# 

# In[9]:


from rdflib import Graph, RDF, RDFS, URIRef, Namespace

ns = Namespace("http://oeg.fi.upm.es/def/people#")

# Step 1: Define the target class (Person)
person_class = URIRef(ns + "Person")

# Step 2: Collect all subclasses of Person (recursively)
def get_all_subclasses(graph, class_uri):
    subclasses = set()
    direct_subs = list(graph.subjects(RDFS.subClassOf, class_uri))
    for sub in direct_subs:
        subclasses.add(sub)
        subclasses.update(get_all_subclasses(graph, sub))
    return subclasses

all_classes = {person_class} | get_all_subclasses(g, person_class)

# Step 3: Find all individuals of Person or its subclasses
individuals = set()
for cls in all_classes:
    for ind in g.subjects(RDF.type, cls):
        individuals.add(str(ind))

individuals = list(individuals)

# Step 4: Print the result
print("Individuals of Person (including subclasses):")
for ind in individuals:
    print(ind)

# variable to return
#individuals = []
# visualize results
for i in individuals:
  print(i)


# In[10]:


# validation. Do not remove
report.validate_07_02a(individuals)


# **TASK 7.2b: Repeat the same exercise in SPARQL, returning the individual URIs in a variable ?ind**

# In[48]:


query = f"""
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX people: <{ns}>

SELECT DISTINCT ?ind
WHERE {{
  ?ind rdf:type ?class .
  ?class rdfs:subClassOf* people:Person .
}}
"""

for r in g.query(query):
  print(r.ind)
# Visualize the results


# In[12]:


## Validation: Do not remove
report.validate_07_02b(g, query)


# **TASK 7.3:  List the name and type of those who know Rocky (in SPARQL only). Use name and type as variables in the query**

# In[49]:


query = f"""
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX people: <{ns}>

SELECT DISTINCT ?name ?type
WHERE {{
  ?person people:knows people:Rocky .
  OPTIONAL {{ ?person rdfs:label ?name . }}
  #OPTIONAL {{ ?person people:name ?name . }}
  OPTIONAL {{ ?person rdf:type ?type . }}
}}
"""

results = g.query(query)
    
# Visualize the results
for r in g.query(query):
  print(r.name, r.type)


# In[21]:


## Validation: Do not remove
report.validate_07_03(g, query)


# **Task 7.4: List the name of those entities who have a colleague with a dog, or that have a collegue who has a colleague who has a dog (in SPARQL). Return the results in a variable called name**

# In[62]:


query = f"""
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX people: <http://oeg.fi.upm.es/def/people#>

SELECT DISTINCT ?name
WHERE {{
  {{
    ?person people:hasColleague ?colleague .
    ?colleague people:ownsPet ?dog .
    ?dog rdf:type people:Animal .
  }}
  UNION
  {{
    ?person people:hasColleague ?colleague .
    ?colleague people:hasColleague ?colleague2 .
    ?colleague2 people:ownsPet ?dog .
    ?dog rdf:type people:Animal .
  }}
  OPTIONAL {{ ?person rdfs:label ?name . }}
  OPTIONAL {{ ?person people:name ?name . }}
}}
"""

# Visualize the results
for r in g.query(query):
  print(r.name)

# TO DO
# Visualize the results


# In[63]:


## Validation: Do not remove
report.validate_07_04(g,query)
report.save_report("_Task_07")


# In[ ]:




