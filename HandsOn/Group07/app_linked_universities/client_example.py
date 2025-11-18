"""
client_example.py
Example client for interacting with the Linked Universities Data Explorer backend.

Run:
    python client_example.py
"""
import os
import json
import requests

BASE = "http://localhost:5000"   # Your backend Flask server


def pretty(x):
    print(json.dumps(x, indent=2, ensure_ascii=False))

# Ensure exported directory exists
export_dir = "exported"
os.makedirs(export_dir, exist_ok=True)

# -----------------------------------------------------------
# 1) Test SEARCH endpoint
# -----------------------------------------------------------
print("\n=== SEARCH: 'Zaragoza' ===")
resp = requests.get(f"{BASE}/search/degrees?q=Zaragoza").json()
pretty(resp)

# -----------------------------------------------------------
# 2) Test FILTERING endpoint
# -----------------------------------------------------------
print("\n=== FILTER: Comunidad Autónoma = 'Aragón', Branch = 'Ingeniería y Arquitectura' ===")
params = {
    "ac": "Aragón",
    "area": "Ingeniería y Arquitectura"
}
resp = requests.get(f"{BASE}/filter/degrees", params=params).json()
pretty(resp)

# -----------------------------------------------------------
# 3) Retrieve degree details
# -----------------------------------------------------------
print("\n=== DEGREE DETAIL: degree id 'UZ-INF' ===")
resp = requests.get(f"{BASE}/degree/UZ-INF").json()
pretty(resp)

# -----------------------------------------------------------
# 4) Export current graph to RDF Turtle
# -----------------------------------------------------------
print("\n=== EXPORT RDF: full dataset ===")
resp = requests.get(f"{BASE}/export")
# Save the file inside the exported directory
export_path = os.path.join(export_dir, "exported.ttl")
with open(export_path, "wb") as f:
    f.write(resp.content)
print("Saved 'exported.ttl', size:", len(resp.content), "bytes")

# -----------------------------------------------------------
# 5) Execute custom SPARQL
# -----------------------------------------------------------
print("\n=== SPARQL: list universities ===")
query = """
PREFIX lude: <https://spainuniversities.data/ontology/lude#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?uni ?label
WHERE {
    ?uni a lude:University ;
         rdfs:label ?label .
}
ORDER BY ?label
"""

resp = requests.post(f"{BASE}/sparql", json={"query": query}).json()
pretty(resp)

print("\n=== EVERYTHING WORKED CORRECTLY ===")
