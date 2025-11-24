from rdflib import Graph, Namespace, OWL
from functools import lru_cache
from urllib.parse import unquote, urlparse
import requests


SC = Namespace("http://smartcity.linkeddata.es/lcc/ontology#")
SCHEMA = Namespace("https://schema.org/")
GEO = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
DBO = Namespace("http://dbpedia.org/ontology/")
OWL = Namespace("http://www.w3.org/2002/07/owl#")#NUEVO

ONTO_FILE = "../ontology/ontology.ttl"
DATA_FILE = "../data/tripletas-Final.nt"
    

@lru_cache(maxsize=1)
def get_graph() -> Graph:
    g = Graph()
    g.parse(ONTO_FILE, format="turtle")
    g.parse(DATA_FILE, format="nt")
    return g

#NUEVO
# ============================
#  Helpers para usar Wikidata
# ============================
def _qid_from_uri(uri: str | None) -> str | None:
    """Extrae el QID (Q1234) de un URI de Wikidata."""
    if not uri:
        return None
    if "wikidata.org" not in uri:
        return None
    return uri.rsplit("/", 1)[-1]

#NUEVO
@lru_cache(maxsize=512)
def fetch_wikidata_entity(qid: str) -> dict | None:
    """
    Descarga una entidad de Wikidata y la devuelve como dict.
    AHORA incluye un User-Agent explícito, como pide Wikidata.
    """
    if not qid:
        return None

    url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"

    # ⚠️ Personalizad esto con algo vuestro si queréis (nombre del proyecto y un email/web)
    headers = {
        "User-Agent": (
            "MadridSmartCityStudentApp/1.0 "
            "(https://example.org/; mailto:student@example.com)"
        ),
        "Accept": "application/json",
    }

    try:
        r = requests.get(url, headers=headers, timeout=8)

        if not r.ok:
            # Deja este print un rato por si hay otro problema
            print("DEBUG WD: respuesta NO OK", qid, r.status_code, r.text[:200])
            return None

        data = r.json()
        ents = data.get("entities", {})
        ent = ents.get(qid) or ents.get(qid.strip())

        if ent is None:
            print("DEBUG WD: no se ha encontrado entidad para", qid)
        return ent

    except Exception as e:
        print("DEBUG WD: excepción en fetch_wikidata_entity:", repr(e))
        return None


#NUEVO
def _wd_label(ent: dict | None, lang: str = "es") -> str | None:
    """Devuelve la etiqueta legible de una entidad de Wikidata."""
    if not ent:
        return None
    labels = ent.get("labels", {})
    if lang in labels:
        return labels[lang]["value"]
    if "en" in labels:
        return labels["en"]["value"]
    if labels:
        # cualquier otro idioma
        return next(iter(labels.values()))["value"]
    return None

#NUEVO
def _wd_claims(ent: dict | None, pid: str) -> list:
    """Devuelve la lista de claims para una propiedad Pxxxx concreta."""
    if not ent:
        return []
    return ent.get("claims", {}).get(pid, []) or []

#NUEVO
def _wd_entity_list(ent: dict | None, pid: str, lang: str = "es") -> list[str]:
    """
    Devuelve una lista de etiquetas (str) para claims cuyo valor es otra entidad
    (ej: head of government, executive body, shares border with, etc.).
    """
    out: list[str] = []
    for c in _wd_claims(ent, pid):
        dv = c.get("mainsnak", {}).get("datavalue")
        if not dv or dv.get("type") != "wikibase-entityid":
            continue
        v = dv.get("value", {})
        qid = v.get("id")
        if not qid:
            continue
        ent2 = fetch_wikidata_entity(qid)
        label = _wd_label(ent2, lang=lang) or qid
        out.append(label)
    # quitar duplicados manteniendo orden
    return list(dict.fromkeys(out))

