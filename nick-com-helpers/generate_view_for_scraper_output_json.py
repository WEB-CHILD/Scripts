#!/usr/bin/env python3
"""
generate_view_for_scraper_output_json.py
=========================================
Converts a folder of scraped JSON files into a self-contained, serverless HTML viewer.

USAGE
-----
    python3 generate_view_for_scraper_output_json.py

Run the script from the folder that contains the .json scraper output files.
It will create (or overwrite) a  viewer/  subfolder next to the script:

    viewer/
    ├── index.html        ← open this in any browser
    └── boards/
        └── *.html        ← one page per JSON file, with all data baked in

INPUT FORMAT
------------
Each .json file must be an array with one board object:
  [{ "board_link": "...", "threads": [ { "thread_url", "crawl_date", "status",
     "posts": [ { "content", "metadata": { "subject", "date", "from",
                  "playback_url", "year_time_jump_detected" } } ] } ] }]

File names are expected to follow the pattern:
  <seq>_y-<year>_bid-<id>_crawl-<timestamp>_<board-slug>.json

RE-RUNNING
----------
Safe to re-run at any time — all output files are overwritten. Add new .json
files to the folder and re-run to pick them up.
"""

import argparse
import json
import os
import re
import html as htmllib
from pathlib import Path

_parser = argparse.ArgumentParser(description="Generate HTML viewer from scraped JSON files.")
_parser.add_argument("--folder", default=None, metavar="DIR",
                     help="Folder containing .json files (default: script directory)")
_parser.add_argument("--output-dir", default=None, metavar="DIR",
                     help="Output directory for viewer (default: <folder>/viewer)")
_args = _parser.parse_args()

FOLDER = Path(_args.folder).resolve() if _args.folder else Path(__file__).parent
OUT_DIR = Path(_args.output_dir).resolve() if _args.output_dir else FOLDER / "viewer"
BOARDS_DIR = OUT_DIR / "boards"
OUT_DIR.mkdir(exist_ok=True)
BOARDS_DIR.mkdir(exist_ok=True)

CSS_SHARED = """
:root {
  --orange: #ff6b00;
  --orange-light: #ff8c2a;
  --teal: #00a8a8;
  --bg: #0d0d1a;
  --surface: #141428;
  --surface2: #1c1c38;
  --border: #2a2a50;
  --text: #e8e8f0;
  --muted: #7878a0;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Segoe UI', system-ui, sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; }
a, button, select, [onclick] { cursor: pointer; }
a { color: inherit; }
"""

def esc(s):
    return htmllib.escape(str(s)) if s else ""

def board_name_from_file(filename):
    parts = filename.replace(".json", "").split("_")
    slug = parts[-1]
    return slug.replace("-", " ").title()

def format_crawl(raw):
    if raw and len(raw) >= 8:
        return f"{raw[:4]}-{raw[4:6]}-{raw[6:8]}"
    return raw or ""

def thread_subject(thread):
    posts = thread.get("posts", [])
    if posts:
        s = (posts[0].get("metadata") or {}).get("subject", "")
        if s:
            return s
    url = thread.get("thread_url", "")
    m = re.search(r"tID=(\d+)", url)
    return f"Thread #{m.group(1)}" if m else "Untitled Thread"

