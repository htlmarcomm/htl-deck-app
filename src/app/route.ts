import fs from "node:fs";
import path from "node:path";
import { currentUser } from "@/lib/auth";

export const dynamic = "force-dynamic";

let shell: string | null = null;
function appShell(): string {
  return (shell ??= fs.readFileSync(path.join(process.cwd(), "src", "frontend", "app.html"), "utf8"));
}

// "/" is the application. Signed-out visitors are sent to /login; signed-in
// ones get the page with their identity injected. (The role shown in the UI
// is a convenience only - every write is re-checked on the server.)
export async function GET(req: Request) {
  const user = await currentUser();
  if (!user) return Response.redirect(new URL("/login", req.url), 302);

  const me = JSON.stringify({ id: user.id, username: user.username, name: user.name, role: user.role }).replace(/</g, "\\u003c");
  const html = appShell().replace("<head>", `<head><script>window.__HTL_USER__=${me};</script>`);
  return new Response(html, {
    headers: { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "private, no-store" },
  });
}
