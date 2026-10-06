import { api, HttpError, requireUser } from "@/lib/auth";
import { q, q1 } from "@/lib/db";

export const dynamic = "force-dynamic";

async function owned(id: string, userId: string, role: string) {
  if (!/^[0-9a-f-]{36}$/.test(id)) throw new HttpError(404, "No such link");
  const l = await q1<{ owner_id: string }>(
    "select d.owner_id from share_links l join decks d on d.id = l.deck_id where l.id = $1",
    [id]
  );
  if (!l || (role !== "creator" && l.owner_id !== userId)) throw new HttpError(404, "No such link");
}

// Revoke a share link: the address stops working immediately.
export const DELETE = api(async (_req: Request, ctx: { params: Promise<{ id: string }> }) => {
  const u = await requireUser();
  const { id } = await ctx.params;
  await owned(id, u.id, u.role);
  await q("update share_links set revoked_at = now() where id = $1 and revoked_at is null", [id]);
  return Response.json({ ok: true });
});

// Turn a revoked link back on.
export const PATCH = api(async (_req: Request, ctx: { params: Promise<{ id: string }> }) => {
  const u = await requireUser();
  const { id } = await ctx.params;
  await owned(id, u.id, u.role);
  await q("update share_links set revoked_at = null where id = $1", [id]);
  return Response.json({ ok: true });
});
