import { HttpError, type SessionUser } from "./auth";
import { q1 } from "./db";

export interface DeckRow {
  id: string;
  owner_id: string;
  name: string;
  client_name: string | null;
  status: "draft" | "finalized";
  archived: boolean;
  state: any;
  updated_at: string;
}

/** A deck the user may touch: their own, or any deck if they are a Creator. */
export async function loadDeck(id: string, user: SessionUser): Promise<DeckRow> {
  if (!/^[0-9a-f-]{36}$/.test(id)) throw new HttpError(404, "No such deck");
  const d = await q1<DeckRow>(
    "select id, owner_id, name, client_name, status, archived, state, updated_at from decks where id = $1",
    [id]
  );
  if (!d || (user.role !== "creator" && d.owner_id !== user.id)) throw new HttpError(404, "No such deck");
  return d;
}

export function cleanName(v: unknown, fallback: string): string {
  const s = String(v ?? "").replace(/\s+/g, " ").trim().slice(0, 160);
  return s || fallback;
}