#NUEVO
def _wd_string_value(ent: dict | None, pid: str) -> str | None:
    """
    Devuelve un literal "simple": string, url o monolingualtext.text.
    Se usa para dirección, CP, teléfono, email, web...
    """
    for c in _wd_claims(ent, pid):
        dv = c.get("mainsnak", {}).get("datavalue")
        if not dv:
            continue
        t = dv.get("type")
        v = dv.get("value")
        if t == "string":
            return str(v)
        if t == "url":
            return str(v)
        if t == "monolingualtext" and isinstance(v, dict):
            txt = v.get("text")
            if txt:
                return str(txt)
    return None

#NUEVO
def _wd_population(ent: dict | None) -> dict | None:
    """
    Extrae la población (P1082) y, si está, el año (cualificador P585 point in time).
    Devuelve algo como {"value": 248443, "year": 2023} o None.
    """
    best_amount = None
    best_year = None

    for c in _wd_claims(ent, "P1082"):  # population
        mainsnak = c.get("mainsnak", {})
        dv = mainsnak.get("datavalue")
        if not dv or dv.get("type") != "quantity":
            continue
        v = dv.get("value", {})
        amount = v.get("amount")
        if amount is None:
            continue
        # amount viene tipo "+248443"
        try:
            amount_num = int(str(amount).lstrip("+"))
        except Exception:
            continue

        # mirar cualificador point in time (P585) si existe
        year = None
        quals = c.get("qualifiers", {})
        for qc in quals.get("P585", []):
            dv2 = qc.get("datavalue")
            if not dv2 or dv2.get("type") != "time":
                continue
            tval = dv2.get("value", {}).get("time")  # "+2023-01-01T00:00:00Z"
            if tval and len(tval) >= 5:
                try:
                    year = int(tval[1:5])
                except Exception:
                    year = None
            break

        # nos quedamos con la más reciente, o la primera si ninguna tiene año
        if best_amount is None:
            best_amount, best_year = amount_num, year
        else:
            if year is not None and (best_year is None or year > best_year):
                best_amount, best_year = amount_num, year

    if best_amount is None:
        return None
    return {"value": best_amount, "year": best_year}




# ===============================================================
# NUEVAS funciones auxiliares para extraer propiedades adicionales
# ===============================================================

def _wd_image(ent: dict | None) -> str | None:
    """Devuelve una URL directa a la imagen (P18) desde Wikimedia Commons."""
    for c in _wd_claims(ent, "P18"):
        dv = c.get("mainsnak", {}).get("datavalue")
        if not dv:
            continue
        filename = dv.get("value")
        if filename:
            # URL pública directa
            from urllib.parse import quote
            return "https://commons.wikimedia.org/wiki/Special:FilePath/" + quote(filename)
    return None


def _wd_inception(ent: dict | None) -> int | None:
    """Devuelve el año de 'inception' (P571) si existe."""
    for c in _wd_claims(ent, "P571"):
        dv = c.get("mainsnak", {}).get("datavalue")
        if not dv or dv.get("type") != "time":
            continue
        time_str = dv.get("value", {}).get("time")  # "+1975-01-01T00:00:00Z"
        if time_str and len(time_str) >= 5:
            try:
                return int(time_str[1:5])
            except Exception:
                return None
    return None


def _wd_part_of(ent: dict | None, pid: str, lang="es") -> list[str]:
    """
    Similar a _wd_entity_list(), pero lo dejamos explícito para 'part of' 
    Devuelve etiquetas humanas de las entidades que aparezcan en P361 
    """
    out = []
    for c in _wd_claims(ent, "P361"):
        dv = c.get("mainsnak", {}).get("datavalue")
        if not dv or dv.get("type") != "wikibase-entityid":
            continue
        qid = dv.get("value", {}).get("id")
        if not qid:
            continue
        ent2 = fetch_wikidata_entity(qid)
        label = _wd_label(ent2, lang=lang) or qid
        out.append(label)
    return list(dict.fromkeys(out))  # quita duplicados manteniendo orden




