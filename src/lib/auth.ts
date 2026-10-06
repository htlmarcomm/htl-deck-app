import { cookies } from "next/headers";
import { jwtVerify, SignJWT } from "jose";
import bcrypt from "bcryptjs";
import { q1 } from "./db";

export const SESSION_COOKIE = "htl_session";
const SESSION_DAYS = 7;

export type Role = "creator" | "user";
export interface SessionUser {
  id: string;
  username: string;
  name: string;
  role: Role;
}

function secret(): Uint8Array {
  const s = process.env.AUTH_SECRET;
  if (!s || s.length < 16) throw new Error("AUTH_SECRET is not set (or too short)");
  return new TextEncoder().encode(s);
}

export async function hashPassword(pw: string): Promise<string> {
  return bcrypt.hash(pw, 12);
}
export async function checkPassword(pw: string, hash: string): Promise<boolean> {
  return bcrypt.compare(pw, hash);
}

export async function signSession(uid: string): Promise<string> {
  return new SignJWT({ uid })
    .setProtectedHeader({ alg: "HS256" })
    .setIssuedAt()
    .setExpirationTime(`${SESSION_DAYS}d`)
    .sign(secret());
}

export function sessionCookieOptions() {
  return {
    httpOnly: true,
    sameSite: "lax" as const,
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: SESSION_DAYS * 24 * 3600,
  };
}

/** The signed-in user, re-read from the database so a deactivated account or
 *  a changed role takes effect immediately. null if not signed in. */
export async function currentUser(): Promise<SessionUser | null> {
  const jar = await cookies();
  const tok = jar.get(SESSION_COOKIE)?.value;
  if (!tok) return null;
  let uid: string;
  try {
    const { payload } = await jwtVerify(tok, secret());
    uid = String(payload.uid);
  } catch {
    return null;
  }
  const u = await q1<{ id: string; username: string; name: string; role: Role; active: boolean }>(
    "select id, username, name, role, active from users where id = $1",
    [uid]
  );
  if (!u || !u.active) return null;
  return { id: u.id, username: u.username, name: u.name, role: u.role };
}

export class HttpError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

export async function requireUser(): Promise<SessionUser> {
  const u = await currentUser();
  if (!u) throw new HttpError(401, "Not signed in");
  return u;
}
export async function requireCreator(): Promise<SessionUser> {
  const u = await requireUser();
  if (u.role !== "creator") throw new HttpError(403, "Only Creator accounts can do this");
  return u;
}

/** Wrap a route handler so HttpErrors become JSON responses. */
export function api<A extends unknown[]>(fn: (...args: A) => Promise<Response>) {
  return async (...args: A): Promise<Response> => {
    try {
      return await fn(...args);
    } catch (e) {
      if (e instanceof HttpError) return Response.json({ error: e.message }, { status: e.status });
      console.error(e);
      return Response.json({ error: "Server error" }, { status: 500 });
    }
  };
}
