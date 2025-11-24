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
    print(s, p, o)

# **Task 6.0: Create new prefixes for "ontology" and "person" as shown in slide 14**

# this task is validated in the next step

print("For this part I just copied the slide 14")
Ontology = Namespace("http://oeg.fi.upm.es/def/people#")
Person = Namespace("http://oeg.fi.upm.es/resource/person/")

g.bind("people", Person)
g.bind("ontology", Ontology)

# **TASK 6.1: Reproduce the taxonomy of classes shown in slide 34**

# TO DO

print("I'll start by adding our 5 classes")

Class_Person = Ontology.Person
Class_Professor = Ontology.Professor
Class_FullProfessor = Ontology.FullProfessor
Class_AssociateProfessor = Ontology.AssociateProfessor
Class_InterimAssociateProfessor = Ontology.InterimAssociateProfessor

print("Now Adding them with their type to g")

g.add((Class_Person, RDF.type, RDFS.Class))
g.add((Class_Professor, RDF.type, RDFS.Class))
g.add((Class_FullProfessor, RDF.type, RDFS.Class))
g.add((Class_AssociateProfessor, RDF.type, RDFS.Class))
g.add((Class_InterimAssociateProfessor, RDF.type, RDFS.Class))

print("And here I'll add their label")

g.add((Class_Person, RDFS.label, Literal('Person', datatype=XSD.string)))
g.add((Class_Professor, RDFS.label, Literal('Professor', datatype=XSD.string)))
g.add((Class_FullProfessor, RDFS.label, Literal('FullProfessor', datatype=XSD.string)))
g.add((Class_AssociateProfessor, RDFS.label, Literal('AssociateProfessor', datatype=XSD.string)))
g.add((Class_InterimAssociateProfessor, RDFS.label, Literal('InterimAssociateProfessor', datatype=XSD.string)))

print("Now I'll precise their position in the hierarchy")

g.add((Class_Person, RDF.type, RDFS.Class))
g.add((Class_Professor, RDFS.subClassOf, Class_Person))
g.add((Class_FullProfessor, RDFS.subClassOf, Class_Professor))
g.add((Class_AssociateProfessor, RDFS.subClassOf, Class_Professor))
g.add((Class_InterimAssociateProfessor, RDFS.subClassOf, Class_AssociateProfessor))

for s, p, o in g:
    print(s, p, o)

# Validation. Do not remove
r.validate_task_06_01(g)

# **TASK 6.2: Add the 3 properties shown in slide 36**

print("Now I'll add the three properties")

g.add((Ontology.hasColleague, RDF.type, RDF.Property))
g.add((Ontology.hasHomePage, RDF.type, RDF.Property))
g.add((Ontology.hasName, RDF.type, RDF.Property))

print("And now their label")

g.add((Ontology.hasColleague, RDFS.label, Literal("hasColleague", datatype=XSD.string)))
g.add((Ontology.hasHomePage, RDFS.label, Literal("hasHomePage", datatype=XSD.string)))
g.add((Ontology.hasName, RDFS.label, Literal("hasName", datatype=XSD.string)))

print("Last but not least, range and domains")

g.add((Ontology.hasColleague, RDFS.domain, Class_Person))
g.add((Ontology.hasColleague, RDFS.range, Class_Person))

g.add((Ontology.hasName, RDFS.domain, Class_Person))
g.add((Ontology.hasName, RDFS.range, RDFS.Literal))

g.add((Ontology.hasHomePage, RDFS.domain, Class_FullProfessor))
g.add((Ontology.hasHomePage, RDFS.range, RDFS.Literal))

# Visualize the results
for s, p, o in g:
    print(s, p, o)

# Validation. Do not remove
r.validate_task_06_02(g)

# **TASK 6.3: Create the individuals shown in slide 36**
print("I'll start by adding our 3 individuals")

g.add((Person.Oscar, RDF.type, Class_AssociateProfessor))
g.add((Person.Asun, RDF.type, Class_FullProfessor))
g.add((Person.Raul, RDF.type, Class_InterimAssociateProfessor))

print("Now I'll add their label")

g.add((Person.Oscar, RDFS.label, Literal("Oscar", datatype=XSD.string)))
g.add((Person.Asun, RDFS.label, Literal("Asun", datatype=XSD.string)))
g.add((Person.Raul, RDFS.label, Literal("Raul", datatype=XSD.string)))

print("And to finish I'll add their respective properties")

g.add((Person.Oscar, Ontology.hasName, Literal("Óscar Corcho García", datatype=XSD.string)))
g.add((Person.Oscar, Ontology.hasColleague, Person.Asun))

g.add((Person.Asun, Ontology.hasHomePage, Literal("http://www.oeg-upm.net/", datatype=XSD.string)))
g.add((Person.Asun, Ontology.hasColleague, Person.Raul))

# Visualize
for s, p, o in g:
    print(s, p, o)

# Validation
r.validate_task_06_03(g)

# **TASK 6.4: Add email, given name, family name using VCARD and FOAF**
print("I'll start by preparing each property")

VCARD = Namespace("http://www.w3.org/2001/vcard-rdf/3.0/")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")

g.add((Person.Oscar, VCARD.Given, Literal("Corcho", datatype=XSD.string)))
g.add((Person.Oscar, VCARD.Family, Literal("García", datatype=XSD.string)))
g.add((Person.Oscar, FOAF.email, Literal("oscar.corcho.garcia@upm.es")))

# Visualize
for s, p, o in g:
    print(s, p, o)

# Validation. Do not remove
r.validate_task_06_04(g)
r.save_report("_Task_06")