#NUEVO: FUNCION PRINCIPAL QUE OBTIENE DATOS DE WIKIDATA
def get_linked_wiki_info(facility_uri: str, lang: str = "es") -> dict:
    """
    Dada la URI local de una facility, busca los owl:sameAs hacia Wikidata para:
      - la propia facility
      - su barrio
      - su distrito
      - su municipio

    Y para cada uno extrae propiedades concretas de Wikidata:
      * Municipio / Distrito:
          - office held by head of government (P1313)
          - head of government (P6)
          - executive body (P208)
          - population (P1082)
      * Barrio:
          - population (P1082)
          - shares border with (P47)
      * Facility:
          - street address (P6375)
          - postal code (P281)
          - official website (P856)
          - image (P18)
          - foundation date (P571)
          - part of (P361)
    """
    g = get_graph()
    q = f"""
    PREFIX schema: <{SCHEMA}>
    PREFIX sc: <{SC}>
    PREFIX dbo: <{DBO}>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>

    SELECT DISTINCT
      ?facWiki
      ?nh ?nhName ?nhWiki
      ?dist ?distName ?distWiki
      ?mun ?munName ?munWiki
    WHERE {{
      OPTIONAL {{
        <{facility_uri}> owl:sameAs ?facWiki .
        FILTER(CONTAINS(STR(?facWiki), "wikidata.org"))
      }}

      OPTIONAL {{
        <{facility_uri}> schema:containedInPlace ?nh .
        OPTIONAL {{ ?nh schema:name ?nhName . }}
        OPTIONAL {{
          ?nh owl:sameAs ?nhWiki .
          FILTER(CONTAINS(STR(?nhWiki), "wikidata.org"))
        }}

        OPTIONAL {{
          ?nh sc:locatedInDistrict ?dist .
          OPTIONAL {{ ?dist schema:name ?distName . }}
          OPTIONAL {{
            ?dist owl:sameAs ?distWiki .
            FILTER(CONTAINS(STR(?distWiki), "wikidata.org"))
          }}

          OPTIONAL {{
            ?dist sc:locatedInMunicipality ?mun .
            OPTIONAL {{ ?mun schema:name ?munName . }}
            OPTIONAL {{
              ?mun owl:sameAs ?munWiki .
              FILTER(CONTAINS(STR(?munWiki), "wikidata.org"))
            }}
          }}
        }}
      }}
    }}
    LIMIT 1
    """

    rows = list(g.query(q))
    r = rows[0] if rows else None

    def _s(attr: str):
        if not r:
            return None
        v = getattr(r, attr, None)
        return str(v) if v else None

    fac_uri_wd = _s("facWiki")
    nh_label = _s("nhName")
    nh_uri_wd = _s("nhWiki")
    dist_label = _s("distName")
    dist_uri_wd = _s("distWiki")
    mun_label = _s("munName")
    mun_uri_wd = _s("munWiki")

    def _build_place_info(uri: str | None, fallback_label: str | None, kind: str) -> dict:
        """
        kind ∈ {"municipality","district","neighbourhood","facility"}
        """
        info: dict = {
            "uri": uri,
            "label": fallback_label,
            "population": None,
            "office": [],
            "head": [],
            "executive_body": [],
            "borders": [],
            "street_address": None,
            "postal_code": None,
            "phone": None,
            "email": None,
            "website": None,
            "image": None,        
            "inception": None,    
            "part_of": []  
        }

        qid = _qid_from_uri(uri)
        #print(f"DEBUG WD: _build_place_info kind={kind} uri={uri} qid={qid}")

        ent = fetch_wikidata_entity(qid) if qid else None
        #print(f"DEBUG WD:   entidad encontrada? {bool(ent)}")

        if ent:
            # Etiqueta por defecto si no viene del CSV
            if not info["label"]:
                info["label"] = _wd_label(ent, lang=lang)
                #print(f"DEBUG WD:   label inferida ({kind}): {info['label']}")

            # Población (municipio, distrito, barrio)
            if kind in ("municipality", "district", "neighbourhood"):
                info["population"] = _wd_population(ent)
                #print(f"DEBUG WD:   población ({kind}): {info['population']}")

            # Gobierno (municipio / distrito)
            if kind in ("municipality", "district"):
                info["office"] = _wd_entity_list(ent, "P1313", lang=lang)
                info["head"] = _wd_entity_list(ent, "P6", lang=lang)
                info["executive_body"] = _wd_entity_list(ent, "P208", lang=lang)
                #print(f"DEBUG WD:   office={info['office']}")
                #print(f"DEBUG WD:   head={info['head']}")
                #print(f"DEBUG WD:   exec={info['executive_body']}")

            # Barrio: límites
            if kind == "neighbourhood":
                info["borders"] = _wd_entity_list(ent, "P47", lang=lang)
                #print(f"DEBUG WD:   borders={info['borders']}")

            # Facility: dirección, web, etc.
            if kind == "facility":
                info["street_address"] = _wd_string_value(ent, "P6375")
                info["postal_code"] = _wd_string_value(ent, "P281")
                info["phone"] = _wd_string_value(ent, "P1329")
                info["email"] = _wd_string_value(ent, "P968")
                info["website"] = _wd_string_value(ent, "P856")
                info["image"] = _wd_image(ent)             
                info["inception"] = _wd_inception(ent)  
                info["part_of"] = _wd_part_of(ent, "P361")   
                #print(f"DEBUG WD:   street={info['street_address']}")
                #print(f"DEBUG WD:   postal={info['postal_code']}")
                #print(f"DEBUG WD:   phone={info['phone']}")
                #print(f"DEBUG WD:   email={info['email']}")
                #print(f"DEBUG WD:   web={info['website']}")

        return info

    return {
        "municipality": _build_place_info(mun_uri_wd, mun_label, "municipality"),
        "district": _build_place_info(dist_uri_wd, dist_label, "district"),
        "neighbourhood": _build_place_info(nh_uri_wd, nh_label, "neighbourhood"),
        "facility": _build_place_info(fac_uri_wd, None, "facility"),
    }


