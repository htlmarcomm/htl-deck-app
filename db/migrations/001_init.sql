-- HTL deck platform: initial schema.

create table users (
  id            uuid primary key default gen_random_uuid(),
  username      text not null unique,
  name          text not null,
  password_hash text not null,
  role          text not null check (role in ('creator', 'user')),
  active        boolean not null default true,
  created_at    timestamptz not null default now()
);

-- Generic shared JSON documents (the project register, master-deck text
-- edits, ...). Same shape the prototype used: collection / id / data.
create table docs (
  collection text not null,
  id         text not null,
  data       jsonb not null,
  updated_at timestamptz not null default now(),
  updated_by uuid references users (id) on delete set null,
  primary key (collection, id)
);

create table decks (
  id          uuid primary key default gen_random_uuid(),
  owner_id    uuid not null references users (id) on delete restrict,
  name        text not null,
  client_name text,
  status      text not null default 'draft' check (status in ('draft', 'finalized')),
  archived    boolean not null default false,
  state       jsonb not null default '{}'::jsonb,
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now()
);
create index decks_owner_idx on decks (owner_id);

-- One immutable snapshot per finalize.
create table deck_versions (
  id          uuid primary key default gen_random_uuid(),
  deck_id     uuid not null references decks (id) on delete cascade,
  version_num int not null,
  snapshot    jsonb not null,
  created_by  uuid references users (id) on delete set null,
  created_at  timestamptz not null default now(),
  unique (deck_id, version_num)
);

create table share_links (
  id          uuid primary key default gen_random_uuid(),
  token       text not null unique,
  deck_id     uuid not null references decks (id) on delete cascade,
  version_id  uuid references deck_versions (id) on delete set null,
  created_by  uuid references users (id) on delete set null,
  created_at  timestamptz not null default now(),
  revoked_at  timestamptz,
  view_count  int not null default 0
);
create index share_links_deck_idx on share_links (deck_id);
