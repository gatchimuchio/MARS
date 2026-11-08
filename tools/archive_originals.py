#!/usr/bin/env python3
"""公開されているMARS原典を、そのままローカルに取得し同一性を記録する。

本ツールは第三者資料をGitHubにアップロードしない。原典ファイルは
sources/_local_originals/objects/、取得メタデータはsources/originals.lock.jsonへ。
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import re
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
REGISTER = ROOT / "docs" / "SOURCE_REGISTER.md"
ARCHIVE = ROOT / "sources" / "_local_originals"
OBJECTS = ARCHIVE / "objects"
LOCK = ROOT / "sources" / "originals.lock.json"
SOURCE_RE = re.compile(r"^\| (S\d\d) \| \[([^\]]+)\]\((https://[^)]+)\)", re.M)
MAX_BYTES = 64 * 1024 * 1024
ALLOWED_HOSTS = frozenset({
    "www.hitachihyoron.com", "www.jstage.jst.go.jp", "museum.ipsj.or.jp",
    "www.jrs.co.jp", "www.cobol.gr.jp", "www.hitachi.co.jp",
    "ethw-images.s3.us-east-va.perf.cloud.ovh.us", "www.rtri.or.jp",
    "ethw.org", "www.kahaku.go.jp",
})


@dataclass(frozen=True)
class Source:
    identifier: str
    title: str
    url: str


def read_catalog(text: str) -> dict[str, Source]:
    sources = {}
    for identifier, title, url in SOURCE_RE.findall(text):
        require_official_url(url)
        if identifier in sources:
            raise ValueError(f"資料ID重複: {identifier}")
        sources[identifier] = Source(identifier, title, url)
    if not sources:
        raise ValueError("資料登録簿に公開原典Sxxが存在しない")
    return sources


def require_official_url(url: str) -> None:
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
        raise ValueError(f"未承認の参照先: {url}")
    if parsed.username or parsed.password or parsed.port not in (None, 443):
        raise ValueError(f"想定外のURL権限・ポート: {url}")


def load_lock() -> dict:
    if not LOCK.exists():
        return {"schema_version": 1, "sources": {}}
    loaded = json.loads(LOCK.read_text(encoding="utf-8"))
    if loaded.get("schema_version") != 1 or not isinstance(loaded.get("sources"), dict):
        raise ValueError("原典ハッシュ台帳の形式が不正")
    return loaded


def atomic_json(path: Path, document: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".write-", delete=False) as temporary:
        temp_path = Path(temporary.name)
        temporary.write(raw)
        temporary.flush()
        os.fsync(temporary.fileno())
    os.replace(temp_path, path)


def archive_one(source: Source, timeout: int) -> dict:
    OBJECTS.mkdir(parents=True, exist_ok=True)
    request = Request(source.url, headers={"User-Agent": "MARS-independent-source-audit/1.0", "Accept": "application/pdf,text/html,*/*"})
    with urlopen(request, timeout=timeout) as response:
        require_official_url(response.geturl())
        content_type = response.headers.get_content_type()
        if content_type == "application/pdf" or urlsplit(response.geturl()).path.lower().endswith(".pdf"):
            extension = ".pdf"
        elif content_type in ("text/html", "application/xhtml+xml"):
            extension = ".html"
        else:
            raise ValueError(f"予期しないメディア種別: {source.identifier} ({content_type})")
        if int(response.headers.get("Content-Length", "0")) > MAX_BYTES:
            raise ValueError(f"ファイルが上限を超える: {source.identifier}")
        with tempfile.NamedTemporaryFile(dir=OBJECTS, prefix=".fetch-", delete=False) as temporary:
            temp_path = Path(temporary.name)
            digest = hashlib.sha256()
            size = 0
            prefix = b""
            try:
                while chunk := response.read(1024 * 1024):
                    size += len(chunk)
                    if size > MAX_BYTES:
                        raise ValueError(f"ファイルが上限を超える: {source.identifier}")
                    if len(prefix) < 8:
                        prefix += chunk[:8]
                    digest.update(chunk)
                    temporary.write(chunk)
                if extension == ".pdf" and not prefix.startswith(b"%PDF-"):
                    raise ValueError(f"PDFではない応答: {source.identifier}")
                if size == 0:
                    raise ValueError(f"空のファイル: {source.identifier}")
            except BaseException:
                temp_path.unlink(missing_ok=True)
                raise
    sha = digest.hexdigest()
    relative = f"objects/{sha}{extension}"
    target = ARCHIVE / relative
    if target.exists():
        if hashlib.sha256(target.read_bytes()).hexdigest() != sha:
            temp_path.unlink(missing_ok=True)
            raise ValueError(f"既存の同名原典が破損: {target}")
        temp_path.unlink(missing_ok=True)
    else:
        os.replace(temp_path, target)
    return {
        "sha256": sha,
        "bytes": size,
        "media_type": content_type,
        "local_object": relative,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "final_url": response.geturl(),
    }


def fetch(catalog: dict[str, Source], identifiers: list[str], timeout: int, workers: int) -> int:
    record = load_lock()
    errors = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(archive_one, catalog[identifier], timeout): identifier for identifier in identifiers}
        for future in concurrent.futures.as_completed(futures):
            identifier = futures[future]
            source = catalog[identifier]
            try:
                capture = future.result()
            except Exception as exc:
                print(f"FAILED {identifier}: {type(exc).__name__}: {exc}", flush=True)
                errors.append(identifier)
                continue
            entry = record["sources"].setdefault(identifier, {"title": source.title, "url": source.url, "captures": []})
            if entry["url"] != source.url:
                print(f"FAILED {identifier}: 参照先が以前の保存記録から変更。手動監査が必要", flush=True)
                errors.append(identifier)
                continue
            if all(item["sha256"] != capture["sha256"] for item in entry["captures"]):
                if entry["captures"]:
                    print(f"CHANGED {identifier}: 旧版を保存したまま新版を追加", flush=True)
                entry["captures"].append(capture)
            print(f"OK {identifier} sha256={capture['sha256']} bytes={capture['bytes']}", flush=True)
    atomic_json(LOCK, record)
    print(f"完了: {len(identifiers) - len(errors)}/{len(identifiers)}。原典本体: {ARCHIVE} / ハッシュ台帳: {LOCK}")
    if errors:
        print("未取得: " + ", ".join(sorted(errors)))
    return 0 if not errors else 2


def verify(catalog: dict[str, Source]) -> int:
    record = load_lock()
    errors = 0
    checked = 0
    for identifier, entry in sorted(record["sources"].items()):
        if identifier not in catalog or entry["url"] != catalog[identifier].url:
            print(f"SOURCE-CHANGED {identifier}")
            errors += 1
            continue
        for capture in entry["captures"]:
            object_path = ARCHIVE / capture["local_object"]
            if object_path.parent != OBJECTS:
                print(f"INVALID-PATH {identifier}")
                errors += 1
                continue
            if not object_path.is_file():
                print(f"MISSING {identifier}: {object_path}")
                errors += 1
                continue
            digest = hashlib.sha256()
            with object_path.open("rb") as input_file:
                while chunk := input_file.read(1024 * 1024):
                    digest.update(chunk)
            if digest.hexdigest() != capture["sha256"] or object_path.stat().st_size != capture["bytes"]:
                print(f"CORRUPT {identifier}: {object_path}")
                errors += 1
            else:
                checked += 1
    print(f"ハッシュ一致: {checked}件 / 不一致・欠落: {errors}件")
    return 0 if not errors else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="原文PDF・HTMLの私的保存、SHA-256記録、突合")
    command = parser.add_subparsers(dest="command", required=True)
    command.add_parser("list", help="登録した原典を表示")
    fetch_parser = command.add_parser("fetch", help="原文を取得。版が異なる場合は両方を保持")
    fetch_parser.add_argument("--all", action="store_true", help="S01～登録済み全資料")
    fetch_parser.add_argument("--id", action="append", default=[], help="原典ID。複数指定可")
    fetch_parser.add_argument("--workers", type=int, default=3, choices=(1, 2, 3, 4))
    fetch_parser.add_argument("--timeout", type=int, default=30)
    command.add_parser("verify", help="原典の存在、サイズ、SHA-256を検証")
    args = parser.parse_args()
    catalog = read_catalog(REGISTER.read_text(encoding="utf-8"))
    if args.command == "list":
        for source in catalog.values():
            print(f"{source.identifier} | {source.title} | {source.url}")
        return 0
    if args.command == "verify":
        return verify(catalog)
    identifiers = sorted(catalog) if args.all else sorted(set(args.id))
    if not identifiers or any(identifier not in catalog for identifier in identifiers):
        parser.error("--allまたは既存の--id Sxxを指定")
    return fetch(catalog, identifiers, args.timeout, args.workers)


if __name__ == "__main__":
    raise SystemExit(main())
