Queries:

1. Get all the properties that can be applied to instances of the Politician class (<http://dbpedia.org/ontology/Politician>)

```
select distinct ?p
where {
  ?s rdf:type dbo:Politician .
  ?s ?p ?o .
}
```

2. Get all the properties, except rdf:type, that can be applied to instances of the Politician class
```
select distinct ?p
where {
  ?s rdf:type dbo:Politician .
  ?s ?p ?o .
  filter ( ?p != rdf:type )
}
```

3. Which different values exist for the properties, except for rdf:type, applicable to the instances of Politician?
```
select distinct ?p ?o
where {
  ?s rdf:type dbo:Politician .
  ?s ?p ?o .
  filter ( ?p != rdf:type )
}
```

4. For each of these applicable properties, except for rdf:type, which different values do they take globally for all those instances?
```
select ?p (GROUP_CONCAT(DISTINCT STR(?o); separator=" | ") AS ?distinct_values)
where {
  ?s rdf:type dbo:Politician .
  ?s ?p ?o .
  filter ( ?p != rdf:type )
}
group by ?p
```

5. For each of these applicable properties, except for rdf:type, how many distinct values do they take globally for all those instances?
```
select ?p (COUNT(DISTINCT ?o) AS ?distinct_values)
where {
  ?s rdf:type dbo:Politician .
  ?s ?p ?o .
  filter ( ?p != rdf:type )
}
group by ?p
```

    
    
    
    
