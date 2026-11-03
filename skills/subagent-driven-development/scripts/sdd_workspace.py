# -*- coding: utf-8 -*-
"""解析并确保某个 plan 的工作区目录，打印其绝对路径。

原脚本：skills/subagent-driven-development/scripts/sdd-workspace
用法：
    python scripts/sdd_workspace.py PLAN_FILE
"""
import sys

from _sdd_common import die, workspace

if len(sys.argv) != 2:
    die("usage: sdd-workspace PLAN_FILE")

print(workspace(sys.argv[1]))
