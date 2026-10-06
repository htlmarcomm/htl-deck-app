import { api, hashPassword, HttpError, requireCreator } from "@/lib/auth";
import { q, q1 } from "@/lib/db";

export const dynamic = "force-dynamic";

export const GET = api(async () => {
  await requireCreator();
  const rows = await q("select id, username, name, role, active, created_at from users order by created_at");
  return Response.json({ users: rows });
});

export const POST = api(async (req: Request) => {
  await requireCreator();
  const b = await req.json().catch(() => ({}));
  const username = String(b.username ?? "").trim().toLowerCase();
  const name = String(b.name ?? "").trim();
  const password = String(b.password ?? "");
  const role = b.role === "creator" ? "creator" : "user";
  if (!/^[a-z0-9._-]{3,40}$/.test(username)) throw new HttpError(400, "Username: 3-40 letters, numbers, . _ -");
  if (!name) throw new HttpError(400, "Enter a name");
  if (password.length < 10) throw new HttpError(400, "Password must be at least 10 characters");
  if (await q1("select 1 from users where username = $1", [username])) throw new HttpError(409, "That username is taken");
  const u = await q1(
    "insert into users (username, name, password_hash, role) values ($1, $2, $3, $4) returning id, username, name, role, active",
    [username, name, await hashPassword(password), role]
  );
  return Response.json({ user: u }, { status: 201 });
});
