#!/usr/bin/env python3
from server import build_topics
import json
from pathlib import Path

ROOT = Path(__file__).parent

topics = build_topics()
topics_data = json.dumps(topics, ensure_ascii=False)

solved_path = ROOT / 'progress.json'
solved_data = solved_path.read_text(encoding='utf-8') if solved_path.exists() else '{}'

template = (ROOT / 'index.html').read_text(encoding='utf-8')
injection = (f'<script>window.__TOPICS__ = {topics_data};\n'
             f'window.__SOLVED__ = {solved_data};</script>\n')
dist = template.replace('</body>', injection + '</body>')
(ROOT / 'dist.html').write_text(dist, encoding='utf-8')
print(f'dist.html written — {len(topics)} topics')
