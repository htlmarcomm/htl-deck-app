import { cookies } from "next/headers";
import { api, checkPassword, SESSION_COOKIE, sessionCookieOptions, signSession } from "@/lib/auth";
import { q1 } from "@/lib/db";

// Best-effort brute-force brake (per server instance): 8 failures per
// username+IP per 10 minutes.
const fails = new Map<string, { n: number; t: number }>();
const WINDOW = 10 * 60_000;
const DUMMY = "$2a$12$C6UzMDM.H6dfI/f/IKcEeO5G5e7p3ZJ6y0q2k7k7Qm4m4m4m4m4m4";

export const POST = api(async (req: Request) => {
  const body = await req.json().catch(() => ({}));
  const username = String(body.username ?? "").trim().toLowerCase();
  const password = String(body.password ?? "");
  if (!username || !password) return Response.json({ error: "Enter your username and password." }, { status: 400 });

  const ip = req.headers.get("x-forwarded-for")?.split(",")[0]?.trim() ?? "?";
  const key = `${username}|${ip}`;
  const f = fails.get(key);
  if (f && Date.now() - f.t < WINDOW && f.n >= 8) {
    return Response.json({ error: "Too many attempts. Try again in a few minutes." }, { status: 429 });
  }

  const u = await q1<{ id: string; password_hash: string; active: boolean }>(
    "select id, password_hash, active from users where username = $1",
    [username]
  );
  const ok = await checkPassword(password, u?.password_hash ?? DUMMY);
  if (!u || !u.active || !ok) {
    fails.set(key, { n: (f && Date.now() - f.t < WINDOW ? f.n : 0) + 1, t: Date.now() });
    return Response.json({ error: "Wrong username or password." }, { status: 401 });
  }
  fails.delete(key);

  const jar = await cookies();
  jar.set(SESSION_COOKIE, await signSession(u.id), sessionCookieOptions());
  return Response.json({ ok: true });
});
