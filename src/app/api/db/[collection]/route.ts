import { api } from "@/lib/auth";
import { q, q1 } from "@/lib/db";
import { readAccess } from "@/lib/rules";

export const dynamic = "force-dynamic";

// List a collection. Cheap change detection: clients send the ETag back and
// get a 304 unless something in the collection changed (used for live updates).
export const GET = api(async (req: Request, ctx: { params: Promise<{ collection: string }> }) => {
  const { collection } = await ctx.params;
  await readAccess(collection);

  const stamp = await q1<{ n: string; t: string | null }>(
    "select count(*)::text as n, coalesce(max(extract(epoch from updated_at))::text, '0') as t from docs where collection = $1",
    [collection]
  );
  const etag = `"${stamp!.n}-${stamp!.t}"`;
  if (req.headers.get("if-none-match") === etag) return new Response(null, { status: 304, headers: { ETag: etag } });

  const rows = await q<{ id: string; data: unknown; updated_at: string }>(
    "select id, data, updated_at from docs where collection = $1 order by id",
    [collection]
  );
  return Response.json(
    { docs: rows.map((r) => ({ id: r.id, data: r.data, updatedAt: r.updated_at })) },
    { headers: { ETag: etag, "Cache-Control": "private, no-cache" } }
  );
});
