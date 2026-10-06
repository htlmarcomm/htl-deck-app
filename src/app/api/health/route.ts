import { pool } from "@/lib/db";

export const dynamic = "force-dynamic";

// Setup check: shows which piece is missing, never any secret values.
export async function GET() {
  const out: Record<string, unknown> = {
    DATABASE_URL_set: !!process.env.DATABASE_URL,
    AUTH_SECRET_set: !!process.env.AUTH_SECRET && process.env.AUTH_SECRET.length >= 16,
  };
  if (!process.env.DATABASE_URL) {
    out.next = "Add DATABASE_URL in Vercel > Settings > Environment Variables, then redeploy.";
    return Response.json(out, { status: 503 });
  }
  try {
    await pool().query("select 1");
    out.database = "connected";
  } catch (e: any) {
    out.database = "cannot connect";
    out.error_code = e?.code ?? null;
    out.next = "DATABASE_URL looks wrong or Neon is unreachable. Re-copy the pooled string from Neon.";
    return Response.json(out, { status: 503 });
  }
  try {
    const r = await pool().query("select count(*)::int as n from users where role = 'creator' and active");
    out.tables = "ok";
    out.active_creators = r.rows[0].n;
    out.next = r.rows[0].n ? "All set - you can sign in." : "Tables exist but there is no Creator yet: run `npm run seed` on your PC.";
  } catch (e: any) {
    out.tables = "missing";
    out.error_code = e?.code ?? null;
    out.next = "Run `npm run migrate` then `npm run seed` on your PC (with .env.local pointing at Neon).";
    return Response.json(out, { status: 503 });
  }
  return Response.json(out);
}
