# %% [markdown]
# **Task 09: Data linking**

# %%
# !pip install rdflib
github_storage = "https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2021-2022/master/Assignment4/course_materials/"

# %%
from rdflib import Graph, Namespace, Literal, URIRef
g1 = Graph()
g2 = Graph()
g3 = Graph()
g1.parse(github_storage+"rdf/data03.rdf", format="xml")
g2.parse(github_storage+"rdf/data04.rdf", format="xml")

# %% [markdown]
# Busca individuos en los dos grafos y enlázalos mediante la propiedad OWL:sameAs, inserta estas coincidencias en g3. Consideramos dos individuos iguales si tienen el mismo apodo y nombre de familia. Ten en cuenta que las URI no tienen por qué ser iguales para un mismo individuo en los dos grafos.

# %% [markdown]
# == Suche nach Individuen in beiden Graphen und verknüpfe sie mithilfe der OWL-Eigenschaft „sameAs”. Füge diese Übereinstimmungen in g3 ein. Wir betrachten zwei Individuen als gleich, wenn sie denselben Spitznamen und denselben Familiennamen haben. Beachte, dass die URIs für dasselbe Individuum in beiden Graphen nicht unbedingt identisch sein müssen.

# %%
VCARD = Namespace("http://www.w3.org/2001/vcard-rdf/3.0#")
from rdflib.namespace import OWL

def extract_people(graph):
    people = []
    for person in set(graph.subjects(VCARD.FN, None)):
        fn = graph.value(person, VCARD.FN)
        fam = graph.value(person, VCARD.Family)
        if fn is not None and fam is not None:
            people.append((person, fn, fam))
    return people

for uri1, fn1, fam1 in extract_people(g1):
    for uri2, fn2, fam2 in extract_people(g2):
        if (fn1 == fn2 and fam1 == fam2):
            g3.add((URIRef(uri1), OWL.sameAs, URIRef(uri2)))

for s, p, o in g3:
    print(s, p, o)


