import { Pool } from "pg";

// One pool per server instance. On Vercel/Neon use the POOLED connection
// string (DATABASE_URL) and keep the pool small: every serverless instance
// holds its own.
const g = globalThis as unknown as { __htlPool?: Pool };

function makePool(): Pool {
  const url = process.env.DATABASE_URL;
  if (!url) throw new Error("DATABASE_URL is not set");
  return new Pool({ connectionString: url, max: 5, idleTimeoutMillis: 10_000 });
}

export function pool(): Pool {
  return (g.__htlPool ??= makePool());
}

export async function q<T = any>(text: string, params: unknown[] = []): Promise<T[]> {
  const r = await pool().query(text, params);
  return r.rows as T[];
}

export async function q1<T = any>(text: string, params: unknown[] = []): Promise<T | null> {
  return (await q<T>(text, params))[0] ?? null;
}