# Mapa “bonito” -> nombre mostrado en UI -> nombre local de clase en tu ontología
FACILITY_CLASS_MAP = {
    # Clases Principales
    "Library": "sc:Library",
    "Park/Garden": "sc:Park",
    "Sports Center": "sc:SportsFacility",
    "Educational Institution": "sc:EducationalInstitution",
    # Mas subclases
    "Residence hall": "sc:ResidenceHall",
    "Faculty": "sc:Faculty",
    "University school": "sc:UniversitySchool",
    "Other centers": "sc:OtherCenters",

    "Gym": "sc:Gym",
    "FootballField": "sc:FootballField",
    "SwimmingPool": "sc:SwimmingPool",
    "Tennis court": "sc:TennisCourt",
    "Climbing wall": "sc:ClimbingWall",
    "Rowing pier": "sc:RowingPier",
    "Stadium": "sc:Stadium",
    "Basketball court": "sc:BasketballCourt"
}



# Las 4 clases principales de facilities (primer desplegable)
FACILITY_MAIN_TYPES = [
    "Library",
    "Park/Garden",
    "Sports Center",
    "Educational Institution",
]

# Para cada clase principal, qué opciones de tipo concreto se muestran
FACILITY_SUBTYPES_BY_MAIN = {
    # Para Library y Park/Garden, el propio tipo principal es la única clase concreta
    "Library": ["Library"],
    "Park/Garden": ["Park/Garden"],

    # Sports Center: tipo genérico + subclases deportivas
    "Sports Center": [
        "Sports Center",      # todas las instalaciones deportivas
        "Gym",
        "FootballField",
        "SwimmingPool",
        "Tennis court",
        "Climbing wall",
        "Rowing pier",
        "Stadium",
        "Basketball court",
    ],

    # Educational Institution: tipo genérico + subclases
    "Educational Institution": [
        "Educational Institution",  # todas las educativas
        "Residence hall",
        "Faculty",
        "University school",
        "Other centers",
    ],

}
# Todas las clases seleccionables en el segundo desplegable
ALL_FACILITY_TYPES = list(FACILITY_CLASS_MAP.keys())

