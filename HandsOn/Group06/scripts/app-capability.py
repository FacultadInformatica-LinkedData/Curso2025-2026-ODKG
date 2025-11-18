#!/usr/bin/env python3
"""
Application Capability Demo - Madrid Bus Network Quiz App
Group 06 - GTFS Madrid

Demonstrates RDF/Linked Data approach:
1. Query local RDF graph (rdflib + SPARQL) to get area for a bus stop
2. Extract Wikidata Q-identifier from owl:sameAs link
3. Query Wikidata RDF graph (SPARQL) to get structured data
4. Extract Wikipedia links from Wikidata SPARQL results
5. Fetch Wikipedia article text using REST API

Example: User at bus stop par_8_09765 (Carabaña)
"""

import json
import ssl
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from rdflib import Graph, Namespace

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

EX = Namespace("http://group06.linkeddata.es/ontology/madridbus/")
RES = Namespace("http://group06.linkeddata.es/resource/")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
OWL = Namespace("http://www.w3.org/2002/07/owl#")


def load_rdf_graph(rdf_file):
    """Load RDF graph from file"""
    print(f"Loading RDF graph from {rdf_file.name}...")
    graph = Graph()
    suffix = rdf_file.suffix.lower()
    rdf_format = "turtle" if suffix in {".ttl", ".turtle"} else "nt"
    graph.parse(rdf_file, format=rdf_format)
    print(f"✓ Loaded {len(graph):,} triples\n")
    return graph


def get_stop_context(graph, stop_id):
    """Query local RDF graph for bus stop and area information"""
    print(f"📍 Querying local RDF for stop: {stop_id}")
    print("-" * 70)

    stop_uri = RES[f"stop/{stop_id}"]
    stop_name = graph.value(stop_uri, RDFS.label)
    area_uri = graph.value(stop_uri, EX.locatedInArea)

    if not area_uri:
        print("✗ No area found for this stop")
        return None

    area_name = graph.value(area_uri, RDFS.label)
    area_code = graph.value(area_uri, EX.areaCode)
    wikidata_uri = graph.value(area_uri, OWL.sameAs)

    context = {
        "stop_id": stop_id,
        "stop_name": str(stop_name) if stop_name else "Unknown",
        "area_name": str(area_name) if area_name else "Unknown",
        "area_code": str(area_code) if area_code else None,
        "wikidata_uri": str(wikidata_uri) if wikidata_uri else None,
        "wikidata_id": str(area_code) if area_code else None,
    }

    print(f"✓ Stop: {context['stop_name']}")
    print(f"✓ Area: {context['area_name']}")
    print(f"✓ Wikidata: {context['wikidata_id']}\n")
    return context


def fetch_wikidata_entity_via_sparql(qid):
    """Fetch structured data from Wikidata using SPARQL"""
    print(f"🌐 Querying Wikidata SPARQL for: {qid}")
    print("-" * 70)

    sparql_query = f"""
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX schema: <http://schema.org/>
    
    SELECT ?label ?description ?instanceOfLabel ?countryLabel ?locatedInLabel 
           ?population ?coordinates ?esWikiTitle ?esWikiUrl ?enWikiTitle ?enWikiUrl
    WHERE {{
      wd:{qid} rdfs:label ?label .
      FILTER(LANG(?label) = "es" || LANG(?label) = "en")
      
      OPTIONAL {{ wd:{qid} schema:description ?description .
                 FILTER(LANG(?description) = "es" || LANG(?description) = "en") }}
      OPTIONAL {{ wd:{qid} wdt:P31 ?instanceOf .
                 ?instanceOf rdfs:label ?instanceOfLabel .
                 FILTER(LANG(?instanceOfLabel) = "es" || LANG(?instanceOfLabel) = "en") }}
      OPTIONAL {{ wd:{qid} wdt:P17 ?country .
                 ?country rdfs:label ?countryLabel .
                 FILTER(LANG(?countryLabel) = "es" || LANG(?countryLabel) = "en") }}
      OPTIONAL {{ wd:{qid} wdt:P131 ?locatedIn .
                 ?locatedIn rdfs:label ?locatedInLabel .
                 FILTER(LANG(?locatedInLabel) = "es" || LANG(?locatedInLabel) = "en") }}
      OPTIONAL {{ wd:{qid} wdt:P1082 ?population }}
      OPTIONAL {{ wd:{qid} wdt:P625 ?coordinates }}
      OPTIONAL {{ ?esWikiUrl schema:about wd:{qid} ;
                             schema:isPartOf <https://es.wikipedia.org/> ;
                             schema:name ?esWikiTitle }}
      OPTIONAL {{ ?enWikiUrl schema:about wd:{qid} ;
                             schema:isPartOf <https://en.wikipedia.org/> ;
                             schema:name ?enWikiTitle }}
    }}
    LIMIT 10
    """

    endpoint = "https://query.wikidata.org/sparql"
    params = {"query": sparql_query, "format": "json"}
    url = f"{endpoint}?" + "&".join(f"{k}={quote(v)}" for k, v in params.items())

    try:
        req = Request(url, headers={"User-Agent": "MadridBusQuizApp/1.0"})
        with urlopen(req, timeout=30, context=ssl_context) as response:
            data = json.loads(response.read().decode())

        bindings = data.get("results", {}).get("bindings", [])
        if not bindings:
            print(f"✗ No data found for {qid}\n")
            return None

        result = {
            "qid": qid,
            "label": None,
            "description": None,
            "properties": {},
            "wikipedia_sites": {},
        }

        for binding in bindings:
            if "label" in binding:
                label_value = binding["label"]["value"]
                label_lang = binding["label"].get("xml:lang", "")
                if not result["label"] or label_lang == "es":
                    result["label"] = label_value

            if "description" in binding and not result["description"]:
                result["description"] = binding["description"]["value"]

            if "instanceOfLabel" in binding:
                if "instance_of" not in result["properties"]:
                    result["properties"]["instance_of"] = []
                result["properties"]["instance_of"].append(
                    binding["instanceOfLabel"]["value"]
                )

            if "countryLabel" in binding and "country" not in result["properties"]:
                result["properties"]["country"] = binding["countryLabel"]["value"]

            if "locatedInLabel" in binding and "located_in" not in result["properties"]:
                result["properties"]["located_in"] = binding["locatedInLabel"]["value"]

            if "population" in binding and "population" not in result["properties"]:
                result["properties"]["population"] = binding["population"]["value"]

            if "coordinates" in binding and "coordinates" not in result["properties"]:
                result["properties"]["coordinates"] = binding["coordinates"]["value"]

            if "esWikiTitle" in binding and "eswiki" not in result["wikipedia_sites"]:
                result["wikipedia_sites"]["eswiki"] = {
                    "title": binding["esWikiTitle"]["value"],
                    "url": binding["esWikiUrl"]["value"],
                }

            if "enWikiTitle" in binding and "enwiki" not in result["wikipedia_sites"]:
                result["wikipedia_sites"]["enwiki"] = {
                    "title": binding["enWikiTitle"]["value"],
                    "url": binding["enWikiUrl"]["value"],
                }

        print(f"✓ Label: {result['label']}")
        print(f"✓ Description: {result['description']}")
        print(f"✓ Properties: {len(result['properties'])}")
        for prop, value in result["properties"].items():
            val_str = ", ".join(value[:3]) if isinstance(value, list) else str(value)
            print(f"  - {prop}: {val_str}")
        print(f"✓ Wikipedia links: {len(result['wikipedia_sites'])}\n")
        return result

    except (HTTPError, URLError) as e:
        print(f"✗ Error querying Wikidata SPARQL: {e}\n")
        return None
    except Exception as e:
        print(f"✗ Unexpected error: {e}\n")
        return None


