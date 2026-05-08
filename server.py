#!/usr/bin/env python3
import json
import mimetypes
import os
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).parent
PROBLEMS_DIR = ROOT / 'problems'


def parse_md(path: Path) -> list[dict]:
    text = path.read_text(encoding='utf-8')
    # Split on lines that start a new numbered item
    parts = re.split(r'\n(?=\d+\. )', '\n' + text.strip())
    problems = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        m = re.match(r'^\d+\.\s+(.+)', part, re.DOTALL)
        if not m:
            continue
        body = m.group(1).strip()
        if re.match(r'^https?://\S+$', body):
            problems.append({'index': len(problems), 'url': body, 'content': None})
        else:
            problems.append({'index': len(problems), 'url': None, 'content': body})
    return problems


def build_topics() -> list[dict]:
    topics = []
    for md_path in sorted(PROBLEMS_DIR.rglob('*.md')):
        rel = md_path.relative_to(PROBLEMS_DIR)
        topic_id = str(rel.with_suffix(''))
        problems = parse_md(md_path)
        if problems:
            topics.append({'id': topic_id, 'name': md_path.stem, 'problems': problems})
    return topics


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # silence access logs

    def do_GET(self):
        if self.path == '/api/problems':
            data = json.dumps({'topics': build_topics()}, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', len(data))
            self.end_headers()
            self.wfile.write(data)
            return

        url_path = self.path.split('?')[0]
        if url_path == '/':
            url_path = '/index.html'
        file_path = ROOT / url_path.lstrip('/')
        if not file_path.is_file():
            self.send_response(404)
            self.end_headers()
            return

        mime, _ = mimetypes.guess_type(str(file_path))
        data = file_path.read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', mime or 'application/octet-stream')
        self.send_header('Content-Length', len(data))
        self.end_headers()
        self.wfile.write(data)


if __name__ == '__main__':
    server = HTTPServer(('localhost', 8080), Handler)
    print('http://localhost:8080')
    server.serve_forever()
