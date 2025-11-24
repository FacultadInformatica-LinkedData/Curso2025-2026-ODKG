from rdflib import Graph
g = Graph()
g.parse("knowledge-graph.nt", format="nt")
g.serialize("rdf/knowledge-graph.ttl", format="turtle")