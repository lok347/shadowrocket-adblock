#!/usr/bin/env python3
"""Review additive domain-filter changes without changing the stable module.

Standard-library only. Fail closed if pinned upstream sources cannot be verified.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
TIMEZONE = ZoneInfo("Asia/Shanghai")
EPOCH = dt.date(2026, 10, 21)
SOURCE_CONFIG = {
    "easylist_china": {"repository": "easylist/easylistchina", "path": "easylistchina.txt"},
    "awa": {"repository": "TG-Twilight/AWAvenue-Ads-Rule", "path": "Filters/AWAvenue-Ads-Rule-Surge-RULE-SET.list"},
    "easylist": {"repository": "easylist/easylist", "path": "easylist/easylist_adservers.txt"},
}
DOMAIN = re.compile(r"^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$", re.I)
UNCONDITIONAL = re.compile(r"^\|\|([a-z0-9.-]+)\^$", re.I)
EXCEPTION = re.compile(r"^@@\|\|([a-z0-9.-]+)(?:\^|/|\$|$)", re.I)
RULE = re.compile(r"^(DOMAIN|DOMAIN-SUFFIX|DOMAIN-KEYWORD),([^,]+),(DIRECT|REJECT)(?:,.*)?$", re.I)


def valid_domain(value: str) -> bool:
    return bool(DOMAIN.fullmatch(value) and "." in value and all(0 < len(p) <= 63 and not p.startswith("-") and not p.endswith("-") for p in value.split(".")))


def parse_domains(text: str) -> set[str]:
    return {m.group(1).lower() for line in text.splitlines() if (m := UNCONDITIONAL.fullmatch(line.strip())) and valid_domain(m.group(1))}


def parse_exceptions(text: str) -> set[str]:
    return {m.group(1).lower() for line in text.splitlines() if (m := EXCEPTION.match(line.strip())) and valid_domain(m.group(1))}


def parse_static(text: str, action: str) -> set[tuple[str, str]]:
    output = set()
    for line in text.splitlines():
        if m := RULE.fullmatch(line.strip()):
            if m.group(3).upper() == action and (m.group(1).upper() == "DOMAIN-KEYWORD" or valid_domain(m.group(2))):
                output.add((m.group(1).upper(), m.group(2).lower()))
    return output


def parse_awa(text: str) -> set[tuple[str, str]]:
    entries: set[tuple[str, str]] = set()
    for line in text.splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 2:
            continue
        kind = parts[0].upper()
        value = parts[1].lower()
        if kind in ("DOMAIN", "DOMAIN-SUFFIX") and valid_domain(value):
            entries.add((kind, value))
        elif kind == "DOMAIN-KEYWORD" and value:
            entries.add((kind, value))
    return entries


def is_covered(domain: str, rule: tuple[str, str]) -> bool:
    kind, target = rule
    if kind == "DOMAIN":
        return domain == target
    if kind == "DOMAIN-SUFFIX":
        return domain == target or domain.endswith("." + target)
    if kind == "DOMAIN-KEYWORD":
        return target in domain
    return False


def is_guard_conflict(domain: str, rule: tuple[str, str]) -> bool:
    kind, target = rule
    return is_covered(domain, rule) or (kind != "DOMAIN-KEYWORD" and (target == domain or target.endswith("." + domain)))


def exception_conflicts(domain: str, exceptions: set[str]) -> list[str]:
    return sorted(e for e in exceptions if domain == e or domain.endswith("." + e) or e.endswith("." + domain))


def next_due(day: dt.date) -> bool:
    return day >= EPOCH and (day - EPOCH).days % 14 == 0


def http_read(url: str, accept: str = "text/plain") -> str:
    headers = {"User-Agent": "lok347-shadowrocket-adblock-review", "Accept": accept}
    if os.getenv("GITHUB_TOKEN") and url.startswith(("https://api.github.com/", "https://raw.githubusercontent.com/")):
        headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
    last_error = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=25) as response:
                return response.read().decode("utf-8")
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, UnicodeError) as error:
            last_error = error
            if isinstance(error, urllib.error.HTTPError) and error.code not in (429, 500, 502, 503, 504):
                break
            if attempt < 2:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"Cannot verify upstream {url}: {last_error}") from last_error


def github_api(path: str) -> dict:
    return json.loads(http_read("https://api.github.com" + path, accept="application/vnd.github+json"))


def git_blob_sha(text: str) -> str:
    data = text.encode("utf-8")
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def source_at_commit(repo: str, commit: str, path: str) -> str:
    safe_path = "/".join(urllib.parse.quote(p, safe="") for p in path.split("/"))
    return http_read(f"https://raw.githubusercontent.com/{repo}/{commit}/{safe_path}")


def snapshot(key: str) -> dict:
    c = SOURCE_CONFIG[key]
    repo, path = c["repository"], c["path"]
    meta = github_api("/repos/" + repo)
    branch = meta["default_branch"]
    commit = github_api("/repos/" + repo + "/commits/" + urllib.parse.quote(branch))["sha"]
    contents = github_api("/repos/" + repo + "/contents/" + path + "?ref=" + commit)
    blob_sha = contents["sha"]
    text = source_at_commit(repo, commit, path)
    if git_blob_sha(text) != blob_sha:
        raise RuntimeError(f"Unverifiable source blob for {key}; refusing to publish review")
    return {"repository": repo, "path": path, "commit": commit, "blob_sha": blob_sha, "text": text}


def review_base(root: Path) -> tuple[Path, dict]:
    reviews = sorted((root / "docs" / "reviews").glob("*.json"), reverse=True)
    for path in reviews:
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("sources", {}).get("easylist_china", {}).get("head_commit"):
            return path, data
    raise RuntimeError("No pinned EasyList China review baseline; manual initialization required")


def summarize(root: Path, date: str, latest: dict, base_path: Path, base: dict) -> tuple[dict, str, str]:
    c = SOURCE_CONFIG["easylist_china"]
    prior = base["sources"]["easylist_china"]["head_commit"]
    old_text = source_at_commit(c["repository"], prior, c["path"])
    old = parse_domains(old_text)
    new = parse_domains(latest["easylist_china"]["text"])
    if not old or not new:
        raise RuntimeError("Parsed empty baseline or current domain set; review stopped")
    raw_added = sorted(new - old)
    removed = sorted(old - new)
    local_module = (root / "Shadowrocket-AdBlock.sgmodule").read_text(encoding="utf-8")
    guarded = parse_static(local_module, "DIRECT")
    rejected = parse_static(local_module, "REJECT")
    awa = parse_awa(latest["awa"]["text"])
    generic = parse_domains(latest["easylist"]["text"])
    exceptions = parse_exceptions(latest["easylist_china"]["text"]) | parse_exceptions(latest["easylist"]["text"])
    candidates = []
    counts = {"upstream_added": len(raw_added), "upstream_removed": len(removed), "ready_for_review": 0, "already_covered_locally": 0, "covered_by_awa": 0, "guard_conflicts": 0, "source_exception_conflicts": 0}
    for domain in raw_added:
        guards = sorted(f"{k},{v}" for k, v in guarded if is_guard_conflict(domain, (k, v)))
        source_exceptions = exception_conflicts(domain, exceptions)
        item = {"domain": domain, "source": "easylist_china", "rule_type": "DOMAIN-SUFFIX", "also_listed_by_easylist": domain in generic, "guard_conflicts": guards, "source_exception_conflicts": source_exceptions}
        if guards:
            item["decision"] = "hold_direct_conflict"
            counts["guard_conflicts"] += 1
        elif source_exceptions:
            item["decision"] = "hold_exception_conflict"
            counts["source_exception_conflicts"] += 1
        elif any(is_covered(domain, rule) for rule in rejected):
            item["decision"] = "skip_local_coverage"
            counts["already_covered_locally"] += 1
        elif any(is_covered(domain, rule) for rule in awa):
            item["decision"] = "skip_awa_coverage"
            counts["covered_by_awa"] += 1
        else:
            item["decision"] = "candidate_only_unverified"
            counts["ready_for_review"] += 1
        candidates.append(item)
    currently_rejected = sorted(d for d in removed if any(is_covered(d, r) for r in rejected))
    previous_awa_commit = base.get("sources", {}).get("awa", {}).get("commit")
    awa_removed = []
    if previous_awa_commit:
        old_awa = parse_awa(source_at_commit(SOURCE_CONFIG["awa"]["repository"], previous_awa_commit, SOURCE_CONFIG["awa"]["path"]))
        awa_removed = sorted(f"{k},{v}" for k, v in old_awa - awa)
    newly_added_exceptions = sorted(parse_exceptions(latest["easylist_china"]["text"]) - parse_exceptions(old_text))
    impacting_exceptions = sorted(e for e in newly_added_exceptions if any(is_covered(e, rule) or is_guard_conflict(e, rule) for rule in rejected))
    sources = {key: {"repository": src["repository"], "path": src["path"], "head_commit": src["commit"], "blob_sha": src["blob_sha"]} for key, src in latest.items()}
    sources["easylist_china"]["base_commit"] = prior
    sources["easylist_china"]["license"] = "GPL-3.0-or-later (https://easylist.to/pages/licence.html)"
    record = {"schema_version": 2, "review_date": date, "status": "review_only_unpublished", "baseline_review": base_path.name, "sources": sources, "counts": counts, "upstream_removed_domains": removed, "removed_still_rejected_locally": currently_rejected, "awa_removed_rules": awa_removed, "new_easylist_china_exceptions": newly_added_exceptions, "new_exceptions_affecting_local_reject": impacting_exceptions, "candidates": candidates, "limitations": ["No iOS/Shadowrocket device verification was performed.", "Community lists are candidate evidence, not proof of exclusive advertising use.", "No stable module, script, MITM or Rewrite changes were made.", "AWAvenue is currently referenced dynamically by the stable module; this review does not pin it."]}
    good = [i["domain"] for i in candidates if i["decision"] == "candidate_only_unverified"]
    rule_text = "# Reviewed candidates only; NOT imported into stable module.\n# Review date: " + date + "\n# Source: EasyList China\n# All entries require human approval before stable release.\n" + "\n".join("DOMAIN-SUFFIX," + name for name in good) + ("\n" if good else "")
    def display(items: list, max_items: int = 25) -> str:
        if not items:
            return "无"
        result = ", ".join(f"`{v}`" for v in items[:max_items])
        if len(items) > max_items:
            result += f" ……（其余 {len(items) - max_items} 条详见 JSON）"
        return result
    md = f"""# Shadowrocket AdBlock 双周审查 — {date}

