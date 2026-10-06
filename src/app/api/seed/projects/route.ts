import fs from "node:fs";
import path from "node:path";
import { api, requireCreator } from "@/lib/auth";

export const dynamic = "force-dynamic";

// The starting project register (2,182 projects). Creator-only: it is
// company data, so it is not a public static file. The "Load project
// register" button on the Project database screen fetches it from here.
export const GET = api(async () => {
  await requireCreator();
  const file = path.join(process.cwd(), "db", "projects_seed.json");
  return new Response(fs.readFileSync(file), {
    headers: { "Content-Type": "application/json", "Cache-Control": "private, no-store" },
  });
});
