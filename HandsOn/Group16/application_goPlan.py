import streamlit as st
from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
import folium
from streamlit_folium import st_folium





# Initialize the SPARQL wrapper
endpoint_url = "http://localhost:7200/repositories/handsOn5"
sparql = SPARQLWrapper(endpoint_url)
sparql.setReturnFormat(JSON)

def execute_sparql_query(query):
    """Execute a SPARQL query and return results."""
    sparql.setQuery(query)
    try:
        results = sparql.query().convert()
        return results
    except Exception as e:
        st.error(f"An error occurred while querying: {e}")
        return None

def extract_distinct_values(results, value_key):
    """Extract distinct values from query results."""
    values = set()
    for result in results["results"]["bindings"]:
        value = result[value_key]["value"].strip()
        if ',' in value:
            values.update(ac.strip() for ac in value.split(","))
        else:
            values.add(value)
    return sorted(values)

# Query to get accessibility options
access_query = """
PREFIX schema: <http://schema.org/>
PREFIX ns: <http://goPlan.linkeddata.es/>
PREFIX rr: <http://www.w3.org/ns/r2rml#>
PREFIX xsd:<http://www.w3.org/2001/XMLSchema#>
PREFIX rml: <http://semweb.mmlab.be/ns/rml#>
PREFIX ql:  <http://semweb.mmlab.be/ns/ql#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX vocab: <http://example.org#>
PREFIX owl: <http://www.w3.org/2002/07/owl#> 

SELECT DISTINCT ?access WHERE {
  ?place a schema:Place ;
         ns:accessibilityLevel ?access .
}
ORDER BY ?access
"""
access_results = execute_sparql_query(access_query)
available_access = extract_distinct_values(access_results, 'access') if access_results else []

# Query to get audience options
audience_query = """
PREFIX schema: <http://schema.org/>
PREFIX ns: <http://goPlan.linkeddata.es/>
PREFIX rr: <http://www.w3.org/ns/r2rml#>
PREFIX xsd:<http://www.w3.org/2001/XMLSchema#>
PREFIX rml: <http://semweb.mmlab.be/ns/rml#>
PREFIX ql:  <http://semweb.mmlab.be/ns/ql#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX vocab: <http://example.org#>
PREFIX owl: <http://www.w3.org/2002/07/owl#> 

SELECT DISTINCT ?audience WHERE {
  ?event a schema:Event ;
         schema:audience ?audience .
}
ORDER BY ?audience
"""
audience_results = execute_sparql_query(audience_query)
available_audiences = extract_distinct_values(audience_results, 'audience') if audience_results else []

# Query to get district options
district_query = """
PREFIX schema: <http://schema.org/>
PREFIX ns: <http://goPlan.linkeddata.es/>

SELECT DISTINCT ?district WHERE {
  ?place a schema:Place ;
         ns:district ?district .
}
ORDER BY ?district
"""
district_results = execute_sparql_query(district_query)
available_districts = extract_distinct_values(district_results, 'district') if district_results else []

# Query to get neighborhood options
neighborhood_query = """
PREFIX schema: <http://schema.org/>
PREFIX ns: <http://goPlan.linkeddata.es/>

SELECT DISTINCT ?neighborhood WHERE {
  ?place a schema:Place ;
         ns:neighborhood ?neighborhood .
}
ORDER BY ?neighborhood
"""
neighborhood_results = execute_sparql_query(neighborhood_query)
available_neighborhoods = extract_distinct_values(neighborhood_results, 'neighborhood') if neighborhood_results else []


with st.sidebar:
# Date range selection
  start_date = st.date_input("Start date", value=pd.to_datetime("2023-01-01"))
  end_date = st.date_input("End date", value=pd.to_datetime("2025-12-31"))
  is_free_check = st.checkbox("Free", value=False)
  selected_audiences = st.multiselect("Select Audiences", options=available_audiences)
  selected_access = st.multiselect("Select Accessibility", options=available_access)
  selected_districts = st.multiselect("Select Districts", options=available_districts)
  selected_neighborhoods = st.multiselect("Select Neighborhoods", options=available_neighborhoods)


