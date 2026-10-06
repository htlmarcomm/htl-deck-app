import { createHash } from "node:crypto";
import { api, HttpError, requireUser } from "@/lib/auth";
import { q } from "@/lib/db";

export const dynamic = "force-dynamic";

const OK = new Set(["image/jpeg", "image/png", "image/webp", "image/gif"]);
const MAX = 4_000_000; // Vercel's request body limit is 4.5 MB; the browser downsizes first

// Upload one picture: raw bytes as the body, content-type = the image type.
export const POST = api(async (req: Request) => {
  const user = await requireUser();
  const mime = (req.headers.get("content-type") || "").split(";")[0].trim().toLowerCase();
  if (!OK.has(mime)) throw new HttpError(415, "Only JPEG, PNG, WebP or GIF pictures");
  const buf = Buffer.from(await req.arrayBuffer());
  if (!buf.length) throw new HttpError(400, "Empty file");
  if (buf.length > MAX) throw new HttpError(413, "Picture is too large (max 4 MB) - try a smaller one");
  const id = createHash("sha256").update(buf).digest("hex").slice(0, 24);
  await q(
    "insert into assets (id, mime, data, size, created_by) values ($1, $2, $3, $4, $5) on conflict (id) do nothing",
    [id, mime, buf, buf.length, user.id]
  );
  return Response.json({ id, url: `/a/${id}` }, { status: 201 });
});
