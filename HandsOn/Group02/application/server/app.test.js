import test from "node:test";
import assert from "node:assert/strict";
import { setTimeout as delay } from "node:timers/promises";
import request from "supertest";
import { createApp } from "./app.js";

const mockBindings = {
  results: {
    bindings: [
      {
        code: { value: "1001" },
        name: { value: "Colegio Uno" },
        address: { value: "Calle Uno" },
        postalCode: { value: "28001" },
        districtName: { value: "Centro" },
        districtCode: { value: "1" },
        typeDescription: { value: "Public" },
        typeCode: { value: "1" },
        ownership: { value: "Ayuntamiento" },
        email: { value: "info@example.com" },
        phone: { value: "910000000" },
        website: { value: "https://example.com" },
        wkt: { value: "POINT(-3.7 40.4)" },
      },
    ],
  },
};

const silentLogger = { error: () => {} };

function createRecordingRunSelect(response = mockBindings) {
  const queries = [];
  const runSelectQuery = async (query) => {
    queries.push(query);
    if (response instanceof Error) {
      throw response;
    }
    return response;
  };
  return { runSelectQuery, queries };
}

test("/api/schools maps SPARQL bindings", async () => {
  const { runSelectQuery, queries } = createRecordingRunSelect();
  const app = createApp({
    runSelectQuery,
    enableGraphdbProxy: false,
    logger: silentLogger,
  });

  const res = await request(app).get("/api/schools");

  assert.equal(res.status, 200);
  assert.equal(queries.length, 1);
  assert.ok(queries[0].includes("safeschool:EducationalCenter"));
  assert.deepEqual(res.body, [
    {
      centro_codigo: 1001,
      centro_nombre: "Colegio Uno",
      direccion: "Calle Uno",
      direccion_codigo_postal: 28001,
      distrito_nombre: "Centro",
      distrito_codigo: 1,
      centro_tipo_descripcion: "Public",
      centro_tipo_codigo: 1,
      centro_titularidad: "Ayuntamiento",
      contacto_email1: "info@example.com",
      contacto_telefono1: 910000000,
      contacto_web: "https://example.com",
      wktGeometry: "POINT(-3.7 40.4)",
    },
  ]);
});

test("/api/accidents maps SPARQL bindings", async () => {
  const accidentResponse = {
    results: {
      bindings: [
        {
          numExpediente: { value: "EXP-1" },
          wkt: { value: "POINT(-3.68 40.41)" },
          lesividad: { value: "Leve" },
          nivelLesividad: { value: "2" },
          distrito: { value: "Salamanca" },
          startDate: { value: "2024-04-10T10:00:00+01:00" },
          localizacion: { value: "Calle Dos" },
          codDistrito: { value: "2" },
          weather: { value: "Nublado" },
          peatonInvolucrado: { value: "true" },
          positivaAlcohol: { value: "false" },
          positivaDroga: { value: "1" },
          tipoAccidente: { value: "Alcance" },
          vehiculos: { value: "Turismo" },
        },
      ],
    },
  };

  const { runSelectQuery, queries } = createRecordingRunSelect(accidentResponse);
  const app = createApp({
    runSelectQuery,
    enableGraphdbProxy: false,
    logger: silentLogger,
  });

  const res = await request(app).get("/api/accidents");

  assert.equal(res.status, 200);
  assert.ok(queries[0].includes("safeschool:Accident"));
  assert.deepEqual(res.body, [
    {
      num_expediente: "EXP-1",
      wktGeometry: "POINT(-3.68 40.41)",
      lesividad: "Leve",
      nivel_lesividad: 2,
      distrito: "Salamanca",
      fecha: "2024-04-10",
      hora: "10:00:00",
      localizacion: "Calle Dos",
      cod_distrito: 2,
      estado_meteorológico: "Nublado",
      peaton_involucrado: true,
      positiva_alcohol: false,
      positiva_droga: true,
      tipo_accidente: "Alcance",
      vehiculos_involucrados: "Turismo",
    },
  ]);
});

test("/api/radar maps SPARQL bindings", async () => {
  const radarResponse = {
    results: {
      bindings: [
        {
          numero: { value: "5" },
          ubicacion: { value: "M-30" },
          wkt: { value: "POINT(-3.69 40.42)" },
          velocidadLimite: { value: "80" },
          tipo: { value: "Fijo" },
        },
      ],
    },
  };

  const { runSelectQuery, queries } = createRecordingRunSelect(radarResponse);
  const app = createApp({
    runSelectQuery,
    enableGraphdbProxy: false,
    logger: silentLogger,
  });

  const res = await request(app).get("/api/radar");

  assert.equal(res.status, 200);
  assert.ok(queries[0].includes("safeschool:SpeedCamera"));
  assert.deepEqual(res.body, [
    {
      numero_radar: 5,
      ubicacion: "M-30",
      wktGeometry: "POINT(-3.69 40.42)",
      velocidad_limite: 80,
      tipo: "Fijo",
    },
  ]);
});

test("failed GraphDB calls return 502", async () => {
  const failingRunSelect = async () => {
    throw new Error("Graph down");
  };

  const app = createApp({
    runSelectQuery: failingRunSelect,
    enableGraphdbProxy: false,
    logger: silentLogger,
  });

  const res = await request(app).get("/api/schools");

  assert.equal(res.status, 502);
  assert.deepEqual(res.body, { message: "Unable to retrieve data from GraphDB" });
});

test("responses are cached for the configured TTL", async () => {
  const { runSelectQuery, queries } = createRecordingRunSelect();
  const app = createApp({
    runSelectQuery,
    enableGraphdbProxy: false,
    logger: silentLogger,
    cacheTtlMs: 1000,
  });

  const first = await request(app).get("/api/schools");
  const second = await request(app).get("/api/schools");

  assert.equal(first.status, 200);
  assert.equal(second.status, 200);
  assert.equal(queries.length, 1);
});

test("cache expires once TTL elapses", async () => {
  const { runSelectQuery, queries } = createRecordingRunSelect();
  const app = createApp({
    runSelectQuery,
    enableGraphdbProxy: false,
    logger: silentLogger,
    cacheTtlMs: 10,
  });

  await request(app).get("/api/schools");
  await delay(15);
  await request(app).get("/api/schools");

  assert.equal(queries.length, 2);
});
