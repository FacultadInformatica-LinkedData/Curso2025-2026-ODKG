#!/usr/bin/env python
# coding: utf-8

# **Task 06: Modifying RDF(s)**

# In[1]:


# get_ipython().system('pip install rdflib')
import urllib.request
url = 'https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/refs/heads/master/Assignment4/course_materials/python/validation.py'
urllib.request.urlretrieve(url, 'validation.py')
github_storage = "https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/master/Assignment4/course_materials"


# Import RDFLib main methods

# In[2]:


from rdflib import Graph, Namespace, Literal, XSD
from rdflib.namespace import RDF, RDFS
from validation import Report
g = Graph()
g.namespace_manager.bind('ns', Namespace("http://somewhere#"), override=False)
r = Report()


# Create a new class named Researcher

# In[3]:


ns = Namespace("http://mydomain.org#")
g.add((ns.Researcher, RDF.type, RDFS.Class))
for s, p, o in g:
  print(s,p,o)


# **Task 6.0: Create new prefixes for "ontology" and "person" as shown in slide 14 of the Slidedeck 01a.RDF(s)-SPARQL shown in class.**

# In[4]:


# this task is validated in the next step

# Crear nuevos prefijos para "ontology" y "person" según la diapositiva 14
ontology_ns = Namespace("http://oeg.fi.upm.es/def/people#")
person_ns = Namespace("http://oeg.fi.upm.es/resource/person/")

# Añadir los nuevos prefijos al gráfico
g.namespace_manager.bind('ontology', ontology_ns, override=False)
g.namespace_manager.bind('person', person_ns, override=False)


# **TASK 6.1: Reproduce the taxonomy of classes shown in slide 34 in class (all the classes under "Vocabulario", Slidedeck: 01a.RDF(s)-SPARQL). Add labels for each of them as they are in the diagram (exactly) with no language tags. Remember adding the correct datatype (xsd:String) when appropriate**
# 

# In[5]:


# TO DO

# Reproducir la taxonomía de clases mostrada en la diapositiva 34
g.add((ontology_ns.Person, RDF.type, RDFS.Class))
g.add((ontology_ns.Employee, RDF.type, RDFS.Class))
g.add((ontology_ns.Student, RDF.type, RDFS.Class))
g.add((ontology_ns.Professor, RDF.type, RDFS.Class))
g.add((ontology_ns.AssociateProfessor, RDF.type, RDFS.Class))
g.add((ontology_ns.InterimAssociateProfessor, RDF.type, RDFS.Class))
g.add((ontology_ns.FullProfessor, RDF.type, RDFS.Class))

# Añadir las etiquetas para cada clase
g.add((ontology_ns.Person, RDFS.label, Literal("Person", datatype=XSD.string)))
g.add((ontology_ns.Employee, RDFS.label, Literal("Employee", datatype=XSD.string)))
g.add((ontology_ns.Student, RDFS.label, Literal("Student", datatype=XSD.string)))
g.add((ontology_ns.Professor, RDFS.label, Literal("Professor", datatype=XSD.string)))
g.add((ontology_ns.AssociateProfessor, RDFS.label, Literal("AssociateProfessor", datatype=XSD.string)))
g.add((ontology_ns.InterimAssociateProfessor, RDFS.label, Literal("InterimAssociateProfessor", datatype=XSD.string)))
g.add((ontology_ns.FullProfessor, RDFS.label, Literal("FullProfessor", datatype=XSD.string)))

# Añadir relaciones de subclase (subClassOf)
g.add((ontology_ns.Professor, RDFS.subClassOf, ontology_ns.Person))
g.add((ontology_ns.AssociateProfessor, RDFS.subClassOf, ontology_ns.Professor))
g.add((ontology_ns.InterimAssociateProfessor, RDFS.subClassOf, ontology_ns.AssociateProfessor))
g.add((ontology_ns.FullProfessor, RDFS.subClassOf, ontology_ns.Professor))

# Visualize the results
for s, p, o in g:
  print(s,p,o)


# In[6]:


# Validation. Do not remove
r.validate_task_06_01(g)


# **TASK 6.2: Add the 3 properties shown in slide 36. Add labels for each of them (exactly as they are in the slide, with no language tags), and their corresponding domains and ranges using RDFS. Remember adding the correct datatype (xsd:String) when appropriate. If a property has no range, make it a literal (string)**

