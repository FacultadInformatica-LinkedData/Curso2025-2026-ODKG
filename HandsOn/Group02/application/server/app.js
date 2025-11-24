import express from "express";
import cors from "cors";
import { createProxyMiddleware } from "http-proxy-middleware";
import {
  runSelectQuery as defaultRunSelectQuery,
  GRAPHDB_URL,
  GRAPHDB_REPOSITORY,
} from "./graphdb.js";
import {
  buildSchoolsQuery,
  buildAccidentsQuery,
  buildRadarsQuery,
  mapSchoolResults,
  mapAccidentResults,
  mapRadarResults,
} from "./queries.js";
import { createQueryCache } from "./cache.js";

const DEFAULT_PROXY_PATH = process.env.GRAPHDB_PROXY_PATH ?? "/graphdb";
const DEFAULT_CACHE_TTL = Number.isFinite(Number(process.env.GRAPHDB_CACHE_TTL_MS))
  ? Number(process.env.GRAPHDB_CACHE_TTL_MS)
  : 5 * 60 * 1000;

function escapeForRegex(value) {
  return value.replace(/[-/\\^$*+?.()|[\]{}]/g, "\\$&");
}

function parseRadiusParam(value) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed) || parsed <= 0) {
    return undefined;
  }
  return parsed;
}

async function executeQuery(
  res,
  queryBuilder,
  mapper,
  runSelect,
  logger,
  cache
) {
  try {
    const query = queryBuilder();
    const cached = cache?.get?.(query);
    if (cached) {
      res.json(cached);
      return;
    }
    const response = await runSelect(query);
    const bindings = response?.results?.bindings ?? [];
    const payload = mapper(bindings);
    cache?.set?.(query, payload);
    res.json(payload);
  } catch (error) {
    logger?.error?.("GraphDB query failed", error);
    res.status(502).json({ message: "Unable to retrieve data from GraphDB" });
  }
}

export function createApp(options = {}) {
  const {
    runSelectQuery = defaultRunSelectQuery,
    graphdbUrl = GRAPHDB_URL,
    graphdbRepository = GRAPHDB_REPOSITORY,
    graphdbProxyPath = DEFAULT_PROXY_PATH,
    enableGraphdbProxy = true,
    logger = console,
    cacheTtlMs = DEFAULT_CACHE_TTL,
  } = options;

  const app = express();
  app.use(cors());
  app.use(express.json());

  const cache = createQueryCache(cacheTtlMs);

  app.get("/api/health", (_req, res) => {
    res.json({ status: "ok" });
  });

  app.get("/api/schools", (_req, res) =>
    executeQuery(
      res,
      buildSchoolsQuery,
      mapSchoolResults,
      runSelectQuery,
      logger,
      cache
    )
  );
  app.get("/api/accidents", (req, res) => {
    const radius = parseRadiusParam(req?.query?.radius);
    const originWkt =
      typeof req?.query?.origin === "string" && req.query.origin.trim().length > 0
        ? req.query.origin.trim()
        : undefined;

    return executeQuery(
      res,
      () => buildAccidentsQuery({ radius, originWkt }),
      mapAccidentResults,
      runSelectQuery,
      logger,
      cache
    );
  });
  app.get("/api/radar", (_req, res) =>
    executeQuery(
      res,
      buildRadarsQuery,
      mapRadarResults,
      runSelectQuery,
      logger,
      cache
    )
  );

  if (enableGraphdbProxy) {
    app.use(
      graphdbProxyPath,
      createProxyMiddleware({
        target: graphdbUrl,
        changeOrigin: true,
        pathRewrite: (path) => {
          const pattern = new RegExp(`^${escapeForRegex(graphdbProxyPath)}`);
          return path.replace(pattern, `/repositories/${graphdbRepository}`);
        },
        logLevel: "warn",
      })
    );
  }

  return app;
}
