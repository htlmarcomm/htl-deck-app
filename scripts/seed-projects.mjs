// Loads db/projects_seed.json into the shared project register (100 rows per
// document, same layout the Project database screen reads). Re-running
// replaces the register with the file's contents.
import fs from "node:fs";
import path from "node:path";
import pg from "pg";
import { loadEnv } from "./env.mjs";

loadEnv();
const url = process.env.DIRECT_URL || process.env.DATABASE_URL;
if (!url) { console.error("Set DATABASE_URL first - see .env.example."); process.exit(1); }
const rows = JSON.parse(fs.readFileSync(path.join(process.cwd(), "db", "projects_seed.json"), "utf8"));

const client = new pg.Client({ connectionString: url });
await client.connect();
try {
  await client.query("begin");
  await client.query("delete from docs where collection = 'projects'");
  for (let i = 0; i < rows.length; i += 100) {
    const id = "c" + String(i / 100 + 1).padStart(3, "0");
    await client.query("insert into docs (collection, id, data) values ('projects', $1, $2)", [id, JSON.stringify({ rows: rows.slice(i, i + 100) })]);
  }
  await client.query("commit");
  console.log(`Loaded ${rows.length} projects.`);
} catch (e) {
  await client.query("rollback");
  throw e;
} finally {
  await client.end();
}
