#!/usr/bin/env python
# coding: utf-8

# **Task 06: Modifying RDF(s)**

# In[ ]:


# !pip install rdflib
import urllib.request
url = 'https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/refs/heads/master/Assignment4/course_materials/python/validation.py'
urllib.request.urlretrieve(url, 'validation.py')
github_storage = "https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/master/Assignment4/course_materials"


# Import RDFLib main methods

# In[ ]:


from rdflib import Graph, Namespace, Literal, XSD
from rdflib.namespace import RDF, RDFS
from validation import Report
g = Graph()
g.namespace_manager.bind('ns', Namespace("http://somewhere#"), override=False)
r = Report()
ontology = Namespace("http://oeg.fi.upm.es/def/people#")
person = Namespace("http://oeg.fi.upm.es/resource/person/")


# Create a new class named Researcher

# In[ ]:


ns = Namespace("http://mydomain.org#")
g.add((ns.Researcher, RDF.type, RDFS.Class))
for s, p, o in g:
  print(s,p,o)


# **Task 6.0: Create new prefixes for "ontology" and "person" as shown in slide 14 of the Slidedeck 01a.RDF(s)-SPARQL shown in class.**

# In[ ]:


# this task is validated in the next step


# **TASK 6.1: Reproduce the taxonomy of classes shown in slide 34 in class (all the classes under "Vocabulario", Slidedeck: 01a.RDF(s)-SPARQL). Add labels for each of them as they are in the diagram (exactly) with no language tags. Remember adding the correct datatype (xsd:String) when appropriate**
# 

# In[ ]:


# Task 6.0 and 6.1
g.namespace_manager.bind('ontology', ontology, override=False)
g.namespace_manager.bind('person', person, override=False)

classes = [
    (ontology.Person, None, "Person"),
    (ontology.Professor, ontology.Person, "Professor"),
    (ontology.AssociateProfessor, ontology.Professor, "AssociateProfessor"),
    (ontology.InterimAssociateProfessor, ontology.AssociateProfessor, "InterimAssociateProfessor"),
    (ontology.FullProfessor, ontology.Professor, "FullProfessor"),
]

for cls, parent, label in classes:
    g.add((cls, RDF.type, RDFS.Class))
    g.add((cls, RDFS.label, Literal(label, datatype=XSD.string)))
    if parent is not None:
        g.add((cls, RDFS.subClassOf, parent))

for s, p, o in g:
    print(s, p, o)


# In[ ]:


# Validation. Do not remove
r.validate_task_06_01(g)


# **TASK 6.2: Add the 3 properties shown in slide 36. Add labels for each of them (exactly as they are in the slide, with no language tags), and their corresponding domains and ranges using RDFS. Remember adding the correct datatype (xsd:String) when appropriate. If a property has no range, make it a literal (string)**

# In[ ]:


# Task 6.2
properties = [
    (ontology.hasColleague, ontology.Person, ontology.Person, "hasColleague"),
    (ontology.hasName, ontology.Person, RDFS.Literal, "hasName"),
    (ontology.hasHomePage, ontology.FullProfessor, RDFS.Literal, "hasHomePage"),
]

for prop, domain, range_, label in properties:
    g.add((prop, RDF.type, RDF.Property))
    g.add((prop, RDFS.label, Literal(label, datatype=XSD.string)))
    g.add((prop, RDFS.domain, domain))
    g.add((prop, RDFS.range, range_))

for s, p, o in g:
    print(s, p, o)


# In[ ]:


# Validation. Do not remove
r.validate_task_06_02(g)


# **TASK 6.3: Create the individuals shown in slide 36 under "Datos". Link them with the same relationships shown in the diagram."**

# In[ ]:


# Task 6.3
asun = person.Asun
oscar = person.Oscar
raul = person.Raul

individuals = [
    (asun, ontology.FullProfessor, "Asun", [
        (ontology.hasHomePage, Literal("http://www.oeg-upm.net/", datatype=XSD.string)),
        (ontology.hasColleague, raul)
    ]),
    (oscar, ontology.AssociateProfessor, "Oscar", [
        (ontology.hasColleague, asun),
        (ontology.hasName, Literal("Oscar Corcho García", datatype=XSD.string))
    ]),
    (raul, ontology.InterimAssociateProfessor, "Raul", [
        (ontology.hasColleague, asun)
    ])
]

for individual, cls, label, statements in individuals:
    g.add((individual, RDF.type, cls))
    g.add((individual, RDFS.label, Literal(label, datatype=XSD.string)))
    for predicate, obj in statements:
        g.add((individual, predicate, obj))

for s, p, o in g:
    print(s, p, o)


# In[ ]:


r.validate_task_06_03(g)


# **TASK 6.4: Add to the individual person:Oscar the email address, given and family names. Use the properties already included in example 4 to describe Jane and John (https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/master/Assignment4/course_materials/rdf/example4.rdf). Do not import the namespaces, add them manually**
# 

# In[ ]:


# Task 6.4
VCARD = Namespace("http://www.w3.org/2001/vcard-rdf/3.0/")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")

g.namespace_manager.bind('vcard', VCARD, override=False)
g.namespace_manager.bind('foaf', FOAF, override=False)

oscar = person.Oscar
contact_details = [
    (VCARD.Given, Literal("Oscar", datatype=XSD.string)),
    (VCARD.Family, Literal("Corcho García", datatype=XSD.string)),
    (FOAF.email, Literal("oscar.corcho@example.org", datatype=XSD.string))
]

for predicate, obj in contact_details:
    g.add((oscar, predicate, obj))

for s, p, o in g:
    print(s, p, o)


# In[ ]:


# Validation. Do not remove
r.validate_task_06_04(g)
r.save_report("_Task_06")