**状态：仅审查，未发布稳定版。** 本报告由 GitHub Actions 的确定性增量检查器生成，未执行 iPhone 实测。

- 上期基线：`{base_path.name}`；EasyList China 固定基线 `{prior}`。
- 本期 EasyList China commit：`{latest['easylist_china']['commit']}`；blob：`{latest['easylist_china']['blob_sha']}`。
- 其余来源的 Commit / Blob SHA 见同名 JSON。
- 来源版权：EasyList China / The EasyList authors，GPL-3.0-or-later；https://easylist.to/pages/licence.html。

## 增量结果

| 检查项 | 数量 |
| --- | ---: |
| 无条件域名新增（来源差集） | {counts['upstream_added']} |
| 来源删除的无条件域名 | {counts['upstream_removed']} |
| 候选待人工审核（未发布） | {counts['ready_for_review']} |
| 本地 REJECT 已覆盖 | {counts['already_covered_locally']} |
| AWAvenue 规则集已覆盖 | {counts['covered_by_awa']} |
| DIRECT guard 冲突，保留待核验 | {counts['guard_conflicts']} |
| 上游例外规则冲突，保留待核验 | {counts['source_exception_conflicts']} |

## 撤回、误杀与风险观察

- 来源已删除但本地仍拦截：{display(currently_rejected)}
- AWAvenue 删除的规则：{display(awa_removed)}
- 新增 EasyList China 例外且可能触及本地静态 REJECT：{display(impacting_exceptions)}
- **这些撤回/例外都需要审核；系统不会自动删除或新增稳定版规则。**

