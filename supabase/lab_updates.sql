-- The Lab sign-up list for the portfolio desk.
--
-- Run this once in the SQL editor of the Supabase project the portfolio uses:
--   https://supabase.com/dashboard/project/wkkyoszrdontvziehaku/sql/new
--
-- The page ships the project's anon key, which is public by design. Row level
-- security is therefore the only thing protecting this table: the policy below
-- grants INSERT and nothing else, so the browser can add an address and cannot
-- read the list back. Do not add a SELECT policy, and never put the
-- service_role key in the page — it bypasses RLS entirely.

create table if not exists public.lab_updates (
  id         bigint generated always as identity primary key,
  email      text not null,
  source     text,
  page       text,
  created_at timestamptz not null default now()
);

-- One row per address, compared without case: the unique violation is what the
-- page turns into "You are already on the list" rather than an error.
create unique index if not exists lab_updates_email_key
  on public.lab_updates (lower(email));

alter table public.lab_updates enable row level security;

drop policy if exists "anon can subscribe" on public.lab_updates;
create policy "anon can subscribe"
  on public.lab_updates
  for insert
  to anon
  with check (
    -- shape check, so the table cannot be used as free storage
    char_length(email) between 6 and 254
    and email like '%_@_%._%'
    and source = 'portfolio-lab'
  );
