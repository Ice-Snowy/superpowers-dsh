# -*- coding: utf-8 -*-
"""SDD 工作区定位的共享实现（superpowers 的 bash 脚本的 DSH/Python 等价版）。

对应原脚本：skills/subagent-driven-development/scripts/sdd-workspace
逻辑逐条对照原 bash，不改变行为：
  - 每个 plan 一个工作区目录：<repo>/.superpowers/sdd/<plan-basename>/
  - 用 plan-path 标记文件记录归属，避免同名 plan 互相覆盖
  - 归属冲突时依次加 -<父目录名>、-<父目录名>-<n> 后缀
  - <repo>/.superpowers/sdd/.gitignore 内容为 "*"（只在缺失时创建）
"""
import os
import subprocess
import sys


def die(msg, code=2):
    sys.stderr.write(msg + "\n")
    sys.exit(code)


def run(cmd, cwd=None):
    return subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )


def git_toplevel():
    r = run(["git", "rev-parse", "--show-toplevel"])
    if r.returncode != 0:
        die("not inside a git work tree: %s" % (r.stderr.strip() or r.stdout.strip()))
    return os.path.realpath(r.stdout.strip())


def workspace(plan):
    """返回（并确保）该 plan 的工作区绝对路径。"""
    if not os.path.isfile(plan):
        die("no such plan file: %s" % plan)

    slug = os.path.basename(plan)
    if slug.lower().endswith(".md"):
        slug = slug[:-3]
    if not slug or slug in (".", ".."):
        die("cannot derive a workspace name from: %s" % plan)

    root = git_toplevel()
    base = os.path.join(root, ".superpowers", "sdd")

    # plan 的物理路径，用于生成归属标记：在仓库内用相对路径，否则用绝对路径
    plan_dir = os.path.realpath(os.path.dirname(os.path.abspath(plan)))
    plan_abs = os.path.join(plan_dir, os.path.basename(plan))
    if plan_abs.startswith(root + os.sep):
        plan_id = os.path.relpath(plan_abs, root)
    else:
        plan_id = plan_abs

    def owns(d):
        """该目录属于本 plan 则返回 True；新建目录则写入标记后返回 True。"""
        marker = os.path.join(d, "plan-path")
        if os.path.exists(marker):
            with open(marker, encoding="utf-8-sig") as f:
                return f.read().strip() == plan_id
        os.makedirs(d, exist_ok=True)
        with open(marker, "w", encoding="utf-8", newline="\n") as f:
            f.write(plan_id + "\n")
        return True

    d = os.path.join(base, slug)
    if not owns(d):
        parent = os.path.basename(plan_dir)
        d = os.path.join(base, "%s-%s" % (slug, parent))
        if not owns(d):
            n = 2
            while not owns(os.path.join(base, "%s-%s-%d" % (slug, parent, n))):
                n += 1
            d = os.path.join(base, "%s-%s-%d" % (slug, parent, n))

    # 只创建、不覆盖：仓库可能自己提交了这里的 .gitignore
    gi = os.path.join(base, ".gitignore")
    if not os.path.exists(gi):
        os.makedirs(base, exist_ok=True)
        with open(gi, "w", encoding="utf-8", newline="\n") as f:
            f.write("*\n")

    return os.path.realpath(d)
