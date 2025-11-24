const DEFAULT_RADIUS_METERS = 200;
const DEFAULT_ORIGIN_WKT = "POINT(-3.7038 40.4168)";

const PREFIXES = `
PREFIX schema: <https://schema.org/>
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX safeschool: <http://safeschool.linkeddata.es/ontology#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
PREFIX uom: <http://www.opengis.net/def/uom/OGC/1.0/>
`;

const sanitizeWktLiteral = (value = DEFAULT_ORIGIN_WKT) => {
  if (!value || typeof value !== "string") {
    return DEFAULT_ORIGIN_WKT;
  }
  return value.replace(/"/g, '\\"');
};

export const buildSchoolsQuery = () => `${PREFIXES}
SELECT ?code ?name ?address ?postalCode ?districtName ?districtCode ?typeDescription ?typeCode
       ?ownership ?email ?phone ?website ?wkt
WHERE {
  ?school a safeschool:EducationalCenter ;
          schema:identifier ?code ;
          schema:name ?name ;
          safeschool:wktGeometry ?wkt .
  OPTIONAL { ?school schema:streetAddress ?address }
  OPTIONAL { ?school schema:postalCode ?postalCode }
  OPTIONAL {
    ?school safeschool:inDistrict ?district .
    OPTIONAL { ?district schema:name ?districtName }
    OPTIONAL { ?district schema:identifier ?districtCode }
  }
  OPTIONAL { ?school schema:description ?typeDescription }
  OPTIONAL { ?school safeschool:centerTypeCode ?typeCode }
  OPTIONAL { ?school safeschool:ownershipType ?ownership }
  OPTIONAL { ?school schema:email ?email }
  OPTIONAL { ?school schema:telephone ?phone }
  OPTIONAL { ?school schema:url ?website }
}`;

export const buildAccidentsQuery = ({ radius, originWkt } = {}) => {
  const normalizedRadius =
    Number.isFinite(radius) && radius > 0 ? radius : DEFAULT_RADIUS_METERS;
  const normalizedOrigin =
    originWkt && originWkt.trim().length > 0 ? originWkt.trim() : DEFAULT_ORIGIN_WKT;
  const sanitizedOrigin = sanitizeWktLiteral(normalizedOrigin);

  return `${PREFIXES}
SELECT ?numExpediente ?wkt ?lesividad ?nivelLesividad ?distrito ?codDistrito ?startDate ?localizacion
       ?weather ?peatonInvolucrado ?positivaAlcohol ?positivaDroga ?tipoAccidente ?vehiculos
WHERE {
  ?accident a safeschool:Accident ;
            schema:identifier ?numExpediente ;
            safeschool:wktGeometry ?wkt .
  OPTIONAL { ?accident safeschool:injuryDescription ?lesividad }
  OPTIONAL { ?accident safeschool:injuryLevel ?nivelLesividad }
  OPTIONAL {
    ?accident safeschool:inDistrict ?district .
    OPTIONAL { ?district schema:name ?distrito }
    OPTIONAL { ?district schema:identifier ?codDistrito }
  }
  OPTIONAL { ?accident schema:startDate ?startDate }
  OPTIONAL { ?accident schema:description ?localizacion }
  OPTIONAL { ?accident safeschool:weatherCondition ?weather }
  OPTIONAL { ?accident safeschool:pedestrianInvolved ?peatonInvolucrado }
  OPTIONAL { ?accident safeschool:alcoholPositive ?positivaAlcohol }
  OPTIONAL { ?accident safeschool:drugPositive ?positivaDroga }
  OPTIONAL { ?accident schema:name ?tipoAccidente }
  OPTIONAL { ?accident safeschool:vehiclesInvolved ?vehiculos }
  BIND(${normalizedRadius} AS ?radiusMeters)
  BIND("${sanitizedOrigin}"^^geo:wktLiteral AS ?originPoint)
  FILTER(geof:distance(?wkt, ?originPoint, uom:metre) <= ?radiusMeters)
}`;
};

export const buildRadarsQuery = () => `${PREFIXES}
SELECT ?numero ?ubicacion ?wkt ?velocidadLimite ?tipo
WHERE {
  ?radar a safeschool:SpeedCamera ;
         schema:identifier ?numero ;
         safeschool:wktGeometry ?wkt .
  OPTIONAL { ?radar schema:description ?ubicacion }
  OPTIONAL { ?radar safeschool:speedLimit ?velocidadLimite }
  OPTIONAL { ?radar safeschool:cameraType ?tipo }
}`;

const asString = (binding, key) => binding?.[key]?.value ?? null;
const asNumber = (binding, key) => {
  const value = binding?.[key]?.value;
  if (value === undefined || value === null) return null;
  const parsed = Number(value);
  return Number.isNaN(parsed) ? null : parsed;
};
const asBoolean = (binding, key) => {
  const value = binding?.[key]?.value;
  if (value === undefined || value === null) return null;
  return value === "true" || value === "1";
};

const splitDateTime = (value) => {
  if (!value) {
    return { fecha: "", hora: "" };
  }
  const [date = "", rest = ""] = value.split("T");
  const time = rest.replace(/([+-].*|Z)$/i, "");
  return { fecha: date, hora: time };
};

export const mapSchoolResults = (bindings = []) =>
  bindings.map((binding) => ({
    centro_codigo: asNumber(binding, "code") ?? 0,
    centro_nombre: asString(binding, "name") ?? "",
    direccion: asString(binding, "address") ?? "",
    direccion_codigo_postal: asNumber(binding, "postalCode"),
    distrito_nombre: asString(binding, "districtName") ?? "",
    distrito_codigo: asNumber(binding, "districtCode"),
    centro_tipo_descripcion: asString(binding, "typeDescription") ?? "",
    centro_tipo_codigo: asNumber(binding, "typeCode"),
    centro_titularidad: asString(binding, "ownership"),
    contacto_email1: asString(binding, "email"),
    contacto_telefono1: asNumber(binding, "phone"),
    contacto_web: asString(binding, "website"),
    wktGeometry: asString(binding, "wkt") ?? "",
  }));

export const mapAccidentResults = (bindings = []) =>
  bindings.map((binding) => ({
    num_expediente: asString(binding, "numExpediente") ?? "",
    wktGeometry: asString(binding, "wkt") ?? "",
    lesividad: asString(binding, "lesividad") ?? "",
    nivel_lesividad: asNumber(binding, "nivelLesividad") ?? 0,
    distrito: asString(binding, "distrito") ?? "",
    ...splitDateTime(asString(binding, "startDate")),
    localizacion: asString(binding, "localizacion") ?? "",
    cod_distrito: asNumber(binding, "codDistrito"),
    estado_meteorológico: asString(binding, "weather"),
    peaton_involucrado: asBoolean(binding, "peatonInvolucrado"),
    positiva_alcohol: asBoolean(binding, "positivaAlcohol"),
    positiva_droga: asBoolean(binding, "positivaDroga"),
    tipo_accidente: asString(binding, "tipoAccidente"),
    vehiculos_involucrados: asString(binding, "vehiculos"),
  }));

export const mapRadarResults = (bindings = []) =>
  bindings.map((binding) => ({
    numero_radar: asNumber(binding, "numero") ?? 0,
    ubicacion: asString(binding, "ubicacion") ?? "",
    wktGeometry: asString(binding, "wkt") ?? "",
    velocidad_limite: asNumber(binding, "velocidadLimite") ?? 0,
    tipo: asString(binding, "tipo") ?? "",
  }));
