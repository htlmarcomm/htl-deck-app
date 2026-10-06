import { api, requireUser } from "@/lib/auth";
import { q, q1 } from "@/lib/db";
import { cleanName, loadDeck } from "@/lib/decks";

export const dynamic = "force-dynamic";
type Ctx = { params: Promise<{ id: string }> };

export const GET = api(async (_req: Request, ctx: Ctx) => {
  const u = await requireUser();
  const { id } = await ctx.params;
  const d = await loadDeck(id, u);
  const versions = await q1<{ n: number }>("select count(*)::int as n from deck_versions where deck_id = $1", [id]);
  return Response.json({ deck: { ...d, versions: versions!.n } });
});

// Autosave + rename + archive. Only the fields sent are changed.
export const PUT = api(async (req: Request, ctx: Ctx) => {
  const u = await requireUser();
  const { id } = await ctx.params;
  const d = await loadDeck(id, u);
  const b = await req.json().catch(() => ({}));
  const sets: string[] = ["updated_at = now()"];
  const vals: unknown[] = [];
  if (b.name !== undefined) { vals.push(cleanName(b.name, d.name)); sets.push(`name = $${vals.length}`); }
  if (b.client_name !== undefined) { vals.push(b.client_name ? cleanName(b.client_name, "") : null); sets.push(`client_name = $${vals.length}`); }
  if (typeof b.archived === "boolean") { vals.push(b.archived); sets.push(`archived = $${vals.length}`); }
  if (b.state !== undefined) {
    vals.push(JSON.stringify(b.state)); sets.push(`state = $${vals.length}`);
    // editing a finalized deck makes it a draft again until it is finalized
    sets.push("status = case when status = 'finalized' then 'draft' else status end");
  }
  vals.push(id);
  await q(`update decks set ${sets.join(", ")} where id = $${vals.length}`, vals);
  return Response.json({ ok: true });
});
