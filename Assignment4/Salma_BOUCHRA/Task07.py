{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {
    "id": "nOOPLCHF7hLB"
   },
   "source": [
    "**Task 07: Querying RDF(s)**"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {
    "id": "Yl9npCt8n6m-"
   },
   "outputs": [],
   "source": [
    "import urllib.request\n",
    "url = 'https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/refs/heads/master/Assignment4/course_materials/python/validation.py'\n",
    "urllib.request.urlretrieve(url, 'validation.py')\n",
    "github_storage = \"https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/master/Assignment4/course_materials\""
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {
    "id": "FmnGjffDT92V"
   },
   "outputs": [],
   "source": [
    "from validation import Report"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "id": "XY7aPc86Bqoo"
   },
   "source": [
    "First let's read the RDF file"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {
    "id": "9ERh415on7kF"
   },
   "outputs": [],
   "source": [
    "from rdflib import Graph, Namespace, Literal\n",
    "from rdflib.namespace import RDF, RDFS\n",
    "# Do not change the name of the variables\n",
    "g = Graph()\n",
    "g.namespace_manager.bind('ns', Namespace(\"http://somewhere#\"), override=False)\n",
    "g.parse(github_storage+\"/rdf/data06.ttl\", format=\"TTL\")\n",
    "report = Report()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "id": "qp1oe2Eddsvo"
   },
   "source": [
    "**TASK 7.1a: For all classes, list each classURI. If the class belogs to another class, then list its superclass.**\n",
    "**Do the exercise in RDFLib returning a list of Tuples: (class, superclass) called \"result\". If a class does not have a super class, then return None as the superclass**"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "metadata": {
    "id": "tRcSWuMHOXBl"
   },
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "(rdflib.term.URIRef('http://oeg.fi.upm.es/def/people#Person'), None)\n",
      "(rdflib.term.URIRef('http://oeg.fi.upm.es/def/people#Animal'), None)\n",
      "(rdflib.term.URIRef('http://oeg.fi.upm.es/def/people#Professor'), rdflib.term.URIRef('http://oeg.fi.upm.es/def/people#Person'))\n",
      "(rdflib.term.URIRef('http://oeg.fi.upm.es/def/people#Student'), rdflib.term.URIRef('http://oeg.fi.upm.es/def/people#Person'))\n",
      "(rdflib.term.URIRef('http://oeg.fi.upm.es/def/people#FullProfessor'), rdflib.term.URIRef('http://oeg.fi.upm.es/def/people#Professor'))\n",
      "(rdflib.term.URIRef('http://oeg.fi.upm.es/def/people#AssociateProfessor'), rdflib.term.URIRef('http://oeg.fi.upm.es/def/people#Professor'))\n",
      "(rdflib.term.URIRef('http://oeg.fi.upm.es/def/people#InterimAssociateProfessor'), rdflib.term.URIRef('http://oeg.fi.upm.es/def/people#AssociateProfessor'))\n"
     ]
    }
   ],
   "source": [
    "# Visualize the results\n",
    "\n",
    "\n",
    "result = [] #list of tuples\n",
    "for s,p,o in g.triples((None, RDF.type, RDFS.Class)):\n",
    "    \n",
    "  superclass = g.value(subject=s, predicate=RDFS.subClassOf, object=None)\n",
    "  result.append((s, superclass))\n",
    "\n",
    "\n",
    "\n",
    "for r in result:\n",
    "  print(r)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "metadata": {
    "id": "uvEpQQrTlMPH"
   },
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "TASK 7.1a OK\n"
     ]
    }
   ],
   "source": [
    "## Validation: Do not remove\n",
    "report.validate_07_1a(result)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "id": "kbY-jqw6klr9"
   },
   "source": [
    "**TASK 7.1b: Repeat the same exercise in SPARQL, returning the variables ?c (class) and ?sc (superclass)**"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "metadata": {
    "id": "NGAG7l9UklMC"
   },
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "http://oeg.fi.upm.es/def/people#Person None\n",
      "http://oeg.fi.upm.es/def/people#Animal None\n",
      "http://oeg.fi.upm.es/def/people#Professor http://oeg.fi.upm.es/def/people#Person\n",
      "http://oeg.fi.upm.es/def/people#Student http://oeg.fi.upm.es/def/people#Person\n",
      "http://oeg.fi.upm.es/def/people#FullProfessor http://oeg.fi.upm.es/def/people#Professor\n",
      "http://oeg.fi.upm.es/def/people#AssociateProfessor http://oeg.fi.upm.es/def/people#Professor\n",
      "http://oeg.fi.upm.es/def/people#InterimAssociateProfessor http://oeg.fi.upm.es/def/people#AssociateProfessor\n"
     ]
    }
   ],
   "source": [
    "query =  \"\"\"\n",
    "select ?c ?sc\n",
    "WHERE {\n",
    "    ?c rdf:type rdfs:Class .\n",
    "    OPTIONAL { ?c rdfs:subClassOf ?sc } #To get the subClass \n",
    "}\n",
    "\"\"\"\n",
    "\n",
    "for r in g.query(query):\n",
    "  print(r.c, r.sc)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "metadata": {
    "id": "9zf4vgVHlKR3"
   },
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "TASK 7.1b OK\n"
     ]
    }
   ],
   "source": [
    "## Validation: Do not remove\n",
    "report.validate_07_1b(query,g)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "id": "gM3DASkTQQ5Y"
   },
   "source": [
    "**TASK 7.2a: List all individuals of \"Person\" with RDFLib (remember the subClasses). Return the individual URIs in a list called \"individuals\"**\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 14,
   "metadata": {
    "id": "LiKSPHRzS-XJ"
   },
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "http://oeg.fi.upm.es/def/people#Raul\n",
      "http://oeg.fi.upm.es/def/people#Asun\n",
      "http://oeg.fi.upm.es/def/people#Oscar\n"
     ]
    }
   ],
   "source": [
    "ns = Namespace(\"http://oeg.fi.upm.es/def/people#\")\n",
    "\n",
    "# variable to return\n",
    "individuals = []\n",
    "\n",
    "classe = set([ns.Person])\n",
    "\n",
    "def add_subclasse(cls):\n",
    "    for subclass in g.subjects(RDFS.subClassOf, cls):\n",
    "        if subclass not in classe:\n",
    "            classe.add(subclass)\n",
    "            add_subclasse(subclass)\n",
    "\n",
    "add_subclasse(ns.Person)\n",
    "\n",
    "for cls in classe:\n",
    "    for indiv in g.subjects(RDF.type, cls):\n",
    "        individuals.append(indiv)\n",
    "\n",
    "# visualize results\n",
    "for i in individuals:\n",
    "  print(i)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 15,
   "metadata": {
    "id": "ONrAls5uiX1G"
   },
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "TASK 7.2a OK\n"
     ]
    }
   ],
   "source": [
    "# validation. Do not remove\n",
    "report.validate_07_02a(individuals)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "id": "up-952A-za7A"
   },
   "source": [
    "**TASK 7.2b: Repeat the same exercise in SPARQL, returning the individual URIs in a variable ?ind**"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 16,
   "metadata": {
    "id": "ipYiEVbTzbR0"
   },
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "http://oeg.fi.upm.es/def/people#Asun\n",
      "http://oeg.fi.upm.es/def/people#Oscar\n",
      "http://oeg.fi.upm.es/def/people#Raul\n"
     ]
    }
   ],
   "source": [
    "query =  \"\"\" Select ?ind\n",
    "Where {\n",
    "  ?ind a ?c .\n",
    "  ?c rdfs:subClassOf* ontology:Person .\n",
    "} \n",
    "\"\"\"\n",
    "for r in g.query(query):\n",
    "  print(r.ind)\n",
    "# Visualize the results"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 17,
   "metadata": {
    "id": "s-Hu2LxRjUQt"
   },
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "TASK 7.2b OK\n"
     ]
    }
   ],
   "source": [
    "## Validation: Do not remove\n",
    "report.validate_07_02b(g, query)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "id": "3NyI7M2VNr9R"
   },
   "source": [
    "**TASK 7.3:  List the name and type of those who know Rocky (in SPARQL only). Use name and type as variables in the query**"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 22,
   "metadata": {
    "id": "I_CNoIKdNpbx"
   },
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Asun http://oeg.fi.upm.es/def/people#FullProfessor\n",
      "Raul http://oeg.fi.upm.es/def/people#InterimAssociateProfessor\n",
      "Fantasma http://oeg.fi.upm.es/def/people#Animal\n"
     ]
    }
   ],
   "source": [
    "query =  \"\"\"\n",
    "prefix people: <http://oeg.fi.upm.es/def/people#>\n",
    "\n",
    "Select ?name ?type\n",
    "Where {\n",
    "  ?person people:knows people:Rocky . \n",
    "  ?person rdfs:label ?name.\n",
    "  ?person rdf:type ?type\n",
    "}\n",
    "\n",
    "\"\"\"\n",
    "\n",
    "\n",
    "\n",
    "# TO DO\n",
    "# Visualize the results\n",
    "for r in g.query(query):\n",
    "  print(r.name, r.type)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 23,
   "metadata": {
    "id": "Zf3JS7tEhS2t"
   },
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "TASK 7.3 OK\n"
     ]
    }
   ],
   "source": [
    "## Validation: Do not remove\n",
    "report.validate_07_03(g, query)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "id": "kyjGsyxDPa2C"
   },
   "source": [
    "**Task 7.4: List the name of those entities who have a colleague with a dog, or that have a collegue who has a colleague who has a dog (in SPARQL). Return the results in a variable called name**"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 33,
   "metadata": {
    "id": "yoVwVZUAPaLm"
   },
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Asun\n",
      "Oscar\n",
      "Raul\n"
     ]
    }
   ],
   "source": [
    "query =  \"\"\"\n",
    "\n",
    "PREFIX people: <http://oeg.fi.upm.es/def/people#>\n",
    "\n",
    "select ?name\n",
    "Where{\n",
    "{\n",
    "      ?person people:hasColleague ?colleague1 .\n",
    "      ?colleague1 people:ownsPet ?pet.\n",
    "      ?pet rdf:type people:Animal .  # >:(\n",
    "    }\n",
    "    UNION\n",
    "    {\n",
    "      ?person people:hasColleague ?colleague1 .\n",
    "      ?colleague1 people:hasColleague ?colleague2 .\n",
    "      ?colleague2 people:ownsPet ?pet.\n",
    "      ?pet rdf:type people:Animal .\n",
    "    }\n",
    "\n",
    "    ?person rdfs:label ?name\n",
    "  } \n",
    "\n",
    "\n",
    "\n",
    "\"\"\"\n",
    "\n",
    "for r in g.query(query):\n",
    "  print(r.name)\n",
    "\n",
    "# TO DO\n",
    "# Visualize the results"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 34,
   "metadata": {
    "id": "zcTZE7ngj2fc"
   },
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "TASK 7.4 OK\n"
     ]
    }
   ],
   "source": [
    "## Validation: Do not remove\n",
    "report.validate_07_04(g,query)\n",
    "report.save_report(\"_Task_07\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "colab": {
   "provenance": []
  },
  "kernelspec": {
   "display_name": "Python [conda env:base] *",
   "language": "python",
   "name": "conda-base-py"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.13.5"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
