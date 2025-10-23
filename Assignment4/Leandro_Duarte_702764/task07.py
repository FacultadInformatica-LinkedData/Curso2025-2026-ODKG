#!/usr/bin/env python
# coding: utf-8

# **Task 07: Querying RDF(s)**

# In[ ]:


#!pip install rdflib
import urllib.request
url = 'https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/refs/heads/master/Assignment4/course_materials/python/validation.py'
urllib.request.urlretrieve(url, 'validation.py')
github_storage = "https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/master/Assignment4/course_materials"


# In[2]:


from validation import Report


# First let's read the RDF file

# In[3]:


from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS
# Do not change the name of the variables
g = Graph()
g.namespace_manager.bind('ns', Namespace("http://somewhere#"), override=False)
g.parse(github_storage+"/rdf/data06.ttl", format="TTL")
report = Report()


# **TASK 7.1a: For all classes, list each classURI. If the class belogs to another class, then list its superclass.**
# **Do the exercise in RDFLib returning a list of Tuples: (class, superclass) called "result". If a class does not have a super class, then return None as the superclass**

# In[4]:


# Task 7.1a: List all classes with their superclass (or None)
result = [] #list of tuples
# Iterate over all classes in the graph
for cls in g.subjects(RDF.type, RDFS.Class):
    # Get the superclass (rdfs:subClassOf) if it exists
    superclass = g.value(subject=cls, predicate=RDFS.subClassOf)
    result.append((cls, superclass))

# Visualize the results
for r in result:
  print(r)


# In[5]:


## Validation: Do not remove
report.validate_07_1a(result)


# **TASK 7.1b: Repeat the same exercise in SPARQL, returning the variables ?c (class) and ?sc (superclass)**

# In[6]:


# Task 7.1b: SPARQL query to list classes and their superclass
query = """
SELECT ?c ?sc
WHERE {
    ?c rdf:type rdfs:Class .
    OPTIONAL { ?c rdfs:subClassOf ?sc }
}
"""

for r in g.query(query):
  print(r.c, r.sc)


# In[7]:


## Validation: Do not remove
report.validate_07_1b(query,g)


# **TASK 7.2a: List all individuals of "Person" with RDFLib (remember the subClasses). Return the individual URIs in a list called "individuals"**
# 

# In[8]:


ns = Namespace("http://oeg.fi.upm.es/def/people#")

# Task 7.2a: Get all individuals of Person (including subclasses)
# Function to recursively get all subclasses
def get_all_subclasses(cls):
    subclasses = {cls}
    for sub in g.subjects(RDFS.subClassOf, cls):
        subclasses.update(get_all_subclasses(sub))
    return subclasses

# Get Person and all its subclasses
person_classes = get_all_subclasses(ns.Person)

# Get all individuals of these classes
individuals = []
for person_class in person_classes:
    for individual in g.subjects(RDF.type, person_class):
        if individual not in individuals:
            individuals.append(individual)

# visualize results
for i in individuals:
  print(i)


# In[9]:


# validation. Do not remove
report.validate_07_02a(individuals)


# **TASK 7.2b: Repeat the same exercise in SPARQL, returning the individual URIs in a variable ?ind**

# In[10]:


# Task 7.2b: SPARQL query to list all Person individuals
query = """
PREFIX people: <http://oeg.fi.upm.es/def/people#>
SELECT DISTINCT ?ind
WHERE {
    ?ind rdf:type/rdfs:subClassOf* people:Person .
}
"""

for r in g.query(query):
  print(r.ind)
# Visualize the results


# In[11]:


## Validation: Do not remove
report.validate_07_02b(g, query)


# **TASK 7.3:  List the name and type of those who know Rocky (in SPARQL only). Use name and type as variables in the query**

# In[12]:


# Task 7.3: List name and type of those who know Rocky
query = """
PREFIX people: <http://oeg.fi.upm.es/def/people#>
SELECT ?name ?type
WHERE {
    ?person people:knows people:Rocky .
    ?person rdfs:label ?name .
    ?person rdf:type ?type .
}
"""

# Visualize the results
for r in g.query(query):
  print(r.name, r.type)


# In[13]:


## Validation: Do not remove
report.validate_07_03(g, query)


# **Task 7.4: List the name of those entities who have a colleague with a dog, or that have a collegue who has a colleague who has a dog (in SPARQL). Return the results in a variable called name**

# In[14]:


# Task 7.4: Entities with colleague who has dog, or colleague of colleague with dog
query = """
PREFIX people: <http://oeg.fi.upm.es/def/people#>
SELECT DISTINCT ?name
WHERE {
    {
        # Colleague with a dog
        ?person people:hasColleague ?col1 .
        ?col1 people:ownsPet ?pet .
        ?pet rdf:type people:Animal .
    }
    UNION
    {
        # Colleague of colleague with a dog
        ?person people:hasColleague ?col1 .
        ?col1 people:hasColleague ?col2 .
        ?col2 people:ownsPet ?pet .
        ?pet rdf:type people:Animal .
    }
    ?person rdfs:label ?name .
}
"""

for r in g.query(query):
  print(r.name)

# Visualize the results


# In[15]:


## Validation: Do not remove
report.validate_07_04(g,query)
report.save_report("_Task_07")

