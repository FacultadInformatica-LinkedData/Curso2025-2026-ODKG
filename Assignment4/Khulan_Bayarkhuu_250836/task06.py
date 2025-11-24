# %% [markdown]
# **Task 06: Modifying RDF(s)**

# %%
# !pip install rdflib
import urllib.request
url = 'https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/refs/heads/master/Assignment4/course_materials/python/validation.py'
urllib.request.urlretrieve(url, 'validation.py')
github_storage = "https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/master/Assignment4/course_materials" 

# %% [markdown]
# Import RDFLib main methods

# %%
from rdflib import Graph, Namespace, Literal, XSD
from rdflib.namespace import RDF, RDFS
from validation import Report
g = Graph()
g.namespace_manager.bind('ns', Namespace("http://somewhere#"), override=False)
r = Report()

# %% [markdown]
# Create a new class named Researcher

# %%
ns = Namespace("http://mydomain.org#")
g.add((ns.Researcher, RDF.type, RDFS.Class))
for s, p, o in g:
  print(s,p,o)

# %% [markdown]
# **Task 6.0: Create new prefixes for "ontology" and "person" as shown in slide 14 of the Slidedeck 01a.RDF(s)-SPARQL shown in class.**

# %%
# this task is validated in the next step
from rdflib import Graph, Namespace, Literal
g = Graph()


PERSON = Namespace("http://oeg.fi.upm.es/resource/person/")
ONTOLOGY = Namespace("http://oeg.fi.upm.es/def/people#")
# RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
# RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
# XSD = Namespace("http://www.w3.org/2001/XMLSchema#")

g.bind("person", PERSON)
g.bind("ontology", ONTOLOGY)
# g.bind("organization", ORGANIZATION)

# %% [markdown]
# **TASK 6.1: Reproduce the taxonomy of classes shown in slide 34 in class (all the classes under "Vocabulario", Slidedeck: 01a.RDF(s)-SPARQL). Add labels for each of them as they are in the diagram (exactly) with no language tags. Remember adding the correct datatype (xsd:String) when appropriate**
# 

# %%

g.add((ONTOLOGY.person, RDF.type, RDFS.Class))
g.add((ONTOLOGY.Professor, RDF.type, RDFS.Class))
g.add((ONTOLOGY.AssociateProfessor, RDF.type, RDFS.Class))
g.add((ONTOLOGY.InterimAssociateProfessor, RDF.type, RDFS.Class))
g.add((ONTOLOGY.FullProfessor, RDF.type, RDFS.Class))

g.add((ONTOLOGY.Professor, RDFS.subClassOf, ONTOLOGY.Person))
g.add((ONTOLOGY.AssociateProfessor, RDFS.subClassOf, ONTOLOGY.Professor))
g.add((ONTOLOGY.InterimAssociateProfessor, RDFS.subClassOf, ONTOLOGY.AssociateProfessor))
g.add((ONTOLOGY.FullProfessor, RDFS.subClassOf, ONTOLOGY.Professor))

g.add((ONTOLOGY.Person, RDFS.label, Literal("Person", datatype=XSD.string)))
g.add((ONTOLOGY.Professor, RDFS.label, Literal("Professor", datatype=XSD.string)))
g.add((ONTOLOGY.AssociateProfessor, RDFS.label, Literal("AssociateProfessor", datatype=XSD.string)))
g.add((ONTOLOGY.InterimAssociateProfessor, RDFS.label, Literal("InterimAssociateProfessor", datatype=XSD.string)))
g.add((ONTOLOGY.FullProfessor, RDFS.label, Literal("FullProfessor", datatype=XSD.string)))


# Visualize the results
for s, p, o in g:
  print(s,p,o)

# %%
r.validate_task_06_01(g)

# %% [markdown]
# **TASK 6.2: Add the 3 properties shown in slide 36. Add labels for each of them (exactly as they are in the slide, with no language tags), and their corresponding domains and ranges using RDFS. Remember adding the correct datatype (xsd:String) when appropriate. If a property has no range, make it a literal (string)**

