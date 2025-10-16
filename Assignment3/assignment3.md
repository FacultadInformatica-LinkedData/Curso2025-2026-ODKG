# Assignment 3 - Politician Class Analysis with SPARQL

## Description
Create SPARQL queries and provide results for the following queries expressed in natural language. The endpoint used for this exercise is: http://es.dbpedia.org/sparql

**Target Class**: `<http://dbpedia.org/ontology/Politician>`

## Queries

### Query 1
**Description:**  
Get all the properties that can be applied to instances of the Politician class

**SPARQL Query:**
```sparql
PREFIX dbo: <http://dbpedia.org/ontology/>

SELECT DISTINCT ?property
WHERE {
    ?politician a dbo:Politician ;
                ?property ?value .
}
ORDER BY ?property
```

[**Results**](https://es.dbpedia.org/sparql?default-graph-uri=&query=PREFIX+dbo%3A+%3Chttp%3A%2F%2Fdbpedia.org%2Fontology%2F%3E%0D%0A%0D%0ASELECT+DISTINCT+%3Fproperty%0D%0AWHERE+%7B%0D%0A++++%3Fpolitician+a+dbo%3APolitician+%3B%0D%0A++++++++++++++++%3Fproperty+%3Fvalue+.%0D%0A%7D%0D%0AORDER+BY+%3Fproperty&should-sponge=&format=text%2Fhtml&timeout=0&debug=on&run=+Run+Query+)

---

### Query 2
**Description:**  
Get all the properties, except rdf:type, that can be applied to instances of the Politician class

**SPARQL Query:**
```sparql
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT DISTINCT ?property
WHERE {
    ?politician a dbo:Politician ;
                ?property ?value .
    FILTER (?property != rdf:type)
}
ORDER BY ?property
```

[**Results**](https://es.dbpedia.org/sparql?default-graph-uri=&query=PREFIX+dbo%3A+%3Chttp%3A%2F%2Fdbpedia.org%2Fontology%2F%3E%0D%0APREFIX+rdf%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%3E%0D%0A%0D%0ASELECT+DISTINCT+%3Fproperty%0D%0AWHERE+%7B%0D%0A++++%3Fpolitician+a+dbo%3APolitician+%3B%0D%0A++++++++++++++++%3Fproperty+%3Fvalue+.%0D%0A++++FILTER+%28%3Fproperty+%21%3D+rdf%3Atype%29%0D%0A%7D%0D%0AORDER+BY+%3Fproperty&should-sponge=&format=text%2Fhtml&timeout=0&debug=on&run=+Run+Query+)

---

### Query 3
**Description:**  
Which different values exist for the properties, except rdf:type, of the instances of the Politician class?

**SPARQL Query:**
```sparql
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT DISTINCT ?value
WHERE {
    ?politician a dbo:Politician ;
                ?property ?value .
    FILTER (?property != rdf:type)
}
ORDER BY ?value
```

[**Results**](https://es.dbpedia.org/sparql?default-graph-uri=&query=PREFIX+dbo%3A+%3Chttp%3A%2F%2Fdbpedia.org%2Fontology%2F%3E%0D%0APREFIX+rdf%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%3E%0D%0A%0D%0ASELECT+DISTINCT+%3Fvalue%0D%0AWHERE+%7B%0D%0A++++%3Fpolitician+a+dbo%3APolitician+%3B%0D%0A++++++++++++++++%3Fproperty+%3Fvalue+.%0D%0A++++FILTER+%28%3Fproperty+%21%3D+rdf%3Atype%29%0D%0A%7D%0D%0AORDER+BY+%3Fvalue&should-sponge=&format=text%2Fhtml&timeout=0&debug=on&run=+Run+Query+)

---

### Query 4
**Description:**  
For each of the properties, except rdf:type, that can be applied to instances of the Politician class, which different values do they take in those instances?

**SPARQL Query:**
```sparql
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT DISTINCT ?property ?value 
WHERE { 
    ?politician a dbo:Politician ;
                ?property ?value . 
    FILTER (?property != rdf:type) 
} 
ORDER BY ?property ?value
```

[**Results**](https://es.dbpedia.org/sparql?default-graph-uri=&query=PREFIX+dbo%3A+%3Chttp%3A%2F%2Fdbpedia.org%2Fontology%2F%3E%0D%0APREFIX+rdf%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%3E%0D%0A%0D%0ASELECT+DISTINCT+%3Fproperty+%3Fvalue+%0D%0AWHERE+%7B+%0D%0A++++%3Fpolitician+a+dbo%3APolitician+%3B%0D%0A++++++++++++++++%3Fproperty+%3Fvalue+.+%0D%0A++++FILTER+%28%3Fproperty+%21%3D+rdf%3Atype%29+%0D%0A%7D+%0D%0AORDER+BY+%3Fproperty+%3Fvalue&should-sponge=&format=text%2Fhtml&timeout=0&debug=on&run=+Run+Query+)

---

### Query 5
**Description:**  
For each of the properties, except rdf:type, that can be applied to instances of the Politician class, how many distinct values do they take in those instances?

**SPARQL Query:**
```sparql
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?property (COUNT(DISTINCT ?value) AS ?numDistinctValues)
WHERE {
    ?politician a dbo:Politician ;
                ?property ?value .
    FILTER (?property != rdf:type)
}
GROUP BY ?property
ORDER BY DESC(?numDistinctValues)
```
[**Results**](https://es.dbpedia.org/sparql?default-graph-uri=&query=PREFIX+dbo%3A+%3Chttp%3A%2F%2Fdbpedia.org%2Fontology%2F%3E%0D%0APREFIX+rdf%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%3E%0D%0A%0D%0ASELECT+%3Fproperty+%28COUNT%28DISTINCT+%3Fvalue%29+AS+%3FnumDistinctValues%29%0D%0AWHERE+%7B%0D%0A++++%3Fpolitician+a+dbo%3APolitician+%3B%0D%0A++++++++++++++++%3Fproperty+%3Fvalue+.%0D%0A++++FILTER+%28%3Fproperty+%21%3D+rdf%3Atype%29%0D%0A%7D%0D%0AGROUP+BY+%3Fproperty%0D%0AORDER+BY+DESC%28%3FnumDistinctValues%29&should-sponge=&format=text%2Fhtml&timeout=0&debug=on&run=+Run+Query+)