import { api, requireUser } from "@/lib/auth";
import { q1 } from "@/lib/db";
import { cleanName, loadDeck } from "@/lib/decks";

export const dynamic = "force-dynamic";

// Copy a deck (into the caller's own list) as a fresh draft.
export const POST = api(async (_req: Request, ctx: { params: Promise<{ id: string }> }) => {
  const u = await requireUser();
  const { id } = await ctx.params;
  const d = await loadDeck(id, u);
  const copy = await q1(
    `insert into decks (owner_id, name, client_name, state) values ($1, $2, $3, $4)
     returning id, name, client_name, status, archived, updated_at`,
    [u.id, cleanName(d.name + " (Copy)", "Copy"), d.client_name, JSON.stringify(d.state)]
  );
  return Response.json({ deck: copy }, { status: 201 });
});
