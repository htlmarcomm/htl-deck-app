// Creates the first Creator login (or resets its password if the username exists).
//   SEED_CREATOR_USERNAME / SEED_CREATOR_NAME / SEED_CREATOR_PASSWORD
import bcrypt from "bcryptjs";
import pg from "pg";
import { loadEnv } from "./env.mjs";

loadEnv();
const url = process.env.DIRECT_URL || process.env.DATABASE_URL;
const username = (process.env.SEED_CREATOR_USERNAME || "creator").trim().toLowerCase();
const name = process.env.SEED_CREATOR_NAME || "HTL Creator";
const password = process.env.SEED_CREATOR_PASSWORD || "";
if (!url) { console.error("Set DATABASE_URL first - see .env.example."); process.exit(1); }
if (password.length < 10) { console.error("Set SEED_CREATOR_PASSWORD (at least 10 characters)."); process.exit(1); }

const client = new pg.Client({ connectionString: url });
await client.connect();
try {
  const hash = await bcrypt.hash(password, 12);
  const r = await client.query(
    `insert into users (username, name, password_hash, role)
     values ($1, $2, $3, 'creator')
     on conflict (username) do update set password_hash = excluded.password_hash, name = excluded.name, role = 'creator', active = true
     returning id`,
    [username, name, hash]
  );
  console.log(`Creator "${username}" is ready (id ${r.rows[0].id}).`);
} finally {
  await client.end();
}
