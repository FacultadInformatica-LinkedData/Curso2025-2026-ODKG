# %% [markdown]
# **Task 06: Modifying RDF(s)**

# %%
#!pip install rdflib
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
g = Graph()

person = Namespace("http://oeg.fi.upm.es/def/people#")
ontology = Namespace("http://oeg.fi.upm.es/def/organization#")

g.namespace_manager.bind('person', person, override=True)
g.namespace_manager.bind('ontology', ontology, override=True)


# %% [markdown]
# **TASK 6.1: Reproduce the taxonomy of classes shown in slide 34 in class (all the classes under "Vocabulario", Slidedeck: 01a.RDF(s)-SPARQL). Add labels for each of them as they are in the diagram (exactly) with no language tags. Remember adding the correct datatype (xsd:String) when appropriate**
# 

# %%
# TO DO

g.add((person.Person, RDF.type, RDFS.Class))
g.add((person.Professor, RDF.type, RDFS.Class))
g.add((person.AssociateProfessor, RDF.type, RDFS.Class))
g.add((person.FullProfessor, RDF.type, RDFS.Class))
g.add((person.InterimAssociateProfessor, RDF.type, RDFS.Class))

# relations
g.add((person.Professor, RDFS.subClassOf, person.Person))
g.add((person.AssociateProfessor, RDFS.subClassOf, person.Professor))
g.add((person.FullProfessor, RDFS.subClassOf, person.Professor))
g.add((person.InterimAssociateProfessor, RDFS.subClassOf, person.AssociateProfessor))

# labels
g.add((person.Person, RDFS.label, Literal("Person", datatype=XSD.string)))
g.add((person.Professor, RDFS.label, Literal("Professor", datatype=XSD.string)))
g.add((person.AssociateProfessor, RDFS.label, Literal("AssociateProfessor", datatype=XSD.string)))
g.add((person.FullProfessor, RDFS.label, Literal("FullProfessor", datatype=XSD.string)))
g.add((person.InterimAssociateProfessor, RDFS.label, Literal("InterimAssociateProfessor", datatype=XSD.string)))


# Visualize the results
for s, p, o in g:
  print(s,p,o)

# %%
# Validation. Do not remove
r.validate_task_06_01(g)

# %% [markdown]
# **TASK 6.2: Add the 3 properties shown in slide 36. Add labels for each of them (exactly as they are in the slide, with no language tags), and their corresponding domains and ranges using RDFS. Remember adding the correct datatype (xsd:String) when appropriate. If a property has no range, make it a literal (string)**

# %%
# TO DO

# hasColleague
g.add((person.hasColleague, RDF.type, RDF.Property))
g.add((person.hasColleague, RDFS.label, Literal("hasColleague", datatype=XSD.string)))
g.add((person.hasColleague, RDFS.domain, person.Person))
g.add((person.hasColleague, RDFS.range, person.Person))

# hasName
g.add((person.hasName, RDF.type, RDF.Property))
g.add((person.hasName, RDFS.label, Literal("hasName", datatype=XSD.string)))
g.add((person.hasName, RDFS.domain, person.Person))
g.add((person.hasName, RDFS.range, RDFS.Literal))

# hasHomePage
g.add((person.hasHomePage, RDF.type, RDF.Property))
g.add((person.hasHomePage, RDFS.label, Literal("hasHomePage", datatype=XSD.string)))
g.add((person.hasHomePage, RDFS.domain, person.FullProfessor))
g.add((person.hasHomePage, RDFS.range, RDFS.Literal))


# Visualize the results
for s, p, o in g:
  print(s,p,o)

# %%
# Validation. Do not remove
r.validate_task_06_02(g)

# %% [markdown]
# **TASK 6.3: Create the individuals shown in slide 36 under "Datos". Link them with the same relationships shown in the diagram."**

# %%
# TO DO

person_ind = Namespace("http://oeg.fi.upm.es/resource/person/")

#delete old triples of def/people#:
for s in list(g.subjects(RDF.type, None)):
    if str(s).startswith("http://oeg.fi.upm.es/def/people#"):
        g.remove((s, None, None))

g.add((person_ind.Asun, RDF.type, person.FullProfessor))
g.add((person_ind.Asun, RDFS.label, Literal("Asun", datatype=XSD.string)))
g.add((person_ind.Asun, person.hasHomePage, Literal("http://www.oeg-upm.net/", datatype=XSD.string)))
g.add((person_ind.Asun, person.hasColleague, person_ind.Raul))

g.add((person_ind.Oscar, RDF.type, person.AssociateProfessor))
g.add((person_ind.Oscar, RDFS.label, Literal("Oscar", datatype=XSD.string)))
g.add((person_ind.Oscar, person.hasName, Literal("Oscar Corcho García", datatype=XSD.string)))
g.add((person_ind.Oscar, person.hasColleague, person_ind.Asun))

g.add((person_ind.Raul, RDF.type, person.InterimAssociateProfessor))
g.add((person_ind.Raul, RDFS.label, Literal("Raul", datatype=XSD.string)))


# Visualize the results
for s, p, o in g:
  print(s,p,o)

# %%
r.validate_task_06_03(g)

# %% [markdown]
# **TASK 6.4: Add to the individual person:Oscar the email address, given and family names. Use the properties already included in example 4 to describe Jane and John (https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/master/Assignment4/course_materials/rdf/example4.rdf). Do not import the namespaces, add them manually**
# 

# %%
# TO DO

VCARD = Namespace("http://www.w3.org/2001/vcard-rdf/3.0/")
FOAF  = Namespace("http://xmlns.com/foaf/0.1/")

g.add((person_ind.Oscar, VCARD.Given,  Literal("Oscar", datatype=XSD.string)))
g.add((person_ind.Oscar, VCARD.Family, Literal("Corcho", datatype=XSD.string)))
g.add((person_ind.Oscar, VCARD.FN,     Literal("Oscar Corcho García", datatype=XSD.string)))
g.add((person_ind.Oscar, FOAF.email,   Literal("ocorcho@fi.upm.es", datatype=XSD.string)))

# Visualize the results
for s, p, o in g:
  print(s,p,o)

# %%
# Validation. Do not remove
r.validate_task_06_04(g)
r.save_report("_Task_06")


