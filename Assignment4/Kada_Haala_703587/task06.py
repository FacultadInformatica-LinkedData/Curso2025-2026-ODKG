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

ontology = Namespace("http://oeg.fi.upm.es/def/people#")
person = Namespace("http://oeg.fi.upm.es/resource/person/")
g.bind("ontology", ontology)
g.bind("person", person)

g.add((ontology.Person, RDF.type, RDFS.Class))
g.add((ontology.Person, RDFS.label, Literal("Person", datatype=XSD.string)))
g.add((ontology.Professor, RDF.type, RDFS.Class))
g.add((ontology.Professor, RDFS.label, Literal("Professor", datatype=XSD.string)))
g.add((ontology.FullProfessor, RDF.type, RDFS.Class))
g.add((ontology.FullProfessor, RDFS.label, Literal("FullProfessor", datatype=XSD.string)))
g.add((ontology.AssociateProfessor, RDF.type, RDFS.Class))
g.add((ontology.AssociateProfessor, RDFS.label, Literal("AssociateProfessor", datatype=XSD.string)))
g.add((ontology.InterimAssociateProfessor, RDF.type, RDFS.Class))
g.add((ontology.InterimAssociateProfessor, RDFS.label, Literal("InterimAssociateProfessor", datatype=XSD.string)))


g.add((ontology.Professor, RDFS.subClassOf, ontology.Person))
g.add((ontology.FullProfessor, RDFS.subClassOf, ontology.Professor))
g.add((ontology.AssociateProfessor, RDFS.subClassOf, ontology.Professor))
g.add((ontology.InterimAssociateProfessor, RDFS.subClassOf, ontology.AssociateProfessor))

r.validate_task_06_01(g)



g.add((ontology.hasColleague, RDF.type, RDF.Property))
g.add((ontology.hasColleague, RDFS.label, Literal("hasColleague", datatype=XSD.string)))
g.add((ontology.hasColleague, RDFS.domain, ontology.Person))
g.add((ontology.hasColleague, RDFS.range, ontology.Person))

g.add((ontology.hasName, RDF.type, RDF.Property))
g.add((ontology.hasName, RDFS.label, Literal("hasName", datatype=XSD.string)))
g.add((ontology.hasName, RDFS.domain, ontology.Person))
g.add((ontology.hasName, RDFS.range, RDFS.Literal))

g.add((ontology.hasHomePage, RDF.type, RDF.Property))
g.add((ontology.hasHomePage, RDFS.label, Literal("hasHomePage", datatype=XSD.string)))
g.add((ontology.hasHomePage, RDFS.domain, ontology.FullProfessor))
g.add((ontology.hasHomePage, RDFS.range, RDFS.Literal))

r.validate_task_06_02(g)



g.add((person.Oscar, RDF.type, ontology.AssociateProfessor))
g.add((person.Oscar, RDFS.label, Literal("Oscar", datatype=XSD.string)))
g.add((person.Oscar, ontology.hasColleague, person.Asun))
g.add((person.Oscar, ontology.hasName, Literal("Oscar", datatype=XSD.string)))

g.add((person.Asun, RDF.type, ontology.FullProfessor))
g.add((person.Asun, RDFS.label, Literal("Asun", datatype=XSD.string)))
g.add((person.Asun, ontology.hasColleague, person.Raul))
g.add((person.Asun, ontology.hasHomePage, Literal("https://asun.homepage", datatype=XSD.string)))

g.add((person.Raul, RDF.type, ontology.InterimAssociateProfessor))
g.add((person.Raul, RDFS.label, Literal("Raul", datatype=XSD.string)))

r.validate_task_06_03(g)



VCARD = Namespace("http://www.w3.org/2001/vcard-rdf/3.0/")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")

g.add((person.Oscar, VCARD.Family, Literal("García", datatype=XSD.string)))
g.add((person.Oscar, VCARD.Given, Literal("García", datatype=XSD.string)))
g.add((person.Oscar, FOAF.email, Literal("García", datatype=XSD.string)))

# Validation. Do not remove
r.validate_task_06_04(g)
r.save_report("_Task_06")