def render_board_html(filename, board, board_name):
    threads = board.get("threads", [])
    board_link = board.get("board_link", "")
    total_posts = sum(len(t.get("posts", [])) for t in threads)
    crawl_dates = sorted({format_crawl(t.get("crawl_date","")) for t in threads if t.get("crawl_date")})
    crawl_str = ", ".join(crawl_dates[:3])

    threads_html_parts = []
    for i, thread in enumerate(threads):
        posts = thread.get("posts", [])
        subject = esc(thread_subject(thread))
        t_url = esc(thread.get("thread_url", ""))
        crawl_fmt = esc(format_crawl(thread.get("crawl_date", "")))
        post_count = len(posts)

        posts_inner = []
        for pi, post in enumerate(posts):
            meta = post.get("metadata") or {}
            author = esc(meta.get("from") or "Unknown")
            date_str = esc(meta.get("date") or "")
            subj = esc(meta.get("subject") or "")
            content = esc(post.get("content") or "")
            playback = esc(meta.get("playback_url") or "")
            year_warn = meta.get("year_time_jump_detected", False)
            av = esc((meta.get("from") or "?")[0].upper())

            post_subj_html = f'<div class="post-subject">{subj}</div>' if subj and pi > 0 else ""
            playback_html = f'<div class="post-playback"><a href="{playback}" target="_blank" rel="noopener">View archived ↗</a></div>' if playback else ""
            year_html = '<span class="year-warn">year jump</span>' if year_warn else ""

            posts_inner.append(f"""
<div class="post{'  post-first' if pi == 0 else ''}">
  <div class="post-hdr">
    <div class="avatar">{av}</div>
    <div class="post-meta">
      <div class="post-author">{author}</div>
      <div class="post-date">{date_str}</div>
      {post_subj_html}
    </div>
    {year_html}
    {playback_html}
  </div>
  <div class="post-body">{content}</div>
</div>""")

        posts_html = "\n".join(posts_inner) if posts_inner else '<div class="no-posts">No posts were archived for this thread.</div>'

        badge = f'<span class="post-badge">{post_count} post{"s" if post_count != 1 else ""}</span>' if post_count else ""
        archive_link = f'<a href="{t_url}" target="_blank" rel="noopener">Archive ↗</a>' if t_url else ""
        no_posts_note = '<span class="no-posts-note">No archived posts</span>' if post_count == 0 else ""

        threads_html_parts.append(f"""
<div class="tcard" id="t{i}">
  <div class="thead" onclick="tog('t{i}')">
    <div class="tarrow">
      <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="9 18 15 12 9 6"/></svg>
    </div>
    <div class="tmeta">
      <div class="tsubject">{subject}</div>
      <div class="tinfo">{badge}{archive_link}<span>Crawled {crawl_fmt}</span>{no_posts_note}</div>
    </div>
  </div>
  <div class="tposts">{posts_html}</div>
</div>""")

    threads_html = "\n".join(threads_html_parts)

    board_link_html = ""
    if board_link:
        board_link_html = f'<div class="blinkrow"><span class="blabel">Original board</span><a href="{esc(board_link)}" target="_blank" rel="noopener">{esc(board_link)}</a></div>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(board_name)} — Message Board Archive</title>