# Define the SPARQL query with date filters
base_query = f"""
PREFIX schema: <http://schema.org/>
PREFIX ns: <http://goPlan.linkeddata.es/>
PREFIX rr: <http://www.w3.org/ns/r2rml#>
PREFIX xsd:<http://www.w3.org/2001/XMLSchema#>
PREFIX rml: <http://semweb.mmlab.be/ns/rml#>
PREFIX ql:  <http://semweb.mmlab.be/ns/ql#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX vocab: <http://example.org#>
PREFIX owl: <http://www.w3.org/2002/07/owl#> 

SELECT ?event ?eventName ?startDate ?endDate ?audience ?isFree
       ?place ?placeName ?latitude ?longitude
       ?access ?district ?neighborhood ?eventUrl ?placeUrl
WHERE {{
  # Evento y sus datos básicos
  ?event a schema:Event ;
         ns:eventName ?eventName ;
         schema:startDate ?startDate ;
         schema:endDate ?endDate ;
         schema:audience ?audience .
  OPTIONAL {{ ?event schema:isAccessibleForFree ?isFree . }}
  OPTIONAL {{ ?event owl:sameAs ?eventUrl . }}

  # Enlace al lugar (todo OPTIONAL por si faltan datos de Place)
  OPTIONAL {{
    ?event ns:hasPlace ?place .
    ?place a schema:Place ;
           ns:placeName ?placeName ;
           ns:accessibilityLevel ?access ;
           ns:district ?district ;
           ns:neighborhood ?neighborhood ;
           schema:latitude ?latitude ;
           schema:longitude ?longitude .
    OPTIONAL {{ ?place owl:sameAs ?placeUrl . }}
  }}

    # Filtro de fechas: tu dataset usa xsd:date (no dateTime)
  FILTER (?startDate >= "{start_date.isoformat()}"^^xsd:date &&
          ?startDate <= "{end_date.isoformat()}"^^xsd:date)

  # Filtros dinámicos (se incluyen sólo si el usuario selecciona algo)
  {"FILTER (lcase(str(?isFree)) = \"gratuito\") ." if is_free_check else ""}

  {("FILTER (" + " || ".join([f'contains(lcase(str(?audience)), \"{a.lower()}\")' for a in selected_audiences]) + ") .")
    if selected_audiences else ""}

  {("FILTER (" + " && ".join([f'contains(lcase(str(?access)), \"{a.lower()}\")' for a in selected_access]) + ") .")
    if selected_access else ""}

  {("FILTER (" + " || ".join(
       [f'contains(lcase(str(?district)), \"{d.lower()}\")' for d in selected_districts] +
       [f'contains(lcase(str(?neighborhood)), \"{n.lower()}\")' for n in selected_neighborhoods]
     ) + ") .")
    if (selected_districts or selected_neighborhoods) else ""}
}}
ORDER BY ?startDate
"""

# Ejecutar la query y procesar resultados
event_results = execute_sparql_query(base_query)

data = []
if event_results and event_results.get("results", {}).get("bindings"):
    for b in event_results["results"]["bindings"]:
        def get(v):
            return b.get(v, {}).get("value")

        data.append({
            "Event IRI":    get("event"),
            "Event Name":   get("eventName"),
            "Start Date":   get("startDate"),
            "End Date":     get("endDate"),
            "Audience":     get("audience"),
            "Is Free":      get("isFree"),
            "Event URL":    get("eventUrl"),
            "Place IRI":    get("place"),
            "Place":        get("placeName"),
            "Latitude":     float(get("latitude")) if get("latitude") else None,
            "Longitude":    float(get("longitude")) if get("longitude") else None,
            "Access":       get("access"),
            "District":     get("district"),
            "Neighborhood": get("neighborhood"),
            "Place Url":    get("placeUrl"),
        })

if data:
    df = pd.DataFrame(data)

    # Agrupar por coordenadas (evita múltiples pins en el mismo sitio)
    grouped_df = df.groupby(['Latitude', 'Longitude'], dropna=True).agg({
        'Event Name': lambda x: list(dict.fromkeys(x)),   # únicos manteniendo orden
        'Start Date': lambda x: list(dict.fromkeys(x)),
        'Audience':   lambda x: list(dict.fromkeys(x)),
        'Event URL':  lambda x: list(dict.fromkeys(x)),
        'Place':      'first',
        'Place Url':  'first',
        'Access':     'first',
        'District':   'first',
        'Neighborhood':'first'
    }).reset_index()

    m = folium.Map(location=[40.4168, -3.7038], zoom_start=12)

    for _, row in grouped_df.iterrows():
        popup_html = "<b>Events:</b>"
        for name, start, aud, url in zip(
            row['Event Name'],
            row['Start Date'],
            row['Audience'],
            row['Event URL']
        ):
            popup_html += f"""
            <div class="box" style="border:1px solid #000; border-radius:2px; padding:5px 3px; margin:5px auto;">
              <a href="{url or '#'}" target="_blank">{name}</a><br>
              <b>Start Date:</b> {start}<br>
              <b>Audience:</b> {aud}
            </div>
            """

        # Info del lugar
        popup_html += f"""
            <b>Place: </b>{row['Place'] or '—'}<br>
            <b>Access:</b> {row['Access'] or '—'}<br>
            <b>District:</b> {row['District'] or '—'}<br>
            <b>Neighborhood:</b> {row['Neighborhood'] or '—'}<br>
        """
        if row['Place Url']:
            popup_html += f'<a href="{row["Place Url"]}" target="_blank">More info</a>'

        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=folium.Popup(popup_html, max_width=320)
        ).add_to(m)

    st.write("### Map of Events")
    st_folium(m, width=1300, height=800)

    st.write("### Table")
    # Convierte fechas a datetime para ordenar
    for c in ["Start Date", "End Date"]:
        df[c] = pd.to_datetime(df[c], errors="coerce")
    st.dataframe(df.sort_values("Start Date")[[
        "Event Name","Start Date","End Date","Audience","Is Free",
        "Place","Access","District","Neighborhood","Event URL","Place Url"
    ]])
else:
    st.info("No events found for these filters, try again!")
