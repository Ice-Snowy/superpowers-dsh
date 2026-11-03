# -*- coding: utf-8 -*-
"""生成评审包：提交列表、改动统计、带扩展上下文的净 diff，写到一个文件。

原脚本：skills/subagent-driven-development/scripts/review-package
用法：
    python scripts/review_package.py PLAN_FILE BASE HEAD [OUTFILE]
默认 OUTFILE：<工作区>/review-<base7>..<head7>.diff
退出码 3 表示范围有问题（HEAD 不是 BASE 的后代，或范围为空）。
"""
import os
import sys

from _sdd_common import die, run, workspace

if len(sys.argv) < 4 or len(sys.argv) > 5:
    die("usage: review-package PLAN_FILE BASE HEAD [OUTFILE]")

plan = sys.argv[1]
base = sys.argv[2]
head = sys.argv[3]

if not os.path.isfile(plan):
    die("no such plan file: %s" % plan)

if run(["git", "rev-parse", "--verify", "--quiet", base]).returncode != 0:
    die("bad BASE: %s" % base, 2)
if run(["git", "rev-parse", "--verify", "--quiet", head]).returncode != 0:
    die("bad HEAD: %s" % head, 2)

rng = "%s..%s" % (base, head)

if run(["git", "merge-base", "--is-ancestor", base, head]).returncode != 0:
    die("HEAD is not a descendant of BASE: %s" % rng, 3)

count_raw = run(["git", "rev-list", "--count", rng]).stdout.strip()
try:
    commits = int(count_raw)
except ValueError:
    die("cannot count commits in %s" % rng, 2)
if commits <= 0:
    die("empty commit range: %s" % rng, 3)

if len(sys.argv) == 5:
    out = sys.argv[4]
else:
    b7 = run(["git", "rev-parse", "--short", base]).stdout.strip()
    h7 = run(["git", "rev-parse", "--short", head]).stdout.strip()
    out = os.path.join(workspace(plan), "review-%s..%s.diff" % (b7, h7))

log_txt = run(["git", "log", "--oneline", rng]).stdout.rstrip("\n")
stat_txt = run(["git", "diff", "--stat", rng]).stdout.rstrip("\n")
diff_txt = run(["git", "diff", "-U10", rng]).stdout.rstrip("\n")

content = (
    "# Review package: %s\n\n" % rng
    + "## Commits\n" + log_txt + "\n\n"
    + "## Files changed\n" + stat_txt + "\n\n"
    + "## Diff\n" + diff_txt + "\n"
)

out_dir = os.path.dirname(os.path.abspath(out))
if out_dir:
    os.makedirs(out_dir, exist_ok=True)
with open(out, "w", encoding="utf-8", newline="\n") as f:
    f.write(content)

print("wrote %s: %d commit(s), %d bytes" % (out, commits, os.path.getsize(out)))