<style>
{CSS_SHARED}
header {{
  background: linear-gradient(135deg,#1a0a2e 0%,#16213e 50%,#0d2137 100%);
  border-bottom: 2px solid var(--orange);
  padding: 1.25rem 2rem;
  display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;
  box-shadow: 0 4px 30px rgba(255,107,0,.12);
  position: sticky; top: 0; z-index: 100;
}}
.back-btn {{
  display: flex; align-items: center; gap: .4rem;
  color: var(--orange-light); text-decoration: none;
  font-size: .85rem; font-weight: 600;
  padding: .4rem .8rem;
  border: 1px solid rgba(255,107,0,.35); border-radius: 6px;
  transition: background .15s, border-color .15s; white-space: nowrap; flex-shrink: 0;
}}
.back-btn:hover {{ background: rgba(255,107,0,.12); border-color: var(--orange); }}
.hinfo {{ flex:1; min-width:0; }}
.btitle {{ font-size:1.4rem; font-weight:800; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
.blinkrow {{ margin-top:.3rem; display:flex; align-items:center; gap:.5rem; flex-wrap:wrap; }}
.blinkrow a {{ font-size:.75rem; color:var(--teal); text-decoration:none; word-break:break-all; }}
.blinkrow a:hover {{ text-decoration:underline; }}
.blabel {{ font-size:.7rem; color:var(--muted); background:rgba(0,168,168,.1); border:1px solid rgba(0,168,168,.25); border-radius:4px; padding:.1rem .4rem; white-space:nowrap; flex-shrink:0; }}
.hstats {{ display:flex; gap:.75rem; flex-wrap:wrap; }}
.spill {{ background:rgba(255,107,0,.1); border:1px solid rgba(255,107,0,.25); border-radius:999px; padding:.3rem .8rem; font-size:.77rem; color:var(--orange-light); white-space:nowrap; }}
.controls {{ max-width:900px; margin:1.5rem auto 0; padding:0 1.5rem; display:flex; gap:.75rem; flex-wrap:wrap; align-items:center; }}
.swrap {{ flex:1; min-width:200px; position:relative; }}
.swrap svg {{ position:absolute; left:.75rem; top:50%; transform:translateY(-50%); color:var(--muted); pointer-events:none; }}
#q {{ width:100%; background:var(--surface2); border:1px solid var(--border); border-radius:8px; padding:.6rem .75rem .6rem 2.25rem; color:var(--text); font-size:.88rem; outline:none; transition:border-color .2s; }}
#q:focus {{ border-color:var(--orange); }}
#q::placeholder {{ color:var(--muted); }}
select {{ background:var(--surface2); border:1px solid var(--border); border-radius:8px; padding:.6rem .75rem; color:var(--text); font-size:.88rem; outline:none; cursor:pointer; }}
select:focus {{ border-color:var(--orange); }}
.clabel {{ font-size:.78rem; color:var(--muted); padding:.6rem 0; }}
main {{ max-width:900px; margin:1.25rem auto 3rem; padding:0 1.5rem; }}
.tcard {{ background:var(--surface); border:1px solid var(--border); border-radius:12px; margin-bottom:1rem; overflow:hidden; transition:border-color .15s; }}
.tcard.open {{ border-color:var(--orange); }}
.thead {{ padding:1rem 1.25rem; cursor:pointer; display:flex; align-items:flex-start; gap:.75rem; user-select:none; transition:background .15s; }}
.thead:hover {{ background:var(--surface2); }}
.tarrow {{ width:22px; height:22px; border-radius:50%; background:rgba(255,107,0,.12); border:1px solid rgba(255,107,0,.3); display:flex; align-items:center; justify-content:center; flex-shrink:0; margin-top:1px; transition:background .15s, transform .2s; color:var(--orange); }}
.tcard.open .tarrow {{ background:rgba(255,107,0,.25); transform:rotate(90deg); }}
.tmeta {{ flex:1; min-width:0; }}
.tsubject {{ font-size:.95rem; font-weight:700; margin-bottom:.35rem; word-break:break-word; }}
.tinfo {{ font-size:.75rem; color:var(--muted); display:flex; gap:.9rem; flex-wrap:wrap; align-items:center; }}
.tinfo a {{ color:var(--teal); text-decoration:none; font-size:.7rem; }}
.tinfo a:hover {{ text-decoration:underline; }}
.post-badge {{ background:rgba(255,107,0,.12); color:var(--orange-light); border:1px solid rgba(255,107,0,.25); border-radius:999px; padding:.1rem .55rem; font-size:.7rem; font-weight:600; }}
.no-posts-note {{ font-size:.72rem; font-style:italic; }}
.tposts {{ display:none; border-top:1px solid var(--border); }}
.tcard.open .tposts {{ display:block; }}
.post {{ border-bottom:1px solid var(--border); padding:1rem 1.25rem 1rem 1.5rem; position:relative; }}
.post:last-child {{ border-bottom:none; }}
.post::before {{ content:''; position:absolute; left:0; top:0; bottom:0; width:3px; background:var(--border); }}
.post-first::before {{ background:var(--orange); }}
.post-hdr {{ display:flex; align-items:flex-start; gap:.6rem; margin-bottom:.55rem; flex-wrap:wrap; }}
.avatar {{ width:30px; height:30px; border-radius:50%; background:linear-gradient(135deg,var(--orange),var(--teal)); display:flex; align-items:center; justify-content:center; font-size:.8rem; font-weight:700; color:white; flex-shrink:0; text-transform:uppercase; }}
.post-meta {{ flex:1; min-width:0; }}
.post-author {{ font-size:.85rem; font-weight:700; color:var(--orange-light); }}
.post-date {{ font-size:.72rem; color:var(--muted); margin-top:.1rem; }}
.post-subject {{ font-size:.78rem; color:var(--teal); font-style:italic; margin-top:.1rem; }}
.post-playback a {{ color:var(--muted); text-decoration:none; font-size:.7rem; }}
.post-playback a:hover {{ color:var(--teal); text-decoration:underline; }}
.year-warn {{ font-size:.7rem; background:rgba(255,107,0,.1); border:1px solid rgba(255,107,0,.3); border-radius:4px; padding:.1rem .4rem; color:var(--orange-light); margin-left:auto; flex-shrink:0; }}
.post-body {{ font-size:.88rem; line-height:1.65; white-space:pre-wrap; word-break:break-word; }}
.no-posts {{ padding:1rem 1.5rem; color:var(--muted); font-size:.85rem; font-style:italic; }}
.empty {{ text-align:center; padding:3rem 1rem; color:var(--muted); }}
footer {{ text-align:center; padding:1.5rem; font-size:.75rem; color:var(--muted); border-top:1px solid var(--border); }}
</style>
</head>
<body>
<header>
  <a class="back-btn" href="../index.html">
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="15 18 9 12 15 6"/></svg>
    All Boards
  </a>
  <div class="hinfo">
    <div class="btitle">{esc(board_name)}</div>
    {board_link_html}
  </div>
  <div class="hstats">
    <span class="spill">{len(threads):,} threads</span>
    <span class="spill">{total_posts:,} posts</span>
    {f'<span class="spill">Crawled {esc(crawl_str)}</span>' if crawl_str else ""}
  </div>
</header>

<div class="controls">
  <div class="swrap">
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
    <input id="q" type="text" placeholder="Search threads and posts…" autocomplete="off" oninput="filt()">
  </div>
  <select onchange="filt()">
    <option value="all">All threads</option>
    <option value="has">With posts only</option>
    <option value="none">Empty threads only</option>
  </select>
  <span class="clabel" id="clabel">{len(threads):,} threads</span>
</div>

<main id="main">
{threads_html}
</main>

<footer>Message board archive — scraped from Nickelodeon Blab via SolrWayback</footer>

<script>
const all = Array.from(document.querySelectorAll('.tcard'));

function tog(id) {{
  document.getElementById(id).classList.toggle('open');
}}

function filt() {{
  const q = document.getElementById('q').value.toLowerCase();
  const sel = document.querySelector('select').value;
  let shown = 0;
  all.forEach(card => {{
    const hasPosts = card.querySelector('.post') !== null;
    if (sel === 'has' && !hasPosts) {{ card.style.display = 'none'; return; }}
    if (sel === 'none' && hasPosts) {{ card.style.display = 'none'; return; }}
    if (q) {{
      const text = card.textContent.toLowerCase();
      if (!text.includes(q)) {{ card.style.display = 'none'; return; }}
    }}
    card.style.display = '';
    shown++;
  }});
  if (!q && sel === 'all') shown = all.length;
  document.getElementById('clabel').textContent = shown + ' thread' + (shown !== 1 ? 's' : '');
}}
</script>
</body>
</html>"""


def generate_index(entries):
    cards_html = []
    for e in entries:
        name = esc(e["name"])
        year = esc(e["year"])
        crawl = esc(e["crawl_date"])
        tc = e["thread_count"]
        pc = e["post_count"]
        href = esc(e["board_html"])
        year_badge = f'<span class="ybadge">{year}</span>' if year else ""
        cards_html.append(f"""
<a class="card" href="{href}">
  <div class="card-hdr">
    <div class="card-name">{name}</div>
    {year_badge}
  </div>
  <div class="card-meta">
    <span><span class="num">{tc:,}</span> threads</span>
    <span><span class="num">{pc:,}</span> posts</span>
  </div>
  <div class="card-crawl">Crawled {crawl}</div>
</a>""")

    total_boards = len(entries)
    total_threads = sum(e["thread_count"] for e in entries)
    total_posts = sum(e["post_count"] for e in entries)
    years = sorted({e["year"] for e in entries if e["year"]})
    year_opts = "\n".join(f'<option value="{y}">{y}</option>' for y in years)
    names_json = json.dumps([{"name": e["name"], "year": e["year"], "idx": i} for i, e in enumerate(entries)])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Your World — Nickelodeon Message Boards Archive</title>
<style>
{CSS_SHARED}
header {{
  background: linear-gradient(135deg,#1a0a2e 0%,#16213e 50%,#0d2137 100%);
  border-bottom: 2px solid var(--orange);
  padding: 2rem 2rem 1.5rem;
  position: sticky; top: 0; z-index: 100;
  box-shadow: 0 4px 30px rgba(255,107,0,.15);
}}
.hinner {{ max-width:1100px; margin:0 auto; display:flex; align-items:flex-end; gap:1.5rem; flex-wrap:wrap; }}
.logo h1 {{ font-size:1.75rem; font-weight:800; letter-spacing:-.5px; color:var(--orange); text-shadow:0 0 20px rgba(255,107,0,.4); }}
.logo p {{ font-size:.8rem; color:var(--muted); margin-top:.25rem; letter-spacing:.05em; text-transform:uppercase; }}
.hstats {{ margin-left:auto; display:flex; gap:1.25rem; }}
.spill {{ background:rgba(255,107,0,.12); border:1px solid rgba(255,107,0,.3); border-radius:999px; padding:.35rem .9rem; font-size:.78rem; color:var(--orange-light); white-space:nowrap; }}
.controls {{ max-width:1100px; margin:1.75rem auto 0; padding:0 2rem; display:flex; gap:.75rem; flex-wrap:wrap; align-items:center; }}
.swrap {{ flex:1; min-width:220px; position:relative; }}
.swrap svg {{ position:absolute; left:.75rem; top:50%; transform:translateY(-50%); color:var(--muted); pointer-events:none; }}
#q {{ width:100%; background:var(--surface2); border:1px solid var(--border); border-radius:8px; padding:.6rem .75rem .6rem 2.25rem; color:var(--text); font-size:.88rem; outline:none; transition:border-color .2s; }}
#q:focus {{ border-color:var(--orange); }}
#q::placeholder {{ color:var(--muted); }}
select {{ background:var(--surface2); border:1px solid var(--border); border-radius:8px; padding:.6rem .75rem; color:var(--text); font-size:.88rem; outline:none; cursor:pointer; }}
.clabel {{ font-size:.78rem; color:var(--muted); padding:.6rem 0; }}
main {{ max-width:1100px; margin:1.25rem auto 3rem; padding:0 2rem; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(300px,1fr)); gap:1rem; }}
.card {{ background:var(--surface); border:1px solid var(--border); border-radius:12px; padding:1.25rem 1.4rem; cursor:pointer; text-decoration:none; color:inherit; display:block; transition:border-color .18s, transform .15s, box-shadow .18s; position:relative; overflow:hidden; }}
.card::before {{ content:''; position:absolute; inset:0; background:linear-gradient(135deg,rgba(255,107,0,.05),transparent 60%); opacity:0; transition:opacity .2s; }}
.card:hover {{ border-color:var(--orange); transform:translateY(-2px); box-shadow:0 8px 25px rgba(255,107,0,.15); }}
.card:hover::before {{ opacity:1; }}
.card-hdr {{ display:flex; align-items:flex-start; justify-content:space-between; gap:.5rem; margin-bottom:.75rem; }}
.card-name {{ font-size:1rem; font-weight:700; line-height:1.3; }}
.ybadge {{ font-size:.7rem; font-weight:600; background:rgba(0,168,168,.15); color:var(--teal); border:1px solid rgba(0,168,168,.3); border-radius:4px; padding:.15rem .45rem; white-space:nowrap; flex-shrink:0; }}
.card-meta {{ display:flex; gap:.9rem; font-size:.78rem; color:var(--muted); flex-wrap:wrap; }}
.num {{ color:var(--orange-light); font-weight:600; }}
.card-crawl {{ font-size:.72rem; color:var(--muted); margin-top:.6rem; opacity:.7; }}
.hidden {{ display:none !important; }}
.empty {{ grid-column:1/-1; text-align:center; padding:4rem 1rem; color:var(--muted); }}
footer {{ text-align:center; padding:1.5rem; font-size:.75rem; color:var(--muted); border-top:1px solid var(--border); }}
</style>
</head>
<body>
<header>
  <div class="hinner">
    <div class="logo">
      <h1>Your World — Message Board Archive</h1>
      <p>Nickelodeon Blab &mdash; Archived Web Crawl</p>
    </div>
    <div class="hstats">
      <span class="spill">{total_boards} boards</span>
      <span class="spill">{total_threads:,} threads</span>
      <span class="spill">{total_posts:,} posts</span>
    </div>
  </div>
</header>

<div class="controls">
  <div class="swrap">
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
    <input id="q" type="text" placeholder="Search boards…" autocomplete="off" oninput="filt()">
  </div>
  <select id="sortSel" onchange="filt()">
    <option value="default">Sort: Default</option>
    <option value="name">Sort: Name A–Z</option>
    <option value="posts">Sort: Most Posts</option>
    <option value="threads">Sort: Most Threads</option>
  </select>
  <select id="yearSel" onchange="filt()">
    <option value="">All Years</option>
    {year_opts}
  </select>
  <span class="clabel" id="clabel">{total_boards} boards</span>
</div>

<main>
  <div class="grid" id="grid">
{''.join(cards_html)}
  </div>
</main>

<footer>Message board archive — scraped from Nickelodeon Blab via SolrWayback</footer>

<script>
const NAMES = {names_json};
const cards = Array.from(document.querySelectorAll('.card'));
const grid = document.getElementById('grid');

function filt() {{
  const q = document.getElementById('q').value.toLowerCase();
  const year = document.getElementById('yearSel').value;
  const sort = document.getElementById('sortSel').value;

  let visible = cards.map((c, i) => ({{ card: c, i, name: NAMES[i].name, year: NAMES[i].year }}));

  if (q) visible = visible.filter(o => o.name.toLowerCase().includes(q));
  if (year) visible = visible.filter(o => o.year === year);

  if (sort === 'name') visible.sort((a,b) => a.name.localeCompare(b.name));
  else if (sort === 'posts') visible.sort((a,b) => {{
    const pa = parseInt(a.card.querySelector('.card-meta').textContent.match(/[\d,]+/g)?.[1]?.replace(/,/g,'') || 0);
    const pb = parseInt(b.card.querySelector('.card-meta').textContent.match(/[\d,]+/g)?.[1]?.replace(/,/g,'') || 0);
    return pb - pa;
  }});
  else if (sort === 'threads') visible.sort((a,b) => {{
    const ta = parseInt(a.card.querySelector('.card-meta').textContent.match(/[\d,]+/g)?.[0]?.replace(/,/g,'') || 0);
    const tb = parseInt(b.card.querySelector('.card-meta').textContent.match(/[\d,]+/g)?.[0]?.replace(/,/g,'') || 0);
    return tb - ta;
  }});

  const visSet = new Set(visible.map(o => o.i));
  cards.forEach((c, i) => c.classList.toggle('hidden', !visSet.has(i)));

  // reorder DOM
  visible.forEach(o => grid.appendChild(o.card));
  cards.filter((c,i) => !visSet.has(i)).forEach(c => grid.appendChild(c));

  document.getElementById('clabel').textContent = visible.length + ' board' + (visible.length !== 1 ? 's' : '');
}}
</script>
</body>
</html>"""


# ── Main generation ──────────────────────────────────────────────────────────

json_files = sorted(f for f in os.listdir(FOLDER) if f.endswith(".json") and f != "manifest.json")

entries = []
for filename in json_files:
    with open(FOLDER / filename) as fp:
        data = json.load(fp)
    board = data[0]
    threads = board.get("threads", [])
    total_posts = sum(len(t.get("posts", [])) for t in threads)

    parts = filename.replace(".json", "").split("_")
    name = board_name_from_file(filename)
    year = parts[1].replace("y-", "") if parts[1].startswith("y-") else ""
    crawl = parts[3].replace("crawl-", "") if len(parts) > 3 else ""
    crawl_fmt = format_crawl(crawl)

    board_html_name = filename.replace(".json", ".html")
    board_html_path = BOARDS_DIR / board_html_name

    print(f"  → {board_html_name} ({len(threads)} threads, {total_posts} posts)")
    html = render_board_html(filename, board, name)
    with open(board_html_path, "w") as fp:
        fp.write(html)

    entries.append({
        "file": filename,
        "name": name,
        "year": year,
        "crawl_date": crawl_fmt,
        "thread_count": len(threads),
        "post_count": total_posts,
        "board_link": board.get("board_link", ""),
        "board_html": f"boards/{board_html_name}",
    })

print(f"\nGenerating index.html…")
with open(OUT_DIR / "index.html", "w") as fp:
    fp.write(generate_index(entries))

print(f"Done. Generated {len(entries)} board pages + index.html")
