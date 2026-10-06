// Local Postgres for development/testing - no install, no accounts.
// Starts an embedded PostgreSQL in ./.local-db and keeps running until Ctrl+C.
// Prints the DATABASE_URL to use. (Production uses Neon instead.)
import fs from "node:fs";
import path from "node:path";
import EmbeddedPostgres from "embedded-postgres";

const dir = path.join(process.cwd(), ".local-db");
const port = Number(process.env.LOCAL_DB_PORT || 54329);
const fresh = !fs.existsSync(path.join(dir, "PG_VERSION"));

const pgInstance = new EmbeddedPostgres({
  databaseDir: dir,
  user: "htl",
  password: "htl-local",
  port,
  persistent: true,
});
if (fresh) await pgInstance.initialise();
await pgInstance.start();
if (fresh) await pgInstance.createDatabase("htl");

const url = `postgresql://htl:htl-local@localhost:${port}/htl`;
console.log("Local database is running.");
console.log("DATABASE_URL=" + url);
console.log("Press Ctrl+C to stop.");

const stop = async () => { await pgInstance.stop(); process.exit(0); };
process.on("SIGINT", stop);
process.on("SIGTERM", stop);
setInterval(() => {}, 1 << 30);