def _norm_coord(val: object, kind: str) -> float | None:
    """
    Normaliza coordenadas provenientes de literales raros (p.ej. '4.045.750.817.868.430').
    kind: 'lat' | 'lon'
    """
    if val is None:
        return None
    s = str(val).strip()
    # Unificar separadores
    s = s.replace(" ", "").replace(",", ".")
    # Si hay más de un punto -> vienen "agrupados": quita todos y re-coloca el decimal
    if s.count(".") > 1:
        s = s.replace(".", "")  # quita todos
        # inserta '.' tras los grados (2 dígitos para lat 40.., 1 dígito para lon -3..)
        if kind == "lat":
            # ej: '4045750817868430' -> '40.45750817868430'
            if len(s) >= 3:
                s = s[:2] + "." + s[2:]
        else:  # lon (Madrid ~ -3.xxx)
            # conserva signo si lo hay
            sign = ""
            if s.startswith("-"):
                sign, s = "-", s[1:]
            if len(s) >= 2:
                s = sign + s[:1] + "." + s[1:]
            else:
                s = sign + s  # no tocar si es rarísimo
    try:
        f = float(s)
        # sanity-check
        if kind == "lat" and not (-90 <= f <= 90):
            return None
        if kind == "lon" and not (-180 <= f <= 180):
            return None
        return f
    except Exception:
        return None

def _pretty_class(uri_or_label: str | None) -> str | None:
    """Devuelve un nombre de clase legible (sin prefijos ni URIs)."""
    if not uri_or_label:
        return None
    s = str(uri_or_label)
    # Quita prefijos schema:, sc:, o URIs completas
    s = s.replace("schema:", "").replace("sc:", "")
    if "/" in s or "#" in s:
        s = s.split("/")[-1].split("#")[-1]
    return s


def get_facilities_by_type(class_label: str):
    g = get_graph()
    local = FACILITY_CLASS_MAP[class_label]

    q = f"""
    PREFIX schema: <{SCHEMA}>
    PREFIX sc: <{SC}>
    PREFIX geo: <{GEO}>
    PREFIX dbo: <{DBO}>

    SELECT DISTINCT ?facility ?name ?lat ?long ?tel ?email
                    ?nhName ?distName ?munName ?classLocal 
    WHERE {{
      ?facility a ?class ;
                schema:name ?name .

      # Filtrar instalaciones por clase exacta (ontology# o resource/)
      FILTER(
        ?class = {local} ||
        STR(?class) = REPLACE(STR({local}), "ontology#", "resource/")
      )

      ########################################
      ## TERRITORIO CORRECTO (ARREGLADO)
      ########################################

      OPTIONAL {{
        ?facility schema:containedInPlace ?nh .
        ?nh schema:name ?nhName .
        ?nh sc:locatedInDistrict ?dist .
        ?dist schema:name ?distName .
        ?dist sc:locatedInMunicipality ?mun .
        ?mun schema:name ?munName .
      }}

      OPTIONAL {{ ?facility geo:lat ?lat . }}
      OPTIONAL {{ ?facility geo:long ?long . }}
      OPTIONAL {{ ?facility schema:telephone ?tel . }}
      OPTIONAL {{ ?facility schema:email ?email . }}

      BIND(REPLACE(REPLACE(STR(?class), "^.*/", ""), "^.*#", "") AS ?classLocal)
    }}
    """
    rows = g.query(q)
    results = []
    for r in rows:
        results.append({
            "uri": str(r.facility),
            "name": str(r.name),
            "lat": _norm_coord(r.lat, "lat"),
            "long": _norm_coord(r.long, "lon"),
            "telephone": str(r.tel) if r.tel else None,
            "email": str(r.email) if r.email else None,
            "neighbourhood": str(r.nhName) if r.nhName else None,
            "district": str(r.distName) if r.distName else None,
            "municipality": str(r.munName) if r.munName else None,
            "class": _pretty_class(r.classLocal),
        })
    return results


def get_neighbourhoods():
    """Lista de barrios (uri, nombre) detectados a partir de las facilities."""
    g = get_graph()
    q = f"""
    PREFIX schema: <{SCHEMA}>
    SELECT DISTINCT ?nh (REPLACE(STR(?nh), "^.*neighbourhood/", "") AS ?rawName)
    WHERE {{
      ?facility schema:containedInPlace ?nh .
      FILTER(CONTAINS(LCASE(STR(?nh)), "neighbourhood"))
    }}
    ORDER BY LCASE(STR(?rawName))
    """
    results = []
    for r in g.query(q):
        uri = str(r.nh)
        raw_name = str(r.rawName)
        name = unquote(raw_name)  # decodifica %20, %C3... → espacios y acentos normales
        results.append((uri, name))
    return results


