import { q1 } from "@/lib/db";

export const dynamic = "force-dynamic";

// Public on purpose: shared decks show these pictures to people without a
// login. Ids are content hashes, not guessable lists.
export async function GET(_req: Request, ctx: { params: Promise<{ id: string }> }) {
  const { id } = await ctx.params;
  if (!/^[a-f0-9]{24}$/.test(id)) return new Response("Not found", { status: 404 });
  const r = await q1<{ mime: string; data: Buffer }>("select mime, data from assets where id = $1", [id]);
  if (!r) return new Response("Not found", { status: 404 });
  return new Response(new Uint8Array(r.data), {
    headers: { "Content-Type": r.mime, "Cache-Control": "public, max-age=31536000, immutable" },
  });
}
