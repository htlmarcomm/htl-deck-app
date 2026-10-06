import { randomBytes } from "node:crypto";
import { api, HttpError, requireUser } from "@/lib/auth";
import { pool } from "@/lib/db";
import { loadDeck } from "@/lib/decks";

export const dynamic = "force-dynamic";

// Finalize: freeze the deck as the next version and give it a share link.
//   mode "keep"    - new version AND a brand-new link; older links keep serving older versions
//   mode "replace" - new version; the deck's current live link is re-pointed to it (same URL)
// The first finalize always creates a link.
export const POST = api(async (req: Request, ctx: { params: Promise<{ id: string }> }) => {
  const u = await requireUser();
  const { id } = await ctx.params;
  const deck = await loadDeck(id, u);
  const b = await req.json().catch(() => ({}));
  const snap = b.snapshot;
  if (!snap || !Array.isArray(snap.slides) || !snap.slides.length) throw new HttpError(400, "The deck has no slides to finalize");
  const mode = b.mode === "replace" ? "replace" : "keep";

  const c = await pool().connect();
  try {
    await c.query("begin");
    const n = await c.query("select coalesce(max(version_num), 0) + 1 as n from deck_versions where deck_id = $1", [id]);
    const versionNum: number = n.rows[0].n;
    const v = await c.query(
      "insert into deck_versions (deck_id, version_num, snapshot, created_by) values ($1, $2, $3, $4) returning id",
      [id, versionNum, JSON.stringify({ name: deck.name, slides: snap.slides }), u.id]
    );
    const versionId = v.rows[0].id;

    let token: string | null = null;
    if (mode === "replace") {
      const cur = await c.query(
        "select id, token from share_links where deck_id = $1 and revoked_at is null order by created_at desc limit 1",
        [id]
      );
      if (cur.rows[0]) {
        await c.query("update share_links set version_id = $1 where id = $2", [versionId, cur.rows[0].id]);
        token = cur.rows[0].token;
      }
    }
    if (!token) {
      token = randomBytes(9).toString("base64url");
      await c.query("insert into share_links (token, deck_id, version_id, created_by) values ($1, $2, $3, $4)", [token, id, versionId, u.id]);
    }
    await c.query("update decks set status = 'finalized', updated_at = now() where id = $1", [id]);
    await c.query("commit");
    return Response.json({ token, url: `/s/${token}`, versionNum });
  } catch (e) {
    await c.query("rollback");
    throw e;
  } finally {
    c.release();
  }
});