## 发布边界

- 本次只生成 `rules/candidates/{date}.list` 和结构化审查记录。
- 未修改 `Shadowrocket-AdBlock.sgmodule`、日期归档、DIRECT、Rewrite、MITM 或 Cleaner。
- 来源命中和冲突检查不代表 App 实机兼容；请审核后手动决定是否发布。
"""
    return record, rule_text, md


def validate(root: Path) -> None:
    fixed = (root / "Shadowrocket-AdBlock.sgmodule").read_bytes()
    name = re.search(rb"^#!name=AdBlock_lok\.(\d{8})\s*$", fixed, re.M)
    if name is None:
        raise AssertionError("Stable module version marker missing")
    archive = root / ("Shadowrocket-AdBlock-lok." + name.group(1).decode() + ".sgmodule")
    if archive.read_bytes() != fixed:
        raise AssertionError("Stable subscription and dated module are not identical")
    url = "https://raw.githubusercontent.com/lok347/shadowrocket-adblock/main/Shadowrocket-AdBlock.sgmodule"
    readme = (root / "README.md").read_text(encoding="utf-8")
    if url not in readme:
        raise AssertionError("Fixed subscription URL missing from README")
    import plistlib
    plist = plistlib.loads((root / "shortcuts/AdBlock-lok-update.plist").read_bytes())
    expected = "shadowrocket://install?module=" + urllib.parse.quote(url, safe="")
    actions = plist.get("WFWorkflowActions", [])
    if expected not in [a.get("WFWorkflowActionParameters", {}).get("WFInput") for a in actions]:
        raise AssertionError("Shortcut no longer uses the stable subscription")
    if b"/main/scripts/adblock-clean.js" not in fixed:
        raise AssertionError("Stable module cleaner reference changed")
    print("PASS: fixed module/dated archive, README, shortcut and cleaner references")


def scan(root: Path, date: str, dry_run: bool) -> None:
    date_obj = dt.date.fromisoformat(date)
    if date_obj > dt.datetime.now(TIMEZONE).date():
        raise ValueError("Cannot claim a future review date")
    validate(root)
    base_path, baseline = review_base(root)
    latest = {key: snapshot(key) for key in SOURCE_CONFIG}
    record, rules, markdown = summarize(root, date, latest, base_path, baseline)
    if dry_run:
        print("DRY-RUN: no repository files will be changed")
        print(markdown)
    else:
        for path, value in {
            root / "docs/reviews" / f"{date}.json": json.dumps(record, indent=2, ensure_ascii=False) + "\n",
            root / "docs/reviews" / f"{date}.md": markdown,
            root / "rules/candidates" / f"{date}.list": rules,
        }.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(value, encoding="utf-8")
            print("Created", path.relative_to(root))
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write(markdown + "\n")
    print("SUMMARY " + json.dumps(record["counts"], ensure_ascii=False))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=["validate", "scan", "due"])
    p.add_argument("--date", default=dt.datetime.now(TIMEZONE).date().isoformat())
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--root", type=Path, default=ROOT)
    args = p.parse_args()
    if args.command == "validate":
        validate(args.root)
    elif args.command == "due":
        day = dt.date.fromisoformat(args.date)
        print("due" if next_due(day) else "not due")
    else:
        scan(args.root, args.date, args.dry_run)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, ValueError, KeyError, AssertionError, OSError) as exc:
        print(f"Review failed closed: {exc}", file=sys.stderr)
        sys.exit(1)
