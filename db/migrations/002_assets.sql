-- Uploaded slide photos (swapped-in pictures). Content-addressed so the same
-- picture is stored once, and served publicly by an unguessable id so shared
-- decks can show them.
create table assets (
  id         text primary key,          -- first 24 hex chars of the sha-256
  mime       text not null,
  data       bytea not null,
  size       int not null,
  created_by uuid references users (id) on delete set null,
  created_at timestamptz not null default now()
);
