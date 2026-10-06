import { api, requireUser } from "@/lib/auth";
import { q } from "@/lib/db";
import { loadDeck } from "@/lib/decks";

export const dynamic = "force-dynamic";

// Version history with each version's share links.
export const GET = api(async (_req: Request, ctx: { params: Promise<{ id: string }> }) => {
  const u = await requireUser();
  const { id } = await ctx.params;
  await loadDeck(id, u);
  const versions = await q(
    `select v.id, v.version_num, v.created_at, usr.name as created_by,
            coalesce(json_agg(json_build_object('id', l.id, 'token', l.token, 'revoked', l.revoked_at is not null,
                                                'views', l.view_count, 'created_at', l.created_at) order by l.created_at)
                     filter (where l.id is not null), '[]') as links
       from deck_versions v
       left join users usr on usr.id = v.created_by
       left join share_links l on l.version_id = v.id
      where v.deck_id = $1
      group by v.id, usr.name
      order by v.version_num desc`,
    [id]
  );
  return Response.json({ versions });
});
