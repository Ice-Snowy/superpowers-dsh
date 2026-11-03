# -*- coding: utf-8 -*-
"""把实施计划里某个任务的完整正文抽到一个文件里，供实现者一次读完。

原脚本：skills/subagent-driven-development/scripts/task-brief
用法：
    python scripts/task_brief.py PLAN_FILE TASK_NUMBER [OUTFILE]
默认 OUTFILE：<工作区>/task-<N>-brief.md

等价性说明：原脚本用 awk 按行扫描，遇到 ``` 切换围栏状态；非围栏状态下遇到
"#+ Task N" 形式的标题开始收录，遇到其它 Task 标题停止。此处逐行同构实现。
"""
import os
import re
import sys

from _sdd_common import die, workspace

if len(sys.argv) < 3 or len(sys.argv) > 4:
    die("usage: task-brief PLAN_FILE TASK_NUMBER [OUTFILE]")

plan = sys.argv[1]
n = sys.argv[2]

if not os.path.isfile(plan):
    die("no such plan file: %s" % plan)

if len(sys.argv) == 4:
    out = sys.argv[3]
else:
    out = os.path.join(workspace(plan), "task-%s-brief.md" % n)

with open(plan, encoding="utf-8-sig") as f:
    lines = f.read().splitlines()

ANNOUNCE = re.compile(r"^#+[ \t]+Task[ \t]+[0-9]+")
WANT = re.compile(r"^#+[ \t]+Task[ \t]+" + re.escape(n) + r"([^0-9]|$)")

in_fence = False
in_task = False
kept = []
for line in lines:
    if line.startswith("```"):
        in_fence = not in_fence
    if not in_fence and ANNOUNCE.match(line):
        in_task = bool(WANT.match(line))
    if in_task:
        kept.append(line)

if not kept:
    die("task %s not found in %s (no heading matching 'Task %s')" % (n, plan, n), 3)

out_dir = os.path.dirname(os.path.abspath(out))
if out_dir:
    os.makedirs(out_dir, exist_ok=True)
with open(out, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(kept) + "\n")

print("wrote %s: %d lines" % (out, len(kept)))
