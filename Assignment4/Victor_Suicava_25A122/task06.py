# **Task 06: Modifying RDF(s)**

#!pip install rdflib
import urllib.request
url = 'https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/refs/heads/master/Assignment4/course_materials/python/validation.py'
urllib.request.urlretrieve(url, 'validation.py')
github_storage = "https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/master/Assignment4/course_materials"

# Import RDFLib main methods

from rdflib import Graph, Namespace, Literal, XSD
from rdflib.namespace import RDF, RDFS
from validation import Report
g = Graph()
g.namespace_manager.bind('ns', Namespace("http://somewhere#"), override=False)
r = Report()

# Create a new class named Researcher

ns = Namespace("http://mydomain.org#")
g.add((ns.Researcher, RDF.type, RDFS.Class))
for s, p, o in g:
  print(s,p,o)

# **Task 6.0: Create new prefixes for "ontology" and "person" as shown in slide 14 of the Slidedeck 01a.RDF(s)-SPARQL shown in class.**

# this task is validated in the next step

person = Namespace("http://oeg.fi.upm.es/def/people#")

data   = Namespace("http://oeg.fi.upm.es/resource/person/")

g.namespace_manager.bind("person", person, override=True)
g.namespace_manager.bind("data",   data,   override=True)
g.namespace_manager.bind("rdf",    RDF,    override=True)
g.namespace_manager.bind("rdfs",   RDFS,   override=True)
g.namespace_manager.bind("xsd",    XSD,    override=True)

# **TASK 6.1: Reproduce the taxonomy of classes shown in slide 34 in class (all the classes under "Vocabulario", Slidedeck: 01a.RDF(s)-SPARQL). Add labels for each of them as they are in the diagram (exactly) with no language tags. Remember adding the correct datatype (xsd:String) when appropriate**
# 

# TO DO

g.add((person.Person,                    RDF.type, RDFS.Class))
g.add((person.Professor,                 RDF.type, RDFS.Class))
g.add((person.AssociateProfessor,        RDF.type, RDFS.Class))
g.add((person.InterimAssociateProfessor, RDF.type, RDFS.Class))
g.add((person.FullProfessor,             RDF.type, RDFS.Class))

g.add((person.Professor,                 RDFS.subClassOf, person.Person))
g.add((person.AssociateProfessor,        RDFS.subClassOf, person.Professor))
g.add((person.InterimAssociateProfessor, RDFS.subClassOf, person.AssociateProfessor))
g.add((person.FullProfessor,             RDFS.subClassOf, person.Professor))

g.add((person.Person,                    RDFS.label, Literal("Person", datatype=XSD.string)))
g.add((person.Professor,                 RDFS.label, Literal("Professor", datatype=XSD.string)))
g.add((person.AssociateProfessor,        RDFS.label, Literal("AssociateProfessor", datatype=XSD.string)))
g.add((person.InterimAssociateProfessor, RDFS.label, Literal("InterimAssociateProfessor", datatype=XSD.string)))
g.add((person.FullProfessor,             RDFS.label, Literal("FullProfessor", datatype=XSD.string)))
g.add((ns.Researcher, RDFS.label, Literal("Researcher", datatype=XSD.string)))

# Visualize the results
for s, p, o in g:
  print(s,p,o)





# Validation. Do not remove
r.validate_task_06_01(g)

# **TASK 6.2: Add the 3 properties shown in slide 36. Add labels for each of them (exactly as they are in the slide, with no language tags), and their corresponding domains and ranges using RDFS. Remember adding the correct datatype (xsd:String) when appropriate. If a property has no range, make it a literal (string)**

# TO DO

g.set((person.hasColleague, RDF.type, RDF.Property))
g.set((person.hasName,      RDF.type, RDF.Property))
g.set((person.hasHomePage,  RDF.type, RDF.Property))

g.set((person.hasColleague, RDFS.domain, person.Person))
g.set((person.hasName,      RDFS.domain, person.Person))
g.set((person.hasHomePage,  RDFS.domain, person.FullProfessor))

g.set((person.hasColleague, RDFS.range,  person.Person))
g.set((person.hasName,      RDFS.range,  RDFS.Literal))
g.set((person.hasHomePage,  RDFS.range,  RDFS.Literal))

g.set((person.hasColleague, RDFS.label, Literal("hasColleague", datatype=XSD.string)))
g.set((person.hasName,      RDFS.label, Literal("hasName",      datatype=XSD.string)))
g.set((person.hasHomePage,  RDFS.label, Literal("hasHomePage",  datatype=XSD.string)))

# Visualize the results
for s, p, o in g:
  print(s,p,o)

# Validation. Do not remove
r.validate_task_06_02(g)

# **TASK 6.3: Create the individuals shown in slide 36 under "Datos". Link them with the same relationships shown in the diagram."**

# TO DO

oscar = data.Oscar
asun  = data.Asun
raul  = data.Raul

g.add((oscar, RDF.type, person.Person))
g.add((asun,  RDF.type, person.Person))
g.add((raul,  RDF.type, person.Person))

g.add((oscar, RDFS.label, Literal("Oscar", datatype=XSD.string)))
g.add((asun,  RDFS.label, Literal("Asun",  datatype=XSD.string)))
g.add((raul,  RDFS.label, Literal("Raul",  datatype=XSD.string)))

g.add((oscar, person.hasColleague, asun))
g.add((asun,  person.hasColleague, raul))

g.add((oscar, person.hasName,     Literal("Óscar Corcho García", datatype=XSD.string)))
g.add((asun,  person.hasHomePage, Literal("http://www.oeg-upm.net/", datatype=XSD.string)))

# Visualize the results
for s, p, o in g:
  print(s,p,o)

r.validate_task_06_03(g)

# **TASK 6.4: Add to the individual person:Oscar the email address, given and family names. Use the properties already included in example 4 to describe Jane and John (https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/master/Assignment4/course_materials/rdf/example4.rdf). Do not import the namespaces, add them manually**
# 

# TO DO

VCARD = Namespace("http://www.w3.org/2001/vcard-rdf/3.0/")
FOAF  = Namespace("http://xmlns.com/foaf/0.1/")

g.add((data.Oscar, VCARD.Given,  Literal("Oscar",  datatype=XSD.string)))
g.add((data.Oscar, VCARD.Family, Literal("Corcho", datatype=XSD.string)))
g.add((data.Oscar, FOAF.email,   Literal("oscar@oeg-upm.net", datatype=XSD.string)))

# Visualize the results
for s, p, o in g:
  print(s,p,o)

# Validation. Do not remove
r.validate_task_06_04(g)
r.save_report("_Task_06")


