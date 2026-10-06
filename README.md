# HTL Deck Platform

Next.js app + Postgres (Neon) for building and sharing HTL Aircon decks.

* Real login (Creator / User roles), enforced on the server.
* Shared project register and master-deck text edits stored in Postgres.
* The slide editor front end lives in `src/frontend/app.html` (images/fonts in `public/media`).

## Deploy (Vercel + Neon)

1. Neon: create a project, copy the **pooled** (`-pooler`) and **direct** connection strings.
2. Vercel: import this repo; add environment variables
   * `DATABASE_URL` = pooled string
   * `DIRECT_URL` = direct string
   * `AUTH_SECRET` = long random text (`node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"`)
3. On your PC, create `.env.local` with the same three values plus
   `SEED_CREATOR_USERNAME`, `SEED_CREATOR_NAME`, `SEED_CREATOR_PASSWORD` (see `.env.example`), then:

```bash
npm install
npm run migrate          # creates the tables
npm run seed             # creates the first Creator login
npm run seed:projects    # loads the 2,182-project register
```

## Updates

Every push to `main` redeploys on Vercel. The build runs `npm run migrate` first, so new database tables are created automatically - no manual step.

## Local development (no accounts needed)

```bash
npm install
npm run db:local         # embedded Postgres, keep this window open
# new window: copy the printed DATABASE_URL into .env.local (+ AUTH_SECRET), then
npm run migrate && npm run seed && npm run dev
```
