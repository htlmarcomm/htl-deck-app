import { q1 } from "@/lib/db";

export const dynamic = "force-dynamic";

// PUBLIC: what a share link shows. No login. Counts the view.
export async function GET(_req: Request, ctx: { params: Promise<{ token: string }> }) {
  const { token } = await ctx.params;
  if (!/^[A-Za-z0-9_-]{8,40}$/.test(token)) return Response.json({ error: "Not found" }, { status: 404 });
  const r = await q1<{ snapshot: any; version_num: number }>(
    `select v.snapshot, v.version_num
       from share_links l join deck_versions v on v.id = l.version_id
      where l.token = $1 and l.revoked_at is null`,
    [token]
  );
  if (!r) return Response.json({ error: "This link is no longer available." }, { status: 404 });
  await q1("update share_links set view_count = view_count + 1 where token = $1", [token]);
  return Response.json(
    { name: r.snapshot.name, version: r.version_num, slides: r.snapshot.slides },
    { headers: { "Cache-Control": "no-store", "X-Robots-Tag": "noindex" } }
  );
}
