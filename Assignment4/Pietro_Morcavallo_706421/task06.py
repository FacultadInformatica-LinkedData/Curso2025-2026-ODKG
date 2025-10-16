#task06.py
# **Task 06: Modifying RDF(s)**

#!pip install rdflib
import urllib.request
url = 'https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/refs/heads/master/Assignment4/course_materials/python/validation.py'
urllib.request.urlretrieve(url, 'validation.py')
github_storage = "https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/master/Assignment4/course_materials"


from rdflib import Graph, Namespace, Literal, XSD
from rdflib.namespace import RDF, RDFS
from validation import Report
g = Graph()
g.namespace_manager.bind('ns', Namespace("http://somewhere#"), override=False)
r = Report()


ns = Namespace("http://mydomain.org#")
g.add((ns.Researcher, RDF.type, RDFS.Class))
for s, p, o in g:
  print(s,p,o)


# **Task 6.0: Create new prefixes for "ontology" and "person" as shown in slide 14 of the Slidedeck 01a.RDF(s)-SPARQL shown in class.**

ontology = Namespace("http://oeg.fi.upm.es/def/people#")
person   = Namespace("http://oeg.fi.upm.es/resource/person/")

g.namespace_manager.bind("ontology", ontology, override=False)
g.namespace_manager.bind("person",   person,   override=False)

# TASK 6.1

# Classi
g.add((ontology.Person,                  RDF.type, RDFS.Class))
g.add((ontology.Professor,               RDF.type, RDFS.Class))
g.add((ontology.AssociateProfessor,      RDF.type, RDFS.Class))
g.add((ontology.InterimAssociateProfessor,RDF.type, RDFS.Class))
g.add((ontology.FullProfessor,           RDF.type, RDFS.Class))

# Gerarchia
g.add((ontology.Professor,               RDFS.subClassOf, ontology.Person))
g.add((ontology.AssociateProfessor,      RDFS.subClassOf, ontology.Professor))
g.add((ontology.InterimAssociateProfessor,RDFS.subClassOf, ontology.AssociateProfessor))
g.add((ontology.FullProfessor,           RDFS.subClassOf, ontology.Professor))

# Etichette (xsd:string)
g.add((ontology.Person,                   RDFS.label, Literal("Person", datatype=XSD.string)))
g.add((ontology.Professor,                RDFS.label, Literal("Professor", datatype=XSD.string)))
g.add((ontology.AssociateProfessor,       RDFS.label, Literal("AssociateProfessor", datatype=XSD.string)))
g.add((ontology.InterimAssociateProfessor,RDFS.label, Literal("InterimAssociateProfessor", datatype=XSD.string)))
g.add((ontology.FullProfessor,            RDFS.label, Literal("FullProfessor", datatype=XSD.string)))

# Visualize the results
for s, p, o in g:
  print(s,p,o)

# %%
# Validation. Do not remove
r.validate_task_06_01(g)


# TASK 6.2

# Proprietà
g.add((ontology.hasColleague, RDF.type, RDF.Property))
g.add((ontology.hasName,      RDF.type, RDF.Property))
g.add((ontology.hasHomePage,  RDF.type, RDF.Property))

# Label (xsd:string)
g.add((ontology.hasColleague, RDFS.label, Literal("hasColleague", datatype=XSD.string)))
g.add((ontology.hasName,      RDFS.label, Literal("hasName", datatype=XSD.string)))
g.add((ontology.hasHomePage,  RDFS.label, Literal("hasHomePage", datatype=XSD.string)))

# Domini e range
g.add((ontology.hasColleague, RDFS.domain, ontology.Person))
g.add((ontology.hasColleague, RDFS.range,  ontology.Person))

g.add((ontology.hasName,      RDFS.domain, ontology.Person))
g.add((ontology.hasName,      RDFS.range,  RDFS.Literal))

g.add((ontology.hasHomePage,  RDFS.domain, ontology.FullProfessor))
g.add((ontology.hasHomePage,  RDFS.range,  RDFS.Literal))


# Visualize the results
for s, p, o in g:
  print(s,p,o)

# Validation. Do not remove
r.validate_task_06_02(g)


# TASK 6.3

# Individui (namespace "person")
oscar = person.Oscar
asun  = person.Asun
raul  = person.Raul

# Tipi coerenti con i domini
g.add((oscar, RDF.type, ontology.Person))
g.add((asun,  RDF.type, ontology.FullProfessor))  # così hasHomePage è semanticamente valido
g.add((raul,  RDF.type, ontology.Person))

# Etichette
g.add((oscar, RDFS.label, Literal("Oscar", datatype=XSD.string)))
g.add((asun,  RDFS.label, Literal("Asun",  datatype=XSD.string)))
g.add((raul,  RDFS.label, Literal("Raul",  datatype=XSD.string)))

# Relazioni dal diagramma
g.add((oscar, ontology.hasColleague, asun))
g.add((asun,  ontology.hasColleague, oscar))
g.add((asun,  ontology.hasHomePage,  Literal("https://example.org/asun", datatype=XSD.string)))
g.add((oscar, ontology.hasName,      Literal("Oscar", datatype=XSD.string)))

# Visualize the results
for s, p, o in g:
  print(s,p,o)

r.validate_task_06_03(g)

#TASK 6.4 

from rdflib import URIRef

VCARD = Namespace("http://www.w3.org/2001/vcard-rdf/3.0/")
FOAF  = Namespace("http://xmlns.com/foaf/0.1/")
g.namespace_manager.bind("vcard", VCARD, override=False)
g.namespace_manager.bind("foaf",  FOAF,  override=False)

# rimuovi eventuale mbox aggiunto prima
g.remove((oscar, FOAF.mbox, None))

# nomi vCard
g.add((oscar, VCARD.Given,  Literal("Oscar", datatype=XSD.string)))
g.add((oscar, VCARD.Family, Literal("Smith", datatype=XSD.string)))  # cambia cognome se necessario

# email foaf:email come literal xsd:string (non mailto:)
g.add((oscar, FOAF.email, Literal("oscar@example.org", datatype=XSD.string)))

# Visualize the results
for s, p, o in g:
  print(s,p,o)

# %%
# Validation. Do not remove
r.validate_task_06_04(g)
r.save_report("_Task_06")


