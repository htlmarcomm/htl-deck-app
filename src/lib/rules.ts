import { HttpError, requireUser, type SessionUser } from "./auth";

// Shared document collections the front end may use, and who may write them.
// Everyone signed in can read; unknown collections are refused outright.
const WRITE: Record<string, "creator" | "user"> = {
  projects: "creator", // project register: only Creators edit
  masterText: "creator", // master-deck text edits: only Creators
};

export function assertCollection(name: string) {
  if (!Object.prototype.hasOwnProperty.call(WRITE, name)) throw new HttpError(404, "Unknown collection");
}

export async function readAccess(collection: string): Promise<SessionUser> {
  assertCollection(collection);
  return requireUser();
}

export async function writeAccess(collection: string): Promise<SessionUser> {
  assertCollection(collection);
  const u = await requireUser();
  if (WRITE[collection] === "creator" && u.role !== "creator") {
    throw new HttpError(403, "Only Creator accounts can change this");
  }
  return u;
}

export function assertId(id: string) {
  if (!/^[A-Za-z0-9_.\-]{1,120}$/.test(id)) throw new HttpError(400, "Bad id");
}
