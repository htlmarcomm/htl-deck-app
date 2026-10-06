// Applies db/migrations/*.sql in order, once each. Safe to re-run.
// Uses DIRECT_URL (falls back to DATABASE_URL): migrations should not go
// through the pooled connection.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import pg from "pg";
import { loadEnv } from "./env.mjs";

loadEnv();
const url = process.env.DIRECT_URL || process.env.DATABASE_URL;
if (!url) {
  console.error("Set DATABASE_URL (and ideally DIRECT_URL) first - see .env.example.");
  process.exit(1);
}

const dir = path.join(path.dirname(fileURLToPath(import.meta.url)), "..", "db", "migrations");
const files = fs.readdirSync(dir).filter((f) => f.endsWith(".sql")).sort();

const client = new pg.Client({ connectionString: url });
await client.connect();
try {
  await client.query(
    "create table if not exists schema_migrations (name text primary key, applied_at timestamptz not null default now())"
  );
  const done = new Set((await client.query("select name from schema_migrations")).rows.map((r) => r.name));
  for (const f of files) {
    if (done.has(f)) continue;
    console.log("applying", f);
    await client.query("begin");
    try {
      await client.query(fs.readFileSync(path.join(dir, f), "utf8"));
      await client.query("insert into schema_migrations (name) values ($1)", [f]);
      await client.query("commit");
    } catch (e) {
      await client.query("rollback");
      throw e;
    }
  }
  console.log("database is up to date");
} finally {
  await client.end();
}