def get_facilities_in_neighbourhood(nh_uri: str):
    g = get_graph()
    q = f"""
    PREFIX sc: <{SC}>
    PREFIX schema: <{SCHEMA}>
    PREFIX geo: <{GEO}>
    PREFIX dbo: <{DBO}>

    SELECT DISTINCT ?facility ?name ?lat ?long ?tel ?email
                    ?classLocal ?distName ?munName
    WHERE {{
        ?facility schema:containedInPlace <{nh_uri}> ;
                  schema:name ?name .

        ########################################
        ## TERRITORIO CORRECTO (ARREGLADO)
        ########################################

        OPTIONAL {{
            <{nh_uri}> sc:locatedInDistrict ?dist .
            ?dist schema:name ?distName .
            ?dist sc:locatedInMunicipality ?mun .
            ?mun schema:name ?munName .
        }}

        OPTIONAL {{ ?facility geo:lat ?lat . }}
        OPTIONAL {{ ?facility geo:long ?long . }}
        OPTIONAL {{ ?facility schema:telephone ?tel . }}
        OPTIONAL {{ ?facility schema:email ?email . }}

        OPTIONAL {{
            ?facility a ?class .
            FILTER(?class != sc:Facility)
            BIND(REPLACE(REPLACE(STR(?class), "^.*/", ""), "^.*#", "") AS ?classLocal)
        }}
    }}
    ORDER BY ?name
    """

    rows = g.query(q)
    out = []
    for r in rows:
        out.append({
            "uri": str(r.facility),
            "name": str(r.name),
            "lat": _norm_coord(r.lat, "lat"),
            "long": _norm_coord(r.long, "lon"),
            "telephone": str(r.tel) if r.tel else None,
            "email": str(r.email) if r.email else None,
            "class": _pretty_class(r.classLocal),
            "district": str(r.distName) if r.distName else None,
            "municipality": str(r.munName) if r.munName else None,
        })
    return out

def get_districts():
    """Lista de distritos (uri, nombre) detectados a partir de las facilities."""
    g = get_graph()
    q = f"""
    PREFIX schema: <{SCHEMA}>
    PREFIX dbo: <{DBO}>
    SELECT DISTINCT ?district (REPLACE(STR(?district), "^.*district/", "") AS ?rawName)
    WHERE {{
      ?facility schema:containedInPlace ?nh .
      ?nh sc:locatedInDistrict ?district .
      FILTER(CONTAINS(LCASE(STR(?district)), "district"))
    }}
    ORDER BY LCASE(STR(?rawName))
    """
    results = []
    for r in g.query(q):
        uri = str(r.district)
        raw_name = str(r.rawName)
        name = unquote(raw_name)  # decodifica %20, %C3... → espacios y acentos normales
        results.append((uri, name))
    return results


def get_neighbourhoods_in_district(district_uri: str):
    """Devuelve todos los barrios dentro de un distrito específico."""
    g = get_graph()
    q = f"""
    PREFIX schema: <{SCHEMA}>
    PREFIX dbo: <{DBO}>
    SELECT DISTINCT ?nh (REPLACE(STR(?nh), "^.*neighbourhood/", "") AS ?rawName)
    WHERE {{
      ?facility schema:containedInPlace ?nh .
      ?nh sc:locatedInDistrict <{district_uri}> .
      FILTER(CONTAINS(LCASE(STR(?nh)), "neighbourhood"))
    }}
    ORDER BY LCASE(STR(?rawName))
    """
    results = []
    for r in g.query(q):
        uri = str(r.nh)
        raw_name = str(r.rawName)
        name = unquote(raw_name)  # decodifica %20, %C3... → espacios y acentos normales
        results.append((uri, name))
    return results


