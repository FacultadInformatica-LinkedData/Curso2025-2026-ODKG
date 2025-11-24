import { createApp } from "./server/app.js";
import { GRAPHDB_URL, GRAPHDB_REPOSITORY } from "./server/graphdb.js";

const PORT = Number(process.env.PORT ?? 4000);

const app = createApp();

app.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}`);
  console.log(`GraphDB endpoint: ${GRAPHDB_URL}/repositories/${GRAPHDB_REPOSITORY}`);
});
