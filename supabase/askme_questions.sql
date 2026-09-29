-- What visitors ask Askme.bot, kept for 90 days so the archive can be improved.
--
-- Run this once in the SQL editor of the Supabase project the portfolio uses:
--   https://supabase.com/dashboard/project/wkkyoszrdontvziehaku/sql/new
-- It is safe to run again; every statement replaces what it made last time.
--
-- Same rules as lab_updates.sql: the page ships the public anon key, so row
-- level security is the only thing protecting this table. The policy grants
-- INSERT and nothing else. Do not add a SELECT policy; read the rows in the
-- dashboard's Table Editor, which uses your own login.
--
-- Three things are enforced here rather than trusted to the page, because
-- anyone can post to the REST endpoint without the page:
--   * a healing-path row is refused unless it carries consent = true (health
--     details are special category data under UK GDPR and need explicit consent);
--   * emails and phone numbers are blanked by a trigger before the row is stored;
--   * rows older than 90 days are deleted by a nightly pg_cron job.

create table if not exists public.askme_questions (
  id           bigint generated always as identity primary key,
  created_at   timestamptz not null default now(),
  conversation text not null,           -- random per conversation; not tied to a person
  path         text not null,           -- 'hiring' | 'healing'
  via          text not null,           -- 'chip' | 'typed'
  topic        text not null,           -- archive entry id, 'none' or 'greeting'
  answered_by  text not null,           -- 'archive' | 'model' | 'fallback'
  consent      boolean not null default false,
  question     text not null
);

create index if not exists askme_questions_created_at on public.askme_questions (created_at);

-- Blank anything that looks like an email address or a phone number, and pin
-- created_at to the server's clock so a row cannot be backdated past the purge.
create or replace function public.askme_questions_scrub() returns trigger
language plpgsql as $$
begin
  new.question := regexp_replace(new.question, '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', '[email]', 'g');
  new.question := regexp_replace(new.question, '\+?[0-9][0-9 ()-]{8,}[0-9]', '[number]', 'g');
  new.created_at := now();
  return new;
end;
$$;

drop trigger if exists askme_questions_scrub on public.askme_questions;
create trigger askme_questions_scrub
  before insert on public.askme_questions
  for each row execute function public.askme_questions_scrub();

alter table public.askme_questions enable row level security;

drop policy if exists "anon can log a question" on public.askme_questions;
create policy "anon can log a question"
  on public.askme_questions
  for insert
  to anon
  with check (
    path in ('hiring', 'healing')
    and (path = 'hiring' or consent = true)
    and via in ('chip', 'typed')
    and answered_by in ('archive', 'model', 'fallback')
    and char_length(topic) between 1 and 40
    and char_length(conversation) between 8 and 64
    and char_length(question) between 1 and 600
  );

-- Nightly purge at 03:17 UTC. pg_cron ships with Supabase; this enables it if
-- it is not already on (Database > Extensions shows it afterwards).
create extension if not exists pg_cron;

select cron.unschedule(jobid) from cron.job where jobname = 'askme-questions-90-days';
select cron.schedule(
  'askme-questions-90-days',
  '17 3 * * *',
  $$delete from public.askme_questions where created_at < now() - interval '90 days'$$
);

-- Handy views of the table once rows arrive (run in the SQL editor):
--   select created_at, path, topic, question from askme_questions order by created_at desc limit 100;
--   select path, topic, count(*) from askme_questions group by 1, 2 order by 3 desc;
--   select question from askme_questions where topic = 'none' order by created_at desc;  -- gaps to fill
