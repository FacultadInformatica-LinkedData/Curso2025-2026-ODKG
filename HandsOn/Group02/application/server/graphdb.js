const GRAPHDB_URL = process.env.GRAPHDB_URL ?? "http://localhost:7200";
const GRAPHDB_REPOSITORY = process.env.GRAPHDB_REPOSITORY ?? "safeschool";
const GRAPHDB_ENDPOINT = `${GRAPHDB_URL.replace(/\/$/, "")}/repositories/${GRAPHDB_REPOSITORY}`;

/**
 * Executes a SPARQL query against GraphDB and returns the JSON bindings.
 * @param {string} query
 */
export async function runSelectQuery(query) {
  const response = await fetch(GRAPHDB_ENDPOINT, {
    method: "POST",
    headers: {
      "Content-Type": "application/sparql-query",
      Accept: "application/sparql-results+json",
    },
    body: query,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`GraphDB request failed with ${response.status}: ${errorText}`);
  }

  return response.json();
}

export { GRAPHDB_URL, GRAPHDB_REPOSITORY, GRAPHDB_ENDPOINT };
