# -*- coding: utf-8 -*-
"""开始一个任务：取任务简报并记录 BASE 提交。

原脚本：skills/executing-plans/scripts/task-start
用法：
    python scripts/task_start.py PLAN_FILE TASK_NUMBER
输出：
    brief: <任务简报文件路径>
    base:  <HEAD 的完整 SHA>
"""
import os
import re
import subprocess
import sys

from _sdd_common import die, run

if len(sys.argv) != 3:
    die("usage: task-start PLAN_FILE TASK_NUMBER")

plan = sys.argv[1]
n = sys.argv[2]

here = os.path.dirname(os.path.abspath(__file__))
sdd = os.path.normpath(os.path.join(here, "..", "..", "subagent-driven-development", "scripts"))
brief_script = os.path.join(sdd, "task_brief.py")

r = subprocess.run(
    [sys.executable, brief_script, plan, n],
    capture_output=True, text=True, encoding="utf-8", errors="replace",
)
if r.returncode != 0:
    sys.stderr.write((r.stderr or r.stdout).strip() + "\n")
    sys.exit(r.returncode)

m = re.search(r"^wrote (.*): ([0-9]+) lines$", r.stdout, re.M)
if not m:
    die("task-brief did not report a path: %s" % r.stdout.strip(), 1)
brief = m.group(1)

g = run(["git", "rev-parse", "HEAD"])
if g.returncode != 0:
    die("git rev-parse HEAD failed: %s" % g.stderr.strip(), 1)

print("brief: " + brief)
print("base: " + g.stdout.strip())
