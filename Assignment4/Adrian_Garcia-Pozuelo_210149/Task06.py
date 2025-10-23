# **Task 06: Modifying RDF(s)**


import urllib.request
from rdflib import Graph, Namespace, Literal, XSD
from rdflib.namespace import RDF, RDFS
from validation import Report


url = 'https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/refs/heads/master/Assignment4/course_materials/python/validation.py'
urllib.request.urlretrieve(url, 'validation.py')
github_storage = "https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/master/Assignment4/course_materials"

# Import RDFLib main methods


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

ONTOLOGY = Namespace("http://oeg.fi.upm.es/resource/person/")
PERSON = Namespace("http://oeg.fi.upm.es/def/people#")

g.namespace_manager.bind('ontology', ONTOLOGY, override=False)
g.namespace_manager.bind('person', PERSON, override=False)

# **TASK 6.1: Reproduce the taxonomy of classes shown in slide 34 in class (all the classes under "Vocabulario", Slidedeck: 01a.RDF(s)-SPARQL). Add labels for each of them as they are in the diagram (exactly) with no language tags. Remember adding the correct datatype (xsd:String) when appropriate**
# 
# TO DO
# rdf:type
g.add((PERSON.Person, RDF.type, RDFS.Class))
g.add((PERSON.Professor, RDF.type, RDFS.Class))
g.add((PERSON.FullProfessor, RDF.type, RDFS.Class))
g.add((PERSON.AssociateProfessor, RDF.type, RDFS.Class))
g.add((PERSON.InterimAssociateProfessor, RDF.type, RDFS.Class))

# rdfs:subClassOf
g.add((PERSON.Professor, RDFS.subClassOf, PERSON.Person))
g.add((PERSON.FullProfessor, RDFS.subClassOf, PERSON.Professor))
g.add((PERSON.AssociateProfessor, RDFS.subClassOf, PERSON.Professor))
g.add((PERSON.InterimAssociateProfessor, RDFS.subClassOf, PERSON.AssociateProfessor))

# datatypes
g.add((PERSON.Person, RDFS.label, Literal("Person", datatype=XSD.string)))
g.add((PERSON.Professor, RDFS.label, Literal("Professor", datatype=XSD.string)))
g.add((PERSON.FullProfessor, RDFS.label, Literal("FullProfessor", datatype=XSD.string)))
g.add((PERSON.AssociateProfessor, RDFS.label, Literal("AssociateProfessor", datatype=XSD.string)))
g.add((PERSON.InterimAssociateProfessor, RDFS.label, Literal("InterimAssociateProfessor", datatype=XSD.string)))


# Visualize the results
for s, p, o in g:
  print(s,p,o)


# Validation. Do not remove
r.validate_task_06_01(g)

# **TASK 6.2: Add the 3 properties shown in slide 36. Add labels for each of them (exactly as they are in the slide, with no language tags), and their corresponding domains and ranges using RDFS. Remember adding the correct datatype (xsd:String) when appropriate. If a property has no range, make it a literal (string)**


# TO DO
# rdf:type, range, domain
g.add((PERSON.hasName, RDF.type, RDF.Property))
g.add((PERSON.hasName, RDFS.range, RDFS.Literal))
g.add((PERSON.hasName, RDFS.domain, PERSON.Person))

g.add((PERSON.hasColleague, RDF.type, RDF.Property))
g.add((PERSON.hasColleague, RDFS.range, PERSON.Person))
g.add((PERSON.hasColleague, RDFS.domain, PERSON.Person))

g.add((PERSON.hasHomePage, RDF.type, RDF.Property))
g.add((PERSON.hasHomePage, RDFS.domain, PERSON.FullProfessor))
g.add((PERSON.hasHomePage, RDFS.range,  RDFS.Literal))

# datatypes
g.add((PERSON.hasName, RDFS.label, Literal("hasName", datatype=XSD.string)))
g.add((PERSON.hasColleague, RDFS.label, Literal("hasColleague", datatype=XSD.string)))
g.add((PERSON.hasHomePage, RDFS.label, Literal("hasHomePage", datatype=XSD.string)))


# Visualize the results
for s, p, o in g:
  print(s,p,o)


# Validation. Do not remove
r.validate_task_06_02(g)


# **TASK 6.3: Create the individuals shown in slide 36 under "Datos". Link them with the same relationships shown in the diagram."**


# TO DO
# rdf:type
g.add((ONTOLOGY.Oscar, RDF.type, PERSON.AssociateProfessor))
g.add((ONTOLOGY.Asun, RDF.type, PERSON.FullProfessor))
g.add((ONTOLOGY.Raul, RDF.type, PERSON.InterimAssociateProfessor))

g.add((ONTOLOGY.Oscar, RDFS.label, Literal("Oscar", datatype=XSD.string)))
g.add((ONTOLOGY.Asun,  RDFS.label, Literal("Asun",  datatype=XSD.string)))
g.add((ONTOLOGY.Raul,  RDFS.label, Literal("Raul",  datatype=XSD.string)))

# relations
g.add((ONTOLOGY.Oscar, PERSON.hasColleague, ONTOLOGY.Asun))
g.add((ONTOLOGY.Oscar, PERSON.hasName, Literal("Óscar Corcho García")))
g.add((ONTOLOGY.Asun,  PERSON.hasColleague, ONTOLOGY.Raul))
g.add((ONTOLOGY.Asun,  PERSON.hasHomePage, Literal("http://www.oeg-upm.net/")))

# Visualize the results
for s, p, o in g:
  print(s,p,o)


r.validate_task_06_03(g)


# **TASK 6.4: Add to the individual person:Oscar the email address, given and family names. Use the properties already included in example 4 to describe Jane and John (https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/master/Assignment4/course_materials/rdf/example4.rdf). Do not import the namespaces, add them manually**
# 


# TO DO
VCARD = Namespace("http://www.w3.org/2001/vcard-rdf/3.0/")
FOAF  = Namespace("http://xmlns.com/foaf/0.1/")

g.namespace_manager.bind('vcard', VCARD, override=False)
g.namespace_manager.bind('foaf',  FOAF,  override=False)


g.add((ONTOLOGY.Oscar, VCARD.Given,  Literal("Óscar")))
g.add((ONTOLOGY.Oscar, VCARD.Family, Literal("Corcho García")))
g.add((ONTOLOGY.Oscar, FOAF.email,   Literal("ocorcho@fi.upm.es")))

# Visualize the results
for s, p, o in g:
  print(s,p,o)


# Validation. Do not remove
r.validate_task_06_04(g)
r.save_report("_Task_06")


