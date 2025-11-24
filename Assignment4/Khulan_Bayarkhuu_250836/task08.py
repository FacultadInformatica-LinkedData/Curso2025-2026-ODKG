# %% [markdown]
# **Task 08: Completing missing data**

# %%
# !pip install rdflib
github_storage = "https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2021-2022/master/Assignment4/course_materials"

# %%
from rdflib import Graph, Namespace, Literal, URIRef
g1 = Graph()
g2 = Graph()
g1.parse(github_storage+"/rdf/data01.rdf", format="xml")
g2.parse(github_storage+"/rdf/data02.rdf", format="xml")

# %% [markdown]
# Tarea: lista todos los elementos de la clase Person en el primer grafo (data01.rdf) y completa los campos (given name, family name y email) que puedan faltar con los datos del segundo grafo (data02.rdf). Puedes usar consultas SPARQL o iterar el grafo, o ambas cosas.

# %% [markdown]
# == Aufgabe: Liste alle Elemente der Klasse Person im ersten Graphen (data01.rdf) auf und fülle die Felder (Vorname, Nachname und E-Mail-Adresse), die möglicherweise fehlen, mit den Daten aus dem zweiten Graphen (data02.rdf) aus. Du kannst SPARQL-Abfragen verwenden oder den Graphen durchlaufen, oder beides.

# %%
from rdflib.namespace import RDF

VCARD = Namespace("http://www.w3.org/2001/vcard-rdf/3.0#")
NS = Namespace("http://data.org#")

for s in g1.subjects(RDF.type, NS.Person):
    if (s, None, None) in g2:
        for p in [VCARD.Given, VCARD.Family, VCARD.EMAIL]:
            if not (s, p, None) in g1:
                if g2.value(s, p):
                    g1.add((s, p, g2.value(s, p)))

# visualize the updated graph
for s, p, o in g1:
    print(s, p, o)


