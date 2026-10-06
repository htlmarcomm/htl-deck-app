import { api, HttpError } from "@/lib/auth";
import { q, q1 } from "@/lib/db";
import { assertId, readAccess, writeAccess } from "@/lib/rules";

export const dynamic = "force-dynamic";
type Ctx = { params: Promise<{ collection: string; id: string }> };

export const GET = api(async (_req: Request, ctx: Ctx) => {
  const { collection, id } = await ctx.params;
  await readAccess(collection);
  assertId(id);
  const r = await q1<{ data: unknown }>("select data from docs where collection = $1 and id = $2", [collection, id]);
  if (!r) throw new HttpError(404, "Not found");
  return Response.json({ id, data: r.data });
});

export const PUT = api(async (req: Request, ctx: Ctx) => {
  const { collection, id } = await ctx.params;
  const user = await writeAccess(collection);
  assertId(id);
  const body = await req.json().catch(() => null);
  if (!body || typeof body !== "object" || Array.isArray(body)) throw new HttpError(400, "Body must be a JSON object");
  await q(
    `insert into docs (collection, id, data, updated_by) values ($1, $2, $3, $4)
     on conflict (collection, id) do update set data = excluded.data, updated_at = now(), updated_by = excluded.updated_by`,
    [collection, id, JSON.stringify(body), user.id]
  );
  return Response.json({ ok: true });
});

export const DELETE = api(async (_req: Request, ctx: Ctx) => {
  const { collection, id } = await ctx.params;
  await writeAccess(collection);
  assertId(id);
  await q("delete from docs where collection = $1 and id = $2", [collection, id]);
  return Response.json({ ok: true });
});
