# -*- coding: utf-8 -*-
"""结束一个任务：跑测试命令，保留完整输出，打印尾部，成功才写账本。

原脚本：skills/executing-plans/scripts/task-done
用法：
    python scripts/task_done.py PLAN_FILE TASK_NUMBER BASE -- TEST_COMMAND [ARGS...]
退出码 = 测试命令的退出码。失败时不记录，任务不算完成。
"""
import os
import re
import subprocess
import sys

from _sdd_common import die, run, workspace

if len(sys.argv) < 5 or sys.argv[4] != "--":
    die("usage: task-done PLAN_FILE TASK_NUMBER BASE -- TEST_COMMAND [ARGS...]")

plan = sys.argv[1]
n = sys.argv[2]
base = sys.argv[3]
cmd = sys.argv[5:]

v = run(["git", "rev-parse", "--verify", "--quiet", base])
if v.returncode != 0:
    die("bad BASE: %s" % base, 2)

d = workspace(plan)
log = os.path.join(d, "task-%s-tests.log" % n)
ledger = os.path.join(d, "progress.md")

# 按人敲命令的样子渲染，用于账本行
NEEDS_QUOTE = re.compile(r'[\s";|&]')
parts = []
for a in cmd:
    parts.append("'%s'" % a if NEEDS_QUOTE.search(a) else a)
shown = " ".join(parts)

# stdout 与 stderr 合并，等价于 bash 的 > log 2>&1
r = subprocess.run(
    cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    text=True, encoding="utf-8", errors="replace",
)
out = r.stdout or ""
with open(log, "w", encoding="utf-8", newline="\n") as f:
    f.write(out)

lines = out.splitlines()
for line in lines[-5:]:
    print(line)

if r.returncode != 0:
    sys.stderr.write(
        "task-done: test command exited %d; Task %s NOT recorded (full output: %s)\n"
        % (r.returncode, n, log)
    )
    sys.exit(r.returncode)

nonblank = [ln for ln in lines if ln.strip()]
last = nonblank[-1] if nonblank else "(no output)"

if not os.path.exists(ledger):
    with open(ledger, "w", encoding="utf-8", newline="\n") as f:
        f.write("# SDD ledger — plan: %s\n" % plan)

b7 = run(["git", "rev-parse", "--short=7", base]).stdout.strip()
h7 = run(["git", "rev-parse", "--short=7", "HEAD"]).stdout.strip()
line = "Task %s: complete (commits %s..%s, tests: %s → %s)" % (n, b7, h7, shown, last)
with open(ledger, "a", encoding="utf-8", newline="\n") as f:
    f.write(line + "\n")

print("ledger: " + line)
