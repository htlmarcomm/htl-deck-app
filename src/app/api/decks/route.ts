import { api, requireUser } from "@/lib/auth";
import { q, q1 } from "@/lib/db";
import { cleanName } from "@/lib/decks";

export const dynamic = "force-dynamic";

// Decks the user can see: their own; a Creator sees everyone's.
export const GET = api(async () => {
  const u = await requireUser();
  const rows = await q(
    `select d.id, d.name, d.client_name, d.status, d.archived, d.created_at, d.updated_at,
            usr.username as owner_username, usr.name as owner_name,
            (select count(*)::int from deck_versions v where v.deck_id = d.id) as versions,
            (select token from share_links l where l.deck_id = d.id and l.revoked_at is null order by l.created_at desc limit 1) as token,
            (d.state->'slides'->0->>'key') as first_key
       from decks d join users usr on usr.id = d.owner_id
      where ($1::boolean or d.owner_id = $2)
      order by d.updated_at desc`,
    [u.role === "creator", u.id]
  );
  return Response.json({ decks: rows });
});

export const POST = api(async (req: Request) => {
  const u = await requireUser();
  const b = await req.json().catch(() => ({}));
  const d = await q1(
    `insert into decks (owner_id, name, client_name, state) values ($1, $2, $3, $4)
     returning id, name, client_name, status, archived, updated_at`,
    [u.id, cleanName(b.name, "Untitled deck"), b.client_name ? cleanName(b.client_name, "") : null, JSON.stringify(b.state ?? {})]
  );
  return Response.json({ deck: d }, { status: 201 });
});
