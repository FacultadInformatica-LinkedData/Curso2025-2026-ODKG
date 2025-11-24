import flask
import requests
from flask import request
from urllib.parse import quote
from flask import jsonify

#Conection to the database
GraphDB_endpoint = 'http://localhost:7200/repositories/Test_Bike'
headers = {"Accept": "application/sparql-results+json"}

routes_api = flask.Blueprint("routes_api", __name__, url_prefix="/api")

# Para cargar las estaciones de 10-10 en el front
@routes_api.route("/stations")
def get_stations():
    page = int(request.args.get("page", 0))
    sice_page = int(request.args.get("sice_page", 10))
    offset = page * 10
    query = f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX ex: <http://example.org/ns#>
            PREFIX wdt: <http://www.wikidata.org/prop/direct/>
            PREFIX wd: <http://www.wikidata.org/entity/>
            SELECT * WHERE {{
                ?station a ex:Bike_Station ;
                    ex:hasStation_name ?name_station ;
                    ex:hasAddress ?address ;
                    ex:hasCoord_y ?coord_x ;
                    ex:hasCoord_x ?coord_y .
                
                ?address a ex:Address ;
                    owl:sameAs ?wiki ;
                    ex:hasAddress_name ?name_address .
                
                SERVICE <https://query.wikidata.org/sparql>{{
                    ?wiki wdt:P31 wd:Q79007 ;
                                 wdt:P18 ?photo 
                }}
                
            }}limit {sice_page}
            offset {offset}
    """
    response = requests.get(GraphDB_endpoint, params={'query': query}, headers=headers)
    data = response.json()
    return data

# Nombre y coordenadas de todas las estaciones
@routes_api.route("/allStations")
def get_all_stations():
    query = f"""
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX ex: <http://example.org/ns#>
                SELECT * WHERE {{
                    ?station a ex:Bike_Station ;
                        ex:hasStation_name ?name_station ;
                        ex:hasCoord_y ?coord_x ;
                        ex:hasCoord_x ?coord_y .
                }}
        """
    response = requests.get(GraphDB_endpoint, params={'query': query}, headers=headers)
    data = response.json()
    return flask.jsonify(list(map(lambda x: {'name':x['name_station']['value'], 'coord':[x['coord_x']['value'], x['coord_y']['value']]}, data['results']['bindings'])))


@routes_api.route("/stations/<string:station_name>")
def get_station(station_name):
    query = f"""
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX owl: <http://www.w3.org/2002/07/owl#>
                PREFIX ex: <http://example.org/ns#>
                PREFIX wdt: <http://www.wikidata.org/prop/direct/>
                PREFIX wd: <http://www.wikidata.org/entity/>
                SELECT * WHERE {{
                    
                    <http://example.org/bikeStation/{quote(station_name)}> a ex:Bike_Station ;
                        ex:hasStation_name ?name_station ;
                        ex:hasAddress ?address ;
                        ex:hasCapacity ?capacity ;
                        ex:hasCoord_y ?coord_x ;
                        ex:hasCoord_x ?coord_y .
                    
                    ?address a ex:Address ;
                        owl:sameAs ?wiki
                    
                    SERVICE <https://query.wikidata.org/sparql> {{
                        ?wiki wdt:P31 wd:Q79007 ;
                            wdt:P18 ?photo ;
                    }}
                    
                }}"""
    response = requests.get(GraphDB_endpoint, params={'query': query}, headers=headers)
    data = response.json()
  
    return data

@routes_api.route("/route_info/<string:origin_station_name>/<string:destination_station_name>")
def get_route_info(origin_station_name, destination_station_name):
    query = f"""
        PREFIX ns: <http://example.org/ns#>

        SELECT ?originStationName ?destinationStationName
                (COUNT(?trip) AS ?numTravels)
                (AVG(?duration) AS ?avgDuration)
        WHERE {{
            ?trip a ns:Trial ;
                    ns:hasUnLockStation <http://example.org/bikeStation/{quote(origin_station_name)}> ;
                    ns:hasLockStation <http://example.org/bikeStation/{quote(destination_station_name)}> ;
                    ns:hasDuration ?duration .

            <http://example.org/bikeStation/{quote(origin_station_name)}> a ns:Bike_Station ;
                    ns:hasStation_name ?originStationName .

            <http://example.org/bikeStation/{quote(destination_station_name)}> a ns:Bike_Station ;
                    ns:hasStation_name ?destinationStationName .
        }}
        GROUP BY ?originStationName ?destinationStationName
    """

    response = requests.get(GraphDB_endpoint, params={'query': query}, headers=headers)
    data = response.json()
    results = data.get("results", {}).get("bindings", [])

    if results:
        row = results[0]
        num_travels = int(row["numTravels"]["value"])
        avg_duration = float(row["avgDuration"]["value"])
    else:
        num_travels = "0"
        avg_duration = "No data available for this route"

    return jsonify({
        "origin_station": origin_station_name,
        "destination_station": destination_station_name,
        "num_travels": num_travels,
        "avg_duration": avg_duration
    })


