#!/usr/bin/env python
# coding: utf-8

# **Task 07: Querying RDF(s)**

# In[1]:


#get_ipython().system('pip install rdflib')
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


# TO DO

result = []  # lista de tuplas

# Iterar sobre todas las clases
for class_uri in g.subjects(predicate=RDF.type, object=RDFS.Class):
    # Buscar la superclase
    super_class = g.value(subject=class_uri, predicate=RDFS.subClassOf)
    
    # Si no tiene superclase, agregar None
    if super_class is None:
        result.append((class_uri, None))
    else:
        result.append((class_uri, super_class))
        
# Visualize the results
for r in result:
  print(r)


# In[5]:


## Validation: Do not remove
report.validate_07_1a(result)


# **TASK 7.1b: Repeat the same exercise in SPARQL, returning the variables ?c (class) and ?sc (superclass)**

# In[6]:


# Consulta SPARQL para obtener clases y superclases
query = """
    SELECT ?c ?sc
    WHERE {
        ?c a rdfs:Class .  # Buscar clases
        OPTIONAL { ?c rdfs:subClassOf ?sc }  # Buscar superclases
    }
"""

for r in g.query(query):
  print(r.c, r.sc)


# In[7]:


## Validation: Do not remove
report.validate_07_1b(query,g)


# **TASK 7.2a: List all individuals of "Person" with RDFLib (remember the subClasses). Return the individual URIs in a list called "individuals"**
# 

# In[23]:


ns = Namespace("http://oeg.fi.upm.es/def/people#")

def get_all_subclasses(cls_uri):
    subclasses = []
    
    # Buscamos todas las subclases directas de la clase
    for sub_class in g.subjects(predicate=RDFS.subClassOf, object=cls_uri):
        subclasses.append(sub_class)
        # Recursivamente buscamos las subclases de esa subclase
        subclasses.extend(get_all_subclasses(sub_class))
    
    return subclasses

# variable to return
individuals = []

# Paso 1: Buscar las subclases de Person (recursivamente)
person_subclasses = get_all_subclasses(ns.Person)

# Paso 2: Buscar instancias de esas subclases
for sub_class in person_subclasses:
    for individual in g.subjects(predicate=RDF.type, object=sub_class):
        individuals.append(individual)
    
# visualize results
for i in individuals:
  print(i)


# In[24]:


# validation. Do not remove
report.validate_07_02a(individuals)


# **TASK 7.2b: Repeat the same exercise in SPARQL, returning the individual URIs in a variable ?ind**

# In[33]:


# Consulta SPARQL para obtener individuos de la clase 'Person'
query = """
    SELECT ?ind
    WHERE {
        {
            ?ind a <http://oeg.fi.upm.es/def/people#Person> .  # Buscar individuos de la clase Person
        }
        UNION
        { 
            ?ind a ?subclass .  # Buscar subclases de Person
            ?subclass rdfs:subClassOf <http://oeg.fi.upm.es/def/people#Person> .
        }
        UNION
        { 
            ?ind a ?subclass2 .  # Subclases de subclases
            ?subclass2 rdfs:subClassOf ?subclass .
            ?subclass rdfs:subClassOf <http://oeg.fi.upm.es/def/people#Person> .
        }
        UNION
        { 
            ?ind a ?subclass3 .  # Subclases de subclases de subclases
            ?subclass3 rdfs:subClassOf ?subclass2 .
            ?subclass2 rdfs:subClassOf ?subclass .
            ?subclass rdfs:subClassOf <http://oeg.fi.upm.es/def/people#Person> .
        }
    }
"""

# Visualize the results
for r in g.query(query):
    print(r.ind)


# In[34]:


## Validation: Do not remove
report.validate_07_02b(g, query)


# **TASK 7.3:  List the name and type of those who know Rocky (in SPARQL only). Use name and type as variables in the query**

# In[37]:


query =  """
    PREFIX ns:<http://oeg.fi.upm.es/def/people#>
    SELECT ?name ?type
    WHERE {
            ?name ns:knows ns:Rocky ;
                  a ?type
    }
"""

# Visualize the results
for r in g.query(query):
  print(r.name, r.type)


# In[38]:


## Validation: Do not remove
report.validate_07_03(g, query)


# **Task 7.4: List the name of those entities who have a colleague with a dog, or that have a collegue who has a colleague who has a dog (in SPARQL). Return the results in a variable called name**

# In[39]:


query =  """
    PREFIX ns:<http://oeg.fi.upm.es/def/people#>
    SELECT ?name
    WHERE {
        {
            ?name ns:hasColleague ?colleague .
            ?colleague ns:ownsPet ?pet .
        }
        UNION
        {
            ?name ns:hasColleague ?colleague1 .
            ?colleague1 ns:hasColleague ?colleague2 .
            ?colleague2 ns:ownsPet ?pet .
        }
    }
"""

for r in g.query(query):
  print(r.name)

# TO DO
# Visualize the results


# In[40]:


## Validation: Do not remove
report.validate_07_04(g,query)
report.save_report("_Task_07")

