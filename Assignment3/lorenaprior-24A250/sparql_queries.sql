--- 1 ---
PREFIX dbo: <http://dbpedia.org/ontology/>

SELECT DISTINCT ?property
WHERE {
  ?s a dbo:Politician ;
     ?property ?o .
}


--- 2 ---
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT DISTINCT ?property
WHERE {
  ?s a dbo:Politician ;
     ?property ?o .
  FILTER (?property != rdf:type)
}


--- 3 ---
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT DISTINCT ?property ?value
WHERE {
  ?s a dbo:Politician ;
     ?property ?value .
  FILTER (?property != rdf:type)
}


--- 4 ---
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT DISTINCT ?property ?value
WHERE {
  ?s a dbo:Politician ;
     ?property ?value .
  FILTER (?property != rdf:type)
}
ORDER BY ?property ?value



--- 5 ---
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?property (COUNT(DISTINCT ?value) AS ?numValues)
WHERE {
  ?s a dbo:Politician ;
     ?property ?value .
  FILTER (?property != rdf:type)
}
GROUP BY ?property
ORDER BY DESC(?numValues)
