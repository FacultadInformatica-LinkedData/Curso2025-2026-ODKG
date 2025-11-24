# SafeSchool Madrid

School safety zone analysis for Madrid combining traffic accidents, educational centers, and speed camera infrastructure.

## Purpose and Scope

The SafeSchool system integrates Madrid traffic accident data, educational center locations, and speed camera infrastructure to enable school safety zone analysis.

## System Overview

The SafeSchool system addresses the question: "Which schools in Madrid are located in areas with high accident rates, and how can traffic enforcement infrastructure be correlated with school safety?"

The system integrates three data sources from Madrid open data portals:

## Data Sources

| Data Source         | Entity Type         | Records        | Key Attributes                                               |
| ------------------- | ------------------- | -------------- | ------------------------------------------------------------ |
| Accidentalidad 2025 | Traffic Accidents   | ~150 accidents | Location, date/time, injury level, vehicle types, substances |
| Centros Educativos  | Educational Centers | ~2,800 schools | Name, type, address, district, contact info                  |
| Radares Fijos       | Speed Cameras       | 37 cameras     | Location, speed limit, camera type, roadway                  |

Sources: Madrid open data portals; OpenStreetMap tiles for basemaps.

## Tech Stack

- Vite + React + TypeScript
- Tailwind CSS + shadcn/ui (Radix UI)
- Leaflet for mapping
- Express REST API + GraphDB (SPARQL) for the data backend
- TanStack Query for data fetching/caching

## Getting Started

### Prerequisites
- Node.js (v18+ recommended) and npm

### Installation
```bash
git clone <YOUR_GIT_URL>
cd safeschool-madrid
npm install
```

### Development
```bash
# Terminal 1 - start the Express API (defaults to port 4000)
npm run server

# Terminal 2 - start the Vite dev server (proxies /api to port 4000)
npm run dev
```
Then open http://localhost:8080

### Production build
```bash
npm run build
npm run preview
```

### Verifying the backend

You can confirm that the Express API is wired correctly in two ways:

1. Run the automated backend tests (they mock GraphDB responses and assert the REST payloads).

```bash
npm run test:server
```

2. With GraphDB running and `npm run server` already started, hit one of the endpoints directly:

```bash
curl http://localhost:4000/api/schools | head
```

If the response is an empty array, double-check that the RDF repository contains `safeschool:EducationalCenter`, `safeschool:Accident`, and `safeschool:SpeedCamera` resources with `safeschool:wktGeometry` literals and that the `GRAPHDB_*` environment variables point to the right instance.

### Linting
```bash
npm run lint
```

## Available Scripts

- dev: Start the Vite dev server
- server: Start the Express API + GraphDB proxy
- build: Build for production
- build:dev: Build in development mode
- preview: Preview the production build
- lint: Run ESLint
- test:server: Run the backend unit tests (Node.js test runner + SuperTest)

## Project Structure

```bash
.
├─ public/                # Static assets
├─ server/                # GraphDB helpers and SPARQL queries
├─ server.js              # Express backend + proxy to GraphDB
├─ src/
│  ├─ components/         # UI components (tables, map, header, etc.)
│  ├─ contexts/           # Global state (filters)
│  ├─ hooks/              # Data hooks (accidents, schools, radar)
│  ├─ lib/                # Utilities (geo parsing, REST client)
│  ├─ pages/              # Routes
│  ├─ types/              # Shared TypeScript types
│  ├─ main.tsx            # App bootstrap
│  └─ App.tsx             # App shell
└─ vite.config.ts
```

## Data Management

Data is queried directly from GraphDB using SPARQL. The Express backend (`server.js`) exposes REST endpoints:
- `GET /api/accidents` → retrieves `safeschool:Accident` resources (case number, date/time, injury metrics, district, weather, etc.)
- `GET /api/schools` → retrieves `safeschool:EducationalCenter` resources (identifier, district, address, contact info)
- `GET /api/radar` → retrieves `safeschool:SpeedCamera` resources (identifier, roadway description, camera type, speed limit)

Each handler converts SPARQL bindings into the shape expected by the frontend. Geometry is retrieved from the `safeschool:wktGeometry` literal on every resource and rendered via Leaflet.

### Quick SPARQL sanity checks

If you want to confirm that the ontology backing GraphDB matches what the API expects, run one of these snippets inside GraphDB's SPARQL console (adjust the repository dropdown first):

```sparql
PREFIX safeschool: <http://safeschool.linkeddata.es/ontology#>
PREFIX schema: <https://schema.org/>

# List school names and types
SELECT ?center ?name ?type
WHERE {
  ?center a safeschool:EducationalCenter ;
          schema:name ?name ;
          schema:description ?type .
}
LIMIT 10
```

```sparql
PREFIX safeschool: <http://safeschool.linkeddata.es/ontology#>
PREFIX schema: <https://schema.org/>

# Accidents that happened near pedestrians
SELECT ?accident ?location ?date ?weather
WHERE {
  ?accident a safeschool:Accident ;
            schema:description ?location ;
            schema:startDate ?date ;
            safeschool:weatherCondition ?weather ;
            safeschool:pedestrianInvolved true .
}
LIMIT 10
```

```sparql
PREFIX safeschool: <http://safeschool.linkeddata.es/ontology#>
PREFIX schema: <https://schema.org/>

# Speed cameras with their speed limits
SELECT ?camera ?location ?type ?speedLimit
WHERE {
  ?camera a safeschool:SpeedCamera ;
          schema:description ?location ;
          safeschool:cameraType ?type ;
          safeschool:speedLimit ?speedLimit .
}
LIMIT 10
```

Seeing data in these queries ensures the ontology matches the API contracts; otherwise, update your ETL or repository before debugging the frontend.

## Environment and Configuration

The Express backend can be configured with the following environment variables:

| Variable | Description | Default |
| --- | --- | --- |
| `GRAPHDB_URL` | Base URL for the GraphDB instance | `http://localhost:7200` |
| `GRAPHDB_REPOSITORY` | Repository to query | `safeschool` |
| `PORT` | Express server port | `4000` |
| `GRAPHDB_PROXY_PATH` | Path exposed by the proxy middleware | `/graphdb` |
| `GRAPHDB_CACHE_TTL_MS` | Milliseconds to cache successful GraphDB responses in memory | `300000` |
| `VITE_API_BASE_URL` | (Frontend) override for the REST base path | `/api` |

## Acknowledgments

- Madrid Open Data portals for datasets
- OpenStreetMap contributors for basemap tiles
- GraphDB community for the RDF database engine
