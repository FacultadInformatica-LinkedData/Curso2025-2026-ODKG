#############################################################
# Linked Universities Data Explorer — Backend API
# Local RDFlib SPARQL Engine (NO external SPARQL server)
#############################################################

import os
from flask import Flask, request, Response, send_file
from rdflib import Graph, URIRef, RDF
from flask_cors import CORS
import json


#############################################################
# 1) Create Flask app
#############################################################

app = Flask(__name__)
CORS(app)

#############################################################
# 2) Load the Knowledge Graph (local rdf.ttl)
#############################################################

DATA_FILE = "complete-with-links.ttl"   # your local RDF dataset

if not os.path.exists(DATA_FILE):
    raise FileNotFoundError("ERROR: rdf.ttl file not found!")

g = Graph()
g.parse(DATA_FILE, format="turtle")  # <-- local RDFlib load

#############################################################
# Helper functions
#############################################################

def execute_query(sparql):
    """
    Runs a SPARQL query on the RDFlib graph.
    Returns JSON-ready dict with results and count.
    """
    try:
        qres = g.query(sparql)
        results = []

        for row in qres:
            item = {}
            for i, var in enumerate(qres.vars):
                val = row[i]
                if val:
                    val = str(val)
                item[str(var)] = val
            results.append(item)

        return {"results": results, "count": len(results)}

    except Exception as e:
        return {"error": str(e)}

def json_response(data):
    """Return a JSON response with proper Unicode characters."""
    return Response(json.dumps(data, ensure_ascii=False, indent=2), mimetype="application/json")

#############################################################
# Base prefixes
#############################################################

