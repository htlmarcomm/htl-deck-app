import { api, currentUser } from "@/lib/auth";

export const dynamic = "force-dynamic";

export const GET = api(async () => {
  const u = await currentUser();
  if (!u) return Response.json({ error: "Not signed in" }, { status: 401 });
  return Response.json({ user: u });
});