# In[7]:


# TO DO

# Propiedad 1: hasColleague
g.add((ontology_ns.hasColleague, RDF.type, RDF.Property))
g.add((ontology_ns.hasColleague, RDFS.label, Literal("hasColleague", datatype=XSD.string)))
g.add((ontology_ns.hasColleague, RDFS.domain, ontology_ns.Person))
g.add((ontology_ns.hasColleague, RDFS.range, ontology_ns.Person))

# Propiedad 2: hasName (dominio: Person, rango: xsd:string)
g.add((ontology_ns.hasName, RDF.type, RDF.Property))
g.add((ontology_ns.hasName, RDFS.label, Literal("hasName", datatype=XSD.string)))
g.add((ontology_ns.hasName, RDFS.domain, ontology_ns.Person))  # Corregido: dominio Person
g.add((ontology_ns.hasName, RDFS.range, RDFS.Literal))  # Rango corregido: xsd:string

# Propiedad 3: hasHomePage (dominio: FullProfessor, rango: xsd:string)
g.add((ontology_ns.hasHomePage, RDF.type, RDF.Property))
g.add((ontology_ns.hasHomePage, RDFS.label, Literal("hasHomePage", datatype=XSD.string)))
g.add((ontology_ns.hasHomePage, RDFS.domain, ontology_ns.FullProfessor))  # Corregido: dominio FullProfessor
g.add((ontology_ns.hasHomePage, RDFS.range, RDFS.Literal))  # Rango corregido: xsd:string


# Visualize the results
for s, p, o in g:
  print(s,p,o)


# In[8]:


# Validation. Do not remove
r.validate_task_06_02(g)


# **TASK 6.3: Create the individuals shown in slide 36 under "Datos". Link them with the same relationships shown in the diagram."**

# In[9]:


# TO DO

# Crear los individuos
g.add((person_ns.Oscar, RDF.type, ontology_ns.Person))
g.add((person_ns.Asun, RDF.type, ontology_ns.Person))
g.add((person_ns.Raul, RDF.type, ontology_ns.Person))

# Asignar etiquetas a los individuos
g.add((person_ns.Oscar, RDFS.label, Literal("Oscar", datatype=XSD.string)))
g.add((person_ns.Asun, RDFS.label, Literal("Asun", datatype=XSD.string)))
g.add((person_ns.Raul, RDFS.label, Literal("Raul", datatype=XSD.string)))

# Relacionar a Oscar con Asun como colegas
g.add((person_ns.Oscar, ontology_ns.hasColleague, person_ns.Asun))
g.add((person_ns.Asun, ontology_ns.hasColleague, person_ns.Oscar))

# Asignar nombre a Oscar
g.add((person_ns.Oscar, ontology_ns.hasName, Literal("Óscar Corcho García", datatype=XSD.string)))

# Asignar página web a Asun
g.add((person_ns.Asun, ontology_ns.hasHomePage, Literal("http://www.oeg-upm.net/", datatype=XSD.string)))

# Visualize the results
for s, p, o in g:
  print(s,p,o)


# In[10]:


r.validate_task_06_03(g)


# **TASK 6.4: Add to the individual person:Oscar the email address, given and family names. Use the properties already included in example 4 to describe Jane and John (https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/master/Assignment4/course_materials/rdf/example4.rdf). Do not import the namespaces, add them manually**
# 

# In[11]:


# TO DO

# Crear los namespaces (manuales, como se pide)
VCARD = Namespace("http://www.w3.org/2001/vcard-rdf/3.0/")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")

# Añadir los prefijos al gráfico
g.namespace_manager.bind('vcard', VCARD, override=False)
g.namespace_manager.bind('foaf', FOAF, override=False)

# Añadir propiedades de Oscar
g.add((person_ns.Oscar, VCARD.Given, Literal("Óscar", datatype=XSD.string)))  # Given name
g.add((person_ns.Oscar, VCARD.Family, Literal("Corcho García", datatype=XSD.string)))  # Family name
g.add((person_ns.Oscar, FOAF.email, Literal("oscar.corcho@example.com", datatype=XSD.string)))  # Email

# Visualize the results
for s, p, o in g:
  print(s,p,o)


# In[12]:


# Validation. Do not remove
r.validate_task_06_04(g)
r.save_report("_Task_06")

