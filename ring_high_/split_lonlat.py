#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
split_lonlat.py  ——  将 .lonlat 文件按段自动拆分
用法：
  python split_lonlat.py /mnt/d/data/4.1/G2.lonlat
  python split_lonlat.py "/mnt/d/data/4.1/*.lonlat"
  python split_lonlat.py /mnt/d/data/4.1 --glob "*.lonlat" --min-points 2
"""

import argparse, glob, os, sys
from pathlib import Path

def split_one_file(path: Path, min_points: int = 2) -> int:
    lines = path.read_text(encoding="utf-8").splitlines()

    segments = []
    cur = []
    for line in lines:
        if line.strip().startswith(">") or line.strip() == "":
            # 遇到新段的开始或空行：把当前段收集起来
            if cur:
                segments.append(cur)
                cur = []
            # 如果是头行 '>'，作为新段的第一行保存
            if line.strip().startswith(">"):
                cur = [line.rstrip()]
        else:
            if not cur:
                # 没有头行的段，自动补一行头
                cur = ["> segment"]
            cur.append(line.rstrip())

    if cur:
        segments.append(cur)

    # 写出
    written = 0
    for i, seg in enumerate(segments, 1):
        # 统计点数（不含头行）
        pts = [ln for ln in seg if not ln.strip().startswith(">") and ln.strip()]
        if len(pts) < min_points:
            continue
        out_path = path.with_name(f"{path.stem}_{i}{path.suffix}")
        out_path.write_text("\n".join(seg) + "\n", encoding="utf-8")
        written += 1
        print(f"✅ {path.name} -> {out_path.name}  ({len(pts)} points)")
    if written == 0:
        print(f"⚠️ {path.name} 没有满足条件的段（min_points={min_points}）")
    return written

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="单个文件、目录或带通配符的路径")
    ap.add_argument("--glob", default=None, help="当 target 是目录时使用的匹配模式，如 '*.lonlat'")
    ap.add_argument("--min-points", type=int, default=2, help="每段最少点数（默认2）")
    args = ap.parse_args()

    target = Path(args.target)
    files = []

    if any(ch in args.target for ch in "*?[]"):
        files = [Path(p) for p in glob.glob(args.target)]
    elif target.is_dir():
        pattern = args.glob or "*.lonlat"
        files = sorted(target.glob(pattern))
    elif target.is_file():
        files = [target]
    else:
        print("找不到目标：", target, file=sys.stderr)
        sys.exit(1)

    if not files:
        print("没有匹配到任何 .lonlat 文件", file=sys.stderr)
        sys.exit(1)

    total = 0
    for f in files:
        if f.suffix.lower() != ".lonlat":
            continue
        total += split_one_file(f, args.min_points)

    print(f"\n✨ 完成：共写出 {total} 个分段文件。")

if __name__ == "__main__":
    main()