def get_nearby_transport(facility_uri: str):
    """
    Devuelve el transporte cercano (Subway, Bus, Train) con sus líneas y estaciones.
    """
    g = get_graph()
    q = f"""
    PREFIX sc: <{SC}>
    PREFIX schema: <{SCHEMA}>
    PREFIX dbo: <{DBO}>

    SELECT DISTINCT ?transport ?transportClass ?line ?station
    WHERE {{
      <{facility_uri}> sc:hasNearby ?transport .
      ?transport a ?transportClass .
      FILTER(?transportClass IN (sc:Subway, sc:Bus, sc:Train))

      OPTIONAL {{ ?transport sc:hasLines ?line . }}
      OPTIONAL {{ ?transport sc:hasStations ?station . }}
    }}
    """

    rows = g.query(q)

    # Construcción de estructura completa
    transport = {
        "Subway": {},
        "Bus": {},
        "Train": {}
    }

    for r in rows:
        uri = str(r.transport)
        t_class = str(r.transportClass).split("#")[-1]  # Subway | Bus | Train
        name = uri.split("resource/")[-1]
        name = unquote(name)

        if name not in transport[t_class]:
            transport[t_class][name] = {"lines": set(), "stations": set()}

        if r.line:
            transport[t_class][name]["lines"].add(str(r.line))

        if r.station:
            transport[t_class][name]["stations"].add(str(r.station))

    # Convertir sets → listas
    for t in transport:
        for name in transport[t]:
            transport[t][name]["lines"] = list(transport[t][name]["lines"])
            transport[t][name]["stations"] = list(transport[t][name]["stations"])

    return transport


#******#
def get_facilities_by_type_and_neighbourhood(class_label: str, nh_uri: str):
    g = get_graph()
    local = FACILITY_CLASS_MAP[class_label]

    q = f"""
    PREFIX schema: <{SCHEMA}>
    PREFIX sc: <{SC}>
    PREFIX geo: <{GEO}>
    PREFIX dbo: <{DBO}>

    SELECT DISTINCT ?facility ?name ?lat ?long ?tel ?email
                    ?nhName ?distName ?munName ?classLocal
    WHERE {{
        ?facility a ?class ;
                  schema:name ?name ;
                  schema:containedInPlace <{nh_uri}> .

        FILTER(
            ?class = {local} ||
            STR(?class) = REPLACE(STR({local}), "ontology#", "resource/")
        )

        OPTIONAL {{ <{nh_uri}> schema:name ?nhName . }}
        OPTIONAL {{
            <{nh_uri}> sc:locatedInDistrict ?dist .
            ?dist schema:name ?distName .
            ?dist sc:locatedInMunicipality ?mun .
            ?mun schema:name ?munName .
        }}

        OPTIONAL {{ ?facility geo:lat ?lat . }}
        OPTIONAL {{ ?facility geo:long ?long . }}
        OPTIONAL {{ ?facility schema:telephone ?tel . }}
        OPTIONAL {{ ?facility schema:email ?email . }}

        BIND(REPLACE(REPLACE(STR(?class), "^.*/", ""), "^.*#", "") AS ?classLocal)
    }}
    """

    rows = g.query(q)
    results = []
    for r in rows:
        results.append({
            "uri": str(r.facility),
            "name": str(r.name),
            "lat": _norm_coord(r.lat, "lat"),
            "long": _norm_coord(r.long, "lon"),
            "telephone": str(r.tel) if r.tel else None,
            "email": str(r.email) if r.email else None,
            "class": _pretty_class(r.classLocal),
            "neighbourhood": str(r.nhName) if r.nhName else None,
            "district": str(r.distName) if r.distName else None,
            "municipality": str(r.munName) if r.munName else None,
        })
    return results


