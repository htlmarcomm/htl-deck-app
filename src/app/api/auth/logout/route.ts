import { cookies } from "next/headers";
import { api, SESSION_COOKIE } from "@/lib/auth";

export const POST = api(async () => {
  const jar = await cookies();
  jar.delete(SESSION_COOKIE);
  return Response.json({ ok: true });
});