def fetch_wikipedia_extract(wikipedia_title, lang="es"):
    """Fetch Wikipedia article extract"""
    print(f"📖 Fetching Wikipedia: {wikipedia_title} ({lang})")
    print("-" * 70)

    encoded_title = quote(wikipedia_title, safe="")
    url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{encoded_title}"

    try:
        req = Request(url, headers={"User-Agent": "MadridBusQuizApp/1.0"})
        with urlopen(req, timeout=10, context=ssl_context) as response:
            data = json.loads(response.read().decode())

        extract = {
            "title": data.get("title"),
            "extract": data.get("extract"),
            "extract_html": data.get("extract_html"),
            "thumbnail": data.get("thumbnail", {}).get("source"),
            "url": data.get("content_urls", {}).get("desktop", {}).get("page"),
        }

        print(f"✓ Title: {extract['title']}")
        print(f"✓ Length: {len(extract['extract'])} chars")
        print(f"✓ URL: {extract['url']}")
        preview = (
            extract["extract"][:300] + "..."
            if len(extract["extract"]) > 300
            else extract["extract"]
        )
        print(f"\nPreview:\n{preview}\n")
        return extract

    except (HTTPError, URLError) as e:
        print(f"✗ Error fetching Wikipedia: {e}\n")
        return None


def main():
    """Main demonstration"""
    print("\n" + "=" * 70)
    print("Madrid Bus Network Quiz App - Capability Demo")
    print("=" * 70 + "\n")

    base_dir = Path(__file__).parent.parent
    rdf_file = base_dir / "rdf" / "madrid-bus-data-with-links-sample-100k.ttl"
    stop_id = "par_8_09765"

    if not rdf_file.exists():
        print(f"✗ RDF file not found: {rdf_file}")
        sys.exit(1)

    graph = load_rdf_graph(rdf_file)
    context = get_stop_context(graph, stop_id)
    if not context or not context["wikidata_id"]:
        print("✗ Cannot proceed without Wikidata link")
        sys.exit(1)

    wikidata_data = fetch_wikidata_entity_via_sparql(context["wikidata_id"])
    if not wikidata_data:
        print("✗ Cannot proceed without Wikidata data")
        sys.exit(1)

    wikipedia_extract = None
    if wikidata_data["wikipedia_sites"]:
        if "eswiki" in wikidata_data["wikipedia_sites"]:
            wiki_title = wikidata_data["wikipedia_sites"]["eswiki"]["title"]
            wikipedia_extract = fetch_wikipedia_extract(wiki_title, lang="es")
        elif "enwiki" in wikidata_data["wikipedia_sites"]:
            wiki_title = wikidata_data["wikipedia_sites"]["enwiki"]["title"]
            wikipedia_extract = fetch_wikipedia_extract(wiki_title, lang="en")

    print("=" * 70)
    print("SUMMARY - Data Available for Quiz Generation")
    print("=" * 70)
    print(f"📍 Bus Stop: {context['stop_name']}")
    print(f"📌 Local Area: {context['area_name']}")
    print(f"🌐 Wikidata: {context['wikidata_uri']}")
    print(f"📊 Label: {wikidata_data['label']}")
    print(f"📊 Description: {wikidata_data['description']}")
    print(f"📊 Properties: {len(wikidata_data['properties'])} available")
    if wikipedia_extract:
        print(f"📖 Wikipedia: Available ({len(wikipedia_extract['extract'])} chars)")
        print(f"📖 URL: {wikipedia_extract['url']}")
    else:
        print("📖 Wikipedia: Not available")
    print("\n✓ Application has sufficient data to generate quiz questions!")
    print("=" * 70)


if __name__ == "__main__":
    main()