# %%
g.add((ONTOLOGY.hasName, RDF.type, RDF.Property))
g.add((ONTOLOGY.hasColleague, RDF.type, RDF.Property))
g.add((ONTOLOGY.hasHomePage, RDF.type, RDF.Property))

g.add((ONTOLOGY.hasName, RDFS.label, Literal("hasName", datatype=XSD.string)))
g.add((ONTOLOGY.hasColleague, RDFS.label, Literal("hasColleague", datatype=XSD.string)))
g.add((ONTOLOGY.hasHomePage, RDFS.label, Literal("hasHomePage", datatype=XSD.string)))

g.add((ONTOLOGY.hasName, RDFS.range, RDFS.Literal))
g.add((ONTOLOGY.hasName, RDFS.domain, ONTOLOGY.Person))

g.add((ONTOLOGY.hasColleague, RDFS.domain, ONTOLOGY.Person))
g.add((ONTOLOGY.hasColleague, RDFS.range, ONTOLOGY.Person))

g.add((ONTOLOGY.hasHomePage, RDFS.range, RDFS.Literal))
g.add((ONTOLOGY.hasHomePage, RDFS.domain, ONTOLOGY.FullProfessor))

# Visualize the results
for s, p, o in g:
  print(s,p,o)

# %%
# Validation. Do not remove
r.validate_task_06_02(g)

# %% [markdown]
# **TASK 6.3: Create the individuals shown in slide 36 under "Datos". Link them with the same relationships shown in the diagram."**

# %%
# Instancia

g.add((PERSON.Oscar, RDF.type, ONTOLOGY.AssociateProfessor))
g.add((PERSON.Asun, RDF.type, ONTOLOGY.FullProfessor))
g.add((PERSON.Raul, RDF.type, ONTOLOGY.InterimAssociateProfessor))

g.add((PERSON.Oscar, RDFS.label, Literal("Oscar", datatype=XSD.string)))
g.add((PERSON.Asun, RDFS.label, Literal("Asun", datatype=XSD.string)))
g.add((PERSON.Raul, RDFS.label, Literal("Raul", datatype=XSD.string)))

fullName = Literal("Óscar Corcho García", datatype=XSD.string)
homepage = Literal("http://www.oeg.fi.upm.es/", datatype=XSD.string)

g.add((PERSON.Oscar, ONTOLOGY.hasName, fullName))
g.add((PERSON.Oscar, ONTOLOGY.hasColleague, PERSON.Asun))
g.add((PERSON.Asun, ONTOLOGY.hasColleague, PERSON.Raul))
g.add((PERSON.Asun, ONTOLOGY.hasHomePage, homepage))

# Visualize the results
for s, p, o in g:
  print(s,p,o)

# %%
r.validate_task_06_03(g)

# %% [markdown]
# **TASK 6.4: Add to the individual person:Oscar the email address, given and family names. Use the properties already included in example 4 to describe Jane and John (https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/master/Assignment4/course_materials/rdf/example4.rdf). Do not import the namespaces, add them manually**
# 

# %%
VCARD = Namespace("http://www.w3.org/2001/vcard-rdf/3.0/")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
g.bind('vcard', VCARD)
g.bind('foaf', FOAF)

g.add((PERSON.Oscar, VCARD.Given, Literal("Óscar", datatype=XSD.string)))
g.add((PERSON.Oscar, VCARD.Family, Literal("Corcho García", datatype=XSD.string)))
g.add((PERSON.Oscar, VCARD.FN, Literal("Óscar Corcho García", datatype=XSD.string)))
g.add((PERSON.Oscar, FOAF.email, Literal("oscar.corcho@upm.es", datatype=XSD.string)))


# Visualize the results
for s, p, o in g:
  print(s,p,o)

# %%
# Validation. Do not remove
r.validate_task_06_04(g)
r.save_report("_Task_06")


