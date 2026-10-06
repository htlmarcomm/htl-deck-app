import { api, hashPassword, HttpError, requireCreator } from "@/lib/auth";
import { q, q1 } from "@/lib/db";

export const dynamic = "force-dynamic";

// Creator edits an account: reset password, change role, deactivate/reactivate.
export const PATCH = api(async (req: Request, ctx: { params: Promise<{ id: string }> }) => {
  const me = await requireCreator();
  const { id } = await ctx.params;
  const b = await req.json().catch(() => ({}));
  const target = await q1<{ id: string; role: string; active: boolean }>("select id, role, active from users where id = $1", [id]);
  if (!target) throw new HttpError(404, "No such user");

  const sets: string[] = [];
  const vals: unknown[] = [];
  if (typeof b.password === "string") {
    if (b.password.length < 10) throw new HttpError(400, "Password must be at least 10 characters");
    vals.push(await hashPassword(b.password)); sets.push(`password_hash = $${vals.length}`);
  }
  if (b.role === "creator" || b.role === "user") { vals.push(b.role); sets.push(`role = $${vals.length}`); }
  if (typeof b.active === "boolean") { vals.push(b.active); sets.push(`active = $${vals.length}`); }
  if (typeof b.name === "string" && b.name.trim()) { vals.push(b.name.trim()); sets.push(`name = $${vals.length}`); }
  if (!sets.length) throw new HttpError(400, "Nothing to change");

  // never lock the last Creator out
  const losingCreator = target.role === "creator" && (b.role === "user" || b.active === false);
  if (losingCreator) {
    const n = await q1<{ n: string }>("select count(*)::text as n from users where role = 'creator' and active and id <> $1", [id]);
    if (Number(n!.n) === 0) throw new HttpError(400, "There must be at least one active Creator");
  }
  if (id === me.id && b.active === false) throw new HttpError(400, "You can't deactivate your own account");

  vals.push(id);
  const u = await q1(`update users set ${sets.join(", ")} where id = $${vals.length} returning id, username, name, role, active`, vals);
  return Response.json({ user: u });
});
