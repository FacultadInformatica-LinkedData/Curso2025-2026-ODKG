# spqrQL Assignment

## Descripion
Create the SPARQL query and the result for the following queries expressed in natural language. The endpoint that you can use for this exercise is: http://es.dbpedia.org/sparql

The queries in natural language:
1. Get all the properties that can be applied to instances of the Politician class (<http://dbpedia.org/ontology/Politician>)
2. Get all the properties, except rdf:type, that can be applied to instances of the Politician class
3. Which different values exist for the properties, except for rdf:type, applicable to the instances of Politician?
4. For each of these applicable properties, except for rdf:type, which different values do they take globally for all those instances?
5. For each of these applicable properties, except for rdf:type, how many distinct values do they take globally for all those instances?
 
## Solution

### Query 1

**Description**:<br>
Get all the properties that can be applied to instances of the Politician class (<http://dbpedia.org/ontology/Politician>)

**Query**:
<!-- sql tag added only for syntax highlight -->
```sql 
select distinct ?property
where {
  ?person a <http://dbpedia.org/ontology/Politician> ;
            ?property ?value
}
```

[**Output Link**](https://es.dbpedia.org/sparql?default-graph-uri=&query=select+distinct+%3Fproperty%0D%0Awhere+%7B%0D%0A++%3Fperson+a+%3Chttp%3A%2F%2Fdbpedia.org%2Fontology%2FPolitician%3E+%3B%0D%0A++++++++++++%3Fproperty+%3Fvalue%0D%0A%7D&should-sponge=&format=text%2Fhtml&timeout=0&debug=on&run=+Run+Query+)



### Query 2

**Description**:<br>
Get all the properties, except rdf:type, that can be applied to instances of the Politician class

**Query**:
<!-- sql tag added only for syntax highlight -->
```sql 
select distinct ?property
where {
  ?person a <http://dbpedia.org/ontology/Politician> ;
            ?property ?value .
 filter ( ?property != rdf:type )
}
```

[**Output Link**](https://es.dbpedia.org/sparql?default-graph-uri=&query=select+distinct+%3Fproperty%0D%0Awhere+%7B%0D%0A++%3Fperson+a+%3Chttp%3A%2F%2Fdbpedia.org%2Fontology%2FPolitician%3E+%3B%0D%0A++++++++++++%3Fproperty+%3Fvalue+.%0D%0A+filter+%28+%3Fproperty+%21%3D+rdf%3Atype+%29%0D%0A%7D&should-sponge=&format=text%2Fhtml&timeout=0&debug=on&run=+Run+Query+)

### Query 3

**Description**:<br>
Which different values exist for the properties, except for rdf:type, applicable to the instances of Politician?

**Query**:
<!-- sql tag added only for syntax highlight -->
```sql 
select distinct ?value
where {
  ?person a <http://dbpedia.org/ontology/Politician> ;
            ?property ?value .
 filter (?property != rdf:type) .
}
```

[**Output Link**](https://es.dbpedia.org/sparql?default-graph-uri=&query=select+distinct+%3Fvalue%0D%0Awhere+%7B%0D%0A++%3Fperson+a+%3Chttp%3A%2F%2Fdbpedia.org%2Fontology%2FPolitician%3E+%3B%0D%0A++++++++++++%3Fproperty+%3Fvalue+.%0D%0A+filter+%28%3Fproperty+%21%3D+rdf%3Atype%29+.%0D%0A%7D&should-sponge=&format=text%2Fhtml&timeout=0&debug=on&run=+Run+Query+)

### Query 4

**Description**:<br>
For each of these applicable properties, except for rdf:type, which different values do they take globally for all those instances?

**Query**:
<!-- sql tag added only for syntax highlight -->
```sql 
select ?property group_concat(distinct ?value; separator="; ")
where {
  ?person a <http://dbpedia.org/ontology/Politician> ;
            ?property ?value .
 filter (?property != rdf:type) .
}
group by ?property
```

[**Output Link**](https://es.dbpedia.org/sparql?default-graph-uri=&query=select+%3Fproperty+group_concat%28distinct+%3Fvalue%3B+separator%3D%22%3B+%22%29%0D%0Awhere+%7B%0D%0A++%3Fperson+a+%3Chttp%3A%2F%2Fdbpedia.org%2Fontology%2FPolitician%3E+%3B%0D%0A++++++++++++%3Fproperty+%3Fvalue+.%0D%0A+filter+%28%3Fproperty+%21%3D+rdf%3Atype%29+.%0D%0A%7D%0D%0Agroup+by+%3Fproperty%0D%0Alimit+10&should-sponge=&format=text%2Fhtml&timeout=0&debug=on&run=+Run+Query+)
(Most probably will time out due to concatenating huge amounts of values)

### Query 5

**Description**:<br>
For each of these applicable properties, except for rdf:type, how many distinct values do they take globally for all those instances?

**Query**:
<!-- sql tag added only for syntax highlight -->
```sql 
select ?property count(distinct ?value)
where {
  ?person a <http://dbpedia.org/ontology/Politician> ;
            ?property ?value .
 filter (?property != rdf:type) .
}
group by ?property
```

[**Output Link**](https://es.dbpedia.org/sparql?default-graph-uri=&query=select+%3Fproperty+count%28distinct+%3Fvalue%29%0D%0Awhere+%7B%0D%0A++%3Fperson+a+%3Chttp%3A%2F%2Fdbpedia.org%2Fontology%2FPolitician%3E+%3B%0D%0A++++++++++++%3Fproperty+%3Fvalue+.%0D%0A+filter+%28%3Fproperty+%21%3D+rdf%3Atype%29+.%0D%0A%7D%0D%0Agroup+by+%3Fproperty&should-sponge=&format=text%2Fhtml&timeout=0&debug=on&run=+Run+Query+)