def get_facilities_by_types(types_list, neighbourhoods_list=None):
    """
    Igual que get_facilities_by_type_and_neighbourhood, pero aceptando múltiples tipos
    y múltiples barrios a la vez.
    """
    g = get_graph()

    # 1. Manejo de tipos de facility (Cláusula de Clase)
    # ------------------------------------------------------------------
    if not types_list:
        return []

    # Convertimos tipos visibles → URIs locales (sc:Library, schema:Park...)
    locals_uris = [FACILITY_CLASS_MAP[t] for t in types_list if t in FACILITY_CLASS_MAP]

    # Si por alguna razón no se mapea nada, no ejecutamos la query
    if not locals_uris:
        return []

    # Construir el filtro de clases (FILTER(?class = local1 || ?class = local2...))
    class_filter_conditions = []
    for local in locals_uris:
        # Incluye las formas 'ontology#' y 'resource/'
        condition = f"?class = {local} || STR(?class) = REPLACE(STR({local}), \"ontology#\", \"resource/\")"
        class_filter_conditions.append(condition)

    class_filter = " || ".join(class_filter_conditions)

    # 2. Manejo de barrios (Cláusulas de Territorio y Filtro)
    # ------------------------------------------------------------------
    if neighbourhoods_list:
        # Se están filtrando barrios: JOIN obligatorio a ?nh y FILTER específico
        nh_filter = "FILTER (?nh IN (" + " ".join(f"<{uri}>" for uri in neighbourhoods_list) + "))"
        
        # Debe haber un patrón obligatorio a ?nh para que el FILTER funcione
        nh_join = """
            ?facility schema:containedInPlace ?nh .
            OPTIONAL { ?nh schema:name ?nhName . }
            
            # Uniones más flexibles para territorio (OPTIONAL anidados)
            OPTIONAL {
                ?nh sc:locatedInDistrict ?dist .
                OPTIONAL { ?dist schema:name ?distName . }
                OPTIONAL { 
                    ?dist sc:locatedInMunicipality ?mun .
                    OPTIONAL { ?mun schema:name ?munName . }
                }
            }
        """
    else:
        # No se está filtrando por barrio (Todos): Uniones OPTIONAL para el territorio
        nh_filter = ""
        nh_join = """
            OPTIONAL { ?facility schema:containedInPlace ?nh . 
                       OPTIONAL { ?nh schema:name ?nhName . }
            }
            OPTIONAL { 
                ?nh sc:locatedInDistrict ?dist .
                OPTIONAL { ?dist schema:name ?distName . }
            }
            OPTIONAL { 
                ?dist sc:locatedInMunicipality ?mun .
                OPTIONAL { ?mun schema:name ?munName . }
            }
        """

    # 3. Construcción de la Consulta SPARQL
    # ------------------------------------------------------------------
    q = f"""
    PREFIX schema: <{SCHEMA}>
    PREFIX sc: <{SC}>
    PREFIX geo: <{GEO}>
    PREFIX dbo: <{DBO}>

    SELECT DISTINCT ?facility ?name ?lat ?long ?tel ?email
                      ?nhName ?distName ?munName ?classLocal
    WHERE {{
        ?facility a ?class ;
                    schema:name ?name .

        {nh_join}

        OPTIONAL {{ ?facility geo:lat ?lat . }}
        OPTIONAL {{ ?facility geo:long ?long . }}
        OPTIONAL {{ ?facility schema:telephone ?tel . }}
        OPTIONAL {{ ?facility schema:email ?email . }}

        # El filtro de clases ya está garantizado para no estar vacío
        FILTER ( {class_filter} )
        
        {nh_filter}

        BIND(REPLACE(REPLACE(STR(?class), "^.*/", ""), "^.*#", "") AS ?classLocal)
    }}
    """

    # 4. Ejecución y Formato
    # ------------------------------------------------------------------
    rows = g.query(q)

    results = []
    for r in rows:
        # El resto de tu lógica de formato (que es correcta)
        results.append({
            "uri": str(r.facility),
            "name": str(r.name),
            "lat": _norm_coord(r.lat, "lat"),
            "long": _norm_coord(r.long, "lon"),
            "telephone": str(r.tel) if r.tel else None,
            "email": str(r.email) if r.email else None,
            "class": _pretty_class(r.classLocal),
            "neighbourhood": str(r.nhName) if r.nhName else None,
            "district": str(r.distName) if r.distName else None,
            "municipality": str(r.munName) if r.munName else None,
        })
    return results