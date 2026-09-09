#!/usr/bin/env python3
"""Point the whole site at a different GitHub username.

Renaming the GitHub account changes the Pages host, and the host is written
into this repo in more places than is obvious: the canonical link, four social
card tags, the JSON-LD `url` and `image`, the sitemap line in robots.txt, the
SITE constant the generator builds every absolute URL from, the Daily News
dashboard hosted from another repo on the same account, and the github.com
source links on three Lab write-ups. GitHub redirects renamed repo URLs, but a
redirect is not something to leave on a portfolio: it lapses the day somebody
else registers the old name.

Run this AFTER renaming the account on GitHub, then commit and push:

    python3 scripts/rename-github-user.py aibotvivi vivienchin

It rewrites the sources, re-runs build-pages.py so every generated page and the
sitemap follow, and prints the things it cannot do for you.

Generated files are not edited directly — they are rebuilt, which is the only
way the two stay honest. --dry-run shows the damage first.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Sources only. Everything under a generated path is rebuilt, not patched.
SOURCES = ['index.html', 'photography.html', 'robots.txt', 'README.md',
           'CLAUDE.md', 'scripts/build-pages.py']


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    dry = '--dry-run' in sys.argv
    if len(args) != 2:
        sys.exit('usage: rename-github-user.py OLD_USER NEW_USER [--dry-run]')
    old, new = args
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9-]{0,38}', new):
        sys.exit('%r is not a valid GitHub username' % new)
    if old == new:
        sys.exit('old and new are the same')

    # The Pages host and the github.com account path both carry the username.
    swaps = [('%s.github.io' % old, '%s.github.io' % new),
             ('github.com/%s/' % old, 'github.com/%s/' % new)]
    old_host, new_host = swaps[0]
    total = 0
    for rel in SOURCES:
        p = ROOT / rel
        if not p.exists():
            print('  skip %-28s (missing)' % rel)
            continue
        t = p.read_text(encoding='utf-8')
        n = sum(t.count(a) for a, _ in swaps)
        if not n:
            continue
        total += n
        print('  %-28s %d occurrence%s' % (rel, n, '' if n == 1 else 's'))
        if not dry:
            for a, b in swaps:
                t = t.replace(a, b)
            p.write_text(t, encoding='utf-8')

    if not total:
        sys.exit('found no reference to %s — is OLD_USER right?' % old_host)
    if dry:
        print('\n--dry-run: nothing written.')
        return

    print('\nrebuilding generated pages and the sitemap...')
    subprocess.run([sys.executable, str(ROOT / 'scripts' / 'build-pages.py')], check=True)

    left = subprocess.run(['git', '-C', str(ROOT), 'grep', '-l', old],
                          capture_output=True, text=True).stdout.split()
    left = [f for f in left if not f.endswith('rename-github-user.py')]
    if left:
        print('\nSTILL MENTIONS %s (check these by hand):' % old)
        for f in left:
            print('  ' + f)
    else:
        print('\nno reference to %s left in the repo.' % old)

    print("""
Not done for you, and the site is not fully moved until they are:

  1. GitHub → Settings → Account → Change username. Do this FIRST; this
     script only follows it. The old %s address stops serving the
     Pages site, so anything already shared with that URL breaks.
  2. Rename the root redirect repo `%s` to `%s`.
     A user Pages site only works from a repo named after the account.
  3. Google Analytics → Admin → Data streams → update the stream URL to
     https://%s/portfolio/.
  4. Google Search Console → add https://%s/portfolio/ as a new
     property and submit the sitemap again. The old property will not follow.
  5. Update the link in your LinkedIn profile, and anywhere else you have
     pasted the old one.
""" % (old_host, old_host, new_host, new_host, new_host))


if __name__ == '__main__':
    main()