PREFIXES = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
PREFIX lude: <http://spanishuniversities.data.es/lude/ontology#>
PREFIX id: <http://spanishuniversities.data.es/lude/resource/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
"""

#############################################################
# 3) ENDPOINTS
#############################################################

@app.route("/")
def home():
    return json_response({"message": "LUDE API running (local RDFlib mode)", "triples": len(g)})

@app.route("/docs")
def docs():
    routes = [
        {"path": "/", "method": "GET", "description": "Health check"},
        {"path": "/classes", "method": "GET", "description": "List all RDF classes"},
        {"path": "/instances?class=", "method": "GET", "description": "List all instances of a class"},
        {"path": "/academic-levels", "method": "GET", "description": "List academic levels"},
        {"path": "/search/degrees?q=", "method": "GET", "description": "Search degrees by text"},
        {"path": "/filter/degrees?ac=&university=&area=", "method": "GET", "description": "Filter degrees"},
        {"path": "/map/universities", "method": "GET", "description": "University locations"},
        {"path": "/degree/<degree_id>", "method": "GET", "description": "Degree details by ID"},
        {"path": "/universities", "method": "GET", "description": "List all universities"},
        {"path": "/search/universities?q=", "method": "GET", "description": "Search universities"},
        {"path": "/university/<uni_id>", "method": "GET", "description": "University details by ID"},
        {"path": "/export", "method": "GET", "description": "Export dataset as Turtle"},
        {"path": "/sparql", "method": "POST", "description": "Raw SPARQL query"}
    ]
    return json_response({"routes": routes})

#############################################################
# List RDF classes
# Example usage: /classes
#############################################################

@app.route("/classes")
def list_classes():
    q = PREFIXES + """
    SELECT DISTINCT ?class
    WHERE { ?s rdf:type ?class . }
    ORDER BY ?class
    """
    return json_response(execute_query(q))

#############################################################
# List all instances of a class and its information
# Example usage: /instances?class=University | Municipality | Province | Degree | AutonomousCommunity | AcademicLevel | KnowledgeArea
#############################################################

#############################################################
# List all instances of a class and its information
# Returns DISTINCT instances (one row per instance)
#############################################################

@app.route("/instances")
def list_instances():
    class_name = request.args.get("class", "").strip()
    if not class_name:
        return json_response({"error": "Missing query parameter: class"})

    # Define known optional properties for each class
    optional_props = {
        "University": ["lude:acronym", "lude:cif", "lude:url", "lude:type", "lude:modality",
                       "lude:publicationYear", "lude:telephone", "lude:email", "geo:lat", "geo:long",
                       "lude:hasAddress", "owl:sameAs"],
        "Municipality": ["lude:partOfProvince", "owl:sameAs"],
        "Province": ["lude:partOfAutonomousCommunity", "owl:sameAs"],
        "AutonomousCommunity": ["owl:sameAs"],
        "AcademicLevel": ["owl:sameAs"],
        "KnowledgeArea": ["owl:sameAs"],
        "Degree": ["lude:code", "lude:academicYear", "lude:hasAcademicLevel", 
                   "lude:hasKnowledgeArea", "owl:sameAs"]
    }

    # Build SELECT with SAMPLE() for all optional properties
    q = PREFIXES + f"SELECT ?instance (SAMPLE(?label) AS ?label)"

    for prop in optional_props.get(class_name, []):
        var_name = prop.split(":")[-1]
        q += f" (SAMPLE(?{var_name}) AS ?{var_name})"

    # Extra readable labels
    if class_name == "Degree":
        q += " (SAMPLE(?academicLevelLabel) AS ?academicLevelLabel) (SAMPLE(?knowledgeAreaLabel) AS ?knowledgeAreaLabel) (SAMPLE(?universityLabel) AS ?universityLabel)"
    if class_name == "University":
        q += " (SAMPLE(?autonomousCommunityLabel) AS ?autonomousCommunityLabel)"

    # Build WHERE clause
    q += f"""
    WHERE {{
        ?instance a lude:{class_name} ;
                  rdfs:label ?label .
    """

    # OPTIONAL clauses for raw properties
    for prop in optional_props.get(class_name, []):
        var_name = prop.split(":")[-1]
        q += f"    OPTIONAL {{ ?instance {prop} ?{var_name} . }}\n"

    # Degree extra labels
    if class_name == "Degree":
        q += """
            OPTIONAL { ?instance lude:hasAcademicLevel ?level . ?level rdfs:label ?academicLevelLabel . }
            OPTIONAL { ?instance lude:hasKnowledgeArea ?area . ?area rdfs:label ?knowledgeAreaLabel . }
            OPTIONAL { ?university lude:offers ?instance . ?university rdfs:label ?universityLabel . }
        """

    # University extra label
    if class_name == "University":
        q += """
            OPTIONAL {
                ?instance lude:hasAddress ?ad .
                ?ad lude:locatedInMunicipality ?mun .
                ?mun lude:partOfProvince ?prov .
                ?prov lude:partOfAutonomousCommunity ?ac .
                ?ac rdfs:label ?autonomousCommunityLabel .
            }
        """

    q += "\n} GROUP BY ?instance ORDER BY ?label"

    return json_response(execute_query(q))



#############################################################
# Search Universities
# Example usage: /search/universities?q=Zaragoza
#############################################################

@app.route("/search/universities")
def search_universities():
    text = request.args.get("q", "").lower()
    if not text:
        return json_response({"error": "Missing query parameter: q"})

    q = PREFIXES + f"""
    SELECT DISTINCT ?university ?label ?acronym ?url ?type ?modality ?publicationYear ?telephone ?email ?lat ?long
    WHERE {{
        ?university a lude:University ;
                    rdfs:label ?label .

        OPTIONAL {{ ?university lude:acronym ?acronym . }}
        OPTIONAL {{ ?university lude:url ?url . }}
        OPTIONAL {{ ?university lude:type ?type . }}
        OPTIONAL {{ ?university lude:modality ?modality . }}
        OPTIONAL {{ ?university lude:publicationYear ?publicationYear . }}
        OPTIONAL {{ ?university lude:telephone ?telephone . }}
        OPTIONAL {{ ?university lude:email ?email . }}
        OPTIONAL {{ ?university geo:lat ?lat . }}
        OPTIONAL {{ ?university geo:long ?long . }}

        FILTER(CONTAINS(LCASE(?label), "{text}"))
    }}
    GROUP BY ?university ORDER BY ?label
    """
    return json_response(execute_query(q))

#############################################################
# Search Degrees
# Example usage: /search/degrees?q=Matemáticas
#############################################################
@app.route("/search/degrees")
def search_degrees():
    text = request.args.get("q", "").lower()
    if not text:
        return json_response({"error": "Missing query parameter: q"})

    q = PREFIXES + f"""
    SELECT DISTINCT ?degree ?label ?academicYear ?code ?academicLevelLabel ?knowledgeAreaLabel 
           ?uniName ?facultyName ?campus ?teachingModality ?ects
    WHERE {{
        ?degree a lude:Degree ;
                rdfs:label ?label .

        FILTER(CONTAINS(LCASE(?label), "{text}"))

        OPTIONAL {{ ?degree lude:academicYear ?academicYear . }}
        OPTIONAL {{ ?degree lude:code ?code . }}
        OPTIONAL {{ ?degree lude:hasAcademicLevel ?al .
                   ?al rdfs:label ?academicLevelLabel . }}
        OPTIONAL {{ ?degree lude:hasKnowledgeArea ?ka .
                   ?ka rdfs:label ?knowledgeAreaLabel . }}
        OPTIONAL {{
            ?uni lude:offers ?degree ;
                 rdfs:label ?uniName .
        }}
        OPTIONAL {{
            ?degree lude:deliveredAt ?fac .
            ?fac rdfs:label ?facultyName .
        }}
        OPTIONAL {{ ?degree lude:campus ?campus . }}
        OPTIONAL {{ ?degree lude:teachingModality ?teachingModality . }}
        OPTIONAL {{ ?degree lude:ectsCredits ?ects . }}
    }}
    GROUP BY ?degree ORDER BY ?label
    """
    return json_response(execute_query(q))

#############################################################
# Filter Degrees
# Example usage: /filter/degrees?ac=Aragon | /filter/degrees?university=UNED&area=Engineering | f/ilter/degrees?ac=Aragón&university=UNED&area=Engineering
#############################################################

@app.route("/filter/degrees")
def filter_degrees():
    # Get query parameters
    ac = request.args.get("ac", "").lower()
    uni = request.args.get("university", "").lower()
    area = request.args.get("area", "").lower()
    prov = request.args.get("province", "").lower()
    mun = request.args.get("municipality", "").lower()
    level = request.args.get("level", "").lower()

    # Build SPARQL query
    q = PREFIXES + f"""
    SELECT ?degree
           (SAMPLE(?degreeName) AS ?degreeName)
           (SAMPLE(?uniLabel) AS ?uniLabel)
           (SAMPLE(?uniName) AS ?uniName)
           (SAMPLE(?munLabel) AS ?munLabel)
           (SAMPLE(?provLabel) AS ?provLabel)
           (SAMPLE(?acLabel) AS ?acLabel)
           (SAMPLE(?areaLabel) AS ?areaLabel)
           (SAMPLE(?levelLabel) AS ?levelLabel)
           (SAMPLE(?facultyName) AS ?facultyName)
           (SAMPLE(?ects) AS ?ects)
           (SAMPLE(?campus) AS ?campus)
           (SAMPLE(?code) AS ?code)
           (SAMPLE(?academicYear) AS ?academicYear)
           (SAMPLE(?teachingModality) AS ?teachingModality)
    WHERE {{
        ?degree a lude:Degree ;
                rdfs:label ?degreeName .

        OPTIONAL {{ ?degree lude:academicYear ?academicYear . }}
        OPTIONAL {{ ?degree lude:code ?code . }}
        OPTIONAL {{
            ?uni lude:offers ?degree ;
                 rdfs:label ?uniLabel .
            OPTIONAL {{
                ?uni lude:hasAddress ?addr .
                ?addr lude:locatedInMunicipality ?mun .
                ?mun rdfs:label ?munLabel ;
                     lude:partOfProvince ?prov .
                ?prov rdfs:label ?provLabel ;
                      lude:partOfAutonomousCommunity ?ac .
                ?ac rdfs:label ?acLabel .
            }}
        }}
        OPTIONAL {{
            ?degree lude:hasKnowledgeArea ?area .
            ?area rdfs:label ?areaLabel .
        }}
        OPTIONAL {{
            ?degree lude:hasAcademicLevel ?level .
            ?level rdfs:label ?levelLabel .
        }}
        OPTIONAL {{
            ?degree lude:deliveredAt ?fac .
            ?fac rdfs:label ?facultyName .
        }}
        OPTIONAL {{ ?degree lude:campus ?campus . }}
        OPTIONAL {{ ?degree lude:teachingModality ?teachingModality . }}
        OPTIONAL {{ ?degree lude:ectsCredits ?ects . }}

        # Filters
        {"FILTER(CONTAINS(LCASE(?acLabel), \"" + ac + "\"))" if ac else ""}
        {"FILTER(CONTAINS(LCASE(?uniLabel), \"" + uni + "\"))" if uni else ""}
        {"FILTER(CONTAINS(LCASE(?areaLabel), \"" + area + "\"))" if area else ""}
        {"FILTER(CONTAINS(LCASE(?provLabel), \"" + prov + "\"))" if prov else ""}
        {"FILTER(CONTAINS(LCASE(?munLabel), \"" + mun + "\"))" if mun else ""}
        {"FILTER(CONTAINS(LCASE(?levelLabel), \"" + level + "\"))" if level else ""}
    }}
    GROUP BY ?degree
    ORDER BY ?degreeName
    """
    return json_response(execute_query(q))


#############################################################
# Map Universities
# Example usage: /map/universities
#############################################################

@app.route("/map/universities")
def map_universities():
    q = PREFIXES + """
    SELECT ?university ?name ?lat ?long ?autonomousCommunityLabel
    WHERE {
        ?university a lude:University ;
                    rdfs:label ?name ;
                    geo:lat ?lat ;
                    geo:long ?long .
        
        OPTIONAL {
            ?university lude:hasAddress ?ad .
            ?ad lude:locatedInMunicipality ?mun .
            ?mun lude:partOfProvince ?prov .
            ?prov lude:partOfAutonomousCommunity ?ac .
            ?ac rdfs:label ?autonomousCommunityLabel .
        }
    }
    """
    return json_response(execute_query(q))

#############################################################
# Export Graph as Turtle
#############################################################

@app.route("/export2")
def export_graph2():
    export_dir = "exported"
    os.makedirs(export_dir, exist_ok=True)
    out_file = os.path.join(export_dir, "export.ttl")
    g.serialize(out_file, format="turtle")
    return send_file(
        out_file, 
        as_attachment=True, 
        download_name="lude_dataset.ttl",  # Flask >= 2.0
        mimetype="text/turtle"
    )   

@app.route("/export")
def export_graph():
    export_dir = "exported"
    os.makedirs(export_dir, exist_ok=True)
    out_file = os.path.join(export_dir, "export.ttl")
    g.serialize(out_file, format="turtle")
    
    return send_file(
        out_file,
        as_attachment=False,           # Important: do NOT force download
        mimetype="text/turtle"         # Browser will display TTL as text
    )



#############################################################
# Raw SPARQL endpoint
#############################################################

@app.route("/sparql", methods=["POST"])
def sparql_endpoint():
    body = request.json
    if not body or "query" not in body:
        return json_response({"error": "Send JSON with 'query'"})
    return json_response(execute_query(body["query"]))

#############################################################
# Run server
#############################################################

if __name__ == "__main__":
    app.run(debug=True)
