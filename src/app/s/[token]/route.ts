import fs from "node:fs";
import path from "node:path";

export const dynamic = "force-dynamic";

let shell: string | null = null;

// PUBLIC share page: the same front end, started in read-only "viewer"
// mode. It fetches the deck from /api/share/<token>; nothing about the
// editor or any account is reachable from here.
export async function GET(_req: Request, ctx: { params: Promise<{ token: string }> }) {
  const { token } = await ctx.params;
  if (!/^[A-Za-z0-9_-]{8,40}$/.test(token)) return new Response("Not found", { status: 404 });
  shell ??= fs.readFileSync(path.join(process.cwd(), "src", "frontend", "app.html"), "utf8");
  const html = shell.replace("<head>", `<head><script>window.__HTL_SHARE_TOKEN__=${JSON.stringify(token)};</script>`);
  return new Response(html, {
    headers: { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store", "X-Robots-Tag": "noindex" },
  });
}
