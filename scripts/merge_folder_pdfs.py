#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""merge_folder_pdfs.py — Merge all PDFs in a folder in filename order (natural sort).

Features:
- Natural sort: 气路1, 气路2, ... 气路10 sorts correctly (not 气路1, 气路10, 气路2).
- Optional orientation control: --orientation landscape rotates portrait pages
  counterclockwise (270) so engineering drawings display horizontally;
  --orientation portrait does the reverse. Default: keep original orientation.
- Auto-installs pypdf (pip --user) if missing.
- Overwrites output file silently on re-run; skips the output file itself
  when scanning the input folder.

Usage:
    python merge_folder_pdfs.py <folder> [--output OUT.pdf] [--pattern "*.pdf"]
                                [--recursive] [--orientation keep|landscape|portrait]
                                [--rotate-extra 0|90|180|270]

Exit codes: 0 ok, 1 error.
"""
import argparse
import glob
import os
import re
import subprocess
import sys


def ensure_pypdf():
    try:
        import pypdf  # noqa: F401
        return
    except ImportError:
        pass
    print("[setup] pypdf 未安装，正在安装（--user）...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "-q", "pypdf"])
    import importlib
    importlib.invalidate_caches()


def natural_key(path):
    """Sort key: split filename into digit/non-digit chunks; digits compare as ints."""
    name = os.path.basename(path)
    parts = re.split(r"(\d+)", name)
    key = []
    for p in parts:
        if p.isdigit():
            key.append((1, int(p), ""))
        else:
            key.append((0, 0, p))
    return key


def collect_pdfs(folder, pattern, recursive, exclude):
    if recursive:
        hits = glob.glob(os.path.join(folder, "**", pattern), recursive=True)
    else:
        hits = glob.glob(os.path.join(folder, pattern))
    hits = [os.path.abspath(p) for p in hits if os.path.abspath(p) != os.path.abspath(exclude)]
    hits.sort(key=natural_key)
    return hits


def page_effective_size(page):
    """(w, h) as displayed, accounting for existing /Rotate."""
    box = page.mediabox
    w, h = float(box.width), float(box.height)
    if page.rotation % 180 == 90:
        w, h = h, w
    return w, h


def rotate_pages_for_orientation(pages, orientation):
    """Return (n_rotated, direction_desc). Rotates only pages that mismatch."""
    n = 0
    for pg in pages:
        w, h = page_effective_size(pg)
        if orientation == "landscape" and h > w:
            pg.rotate(270)  # counterclockwise 90° — CAD 图纸实测正确方向
            n += 1
        elif orientation == "portrait" and w > h:
            pg.rotate(90)
            n += 1
    return n


def main():
    ap = argparse.ArgumentParser(description="Merge folder PDFs in filename order")
    ap.add_argument("folder", help="包含 PDF 的文件夹")
    ap.add_argument("--output", default=None, help="输出 PDF 路径（默认 <folder>/<folder名>-合并.pdf）")
    ap.add_argument("--pattern", default="*.pdf", help="文件匹配模式，默认 *.pdf")
    ap.add_argument("--recursive", action="store_true", help="递归子文件夹")
    ap.add_argument("--orientation", choices=["keep", "landscape", "portrait"],
                    default="keep", help="显示方向：keep=保持原样（默认），landscape=横向，portrait=竖向")
    ap.add_argument("--rotate-extra", type=int, choices=[0, 90, 180, 270], default=0,
                    help="在 orientation 基础上额外旋转所有页（度，顺时针）")
    args = ap.parse_args()

    ensure_pypdf()
    import pypdf

    folder = os.path.abspath(args.folder)
    if not os.path.isdir(folder):
        print(f"[error] 文件夹不存在: {folder}")
        return 1

    folder_name = os.path.basename(folder.rstrip("\\/"))
    output = os.path.abspath(args.output) if args.output else os.path.join(folder, f"{folder_name}-合并.pdf")
    os.makedirs(os.path.dirname(output), exist_ok=True)

    pdfs = collect_pdfs(folder, args.pattern, args.recursive, output)
    if not pdfs:
        print(f"[error] 未找到匹配 {args.pattern} 的 PDF 文件")
        return 1

    print(f"共 {len(pdfs)} 个文件，合并顺序：")
    writer = pypdf.PdfWriter()
    total = 0
    for p in pdfs:
        try:
            reader = pypdf.PdfReader(p)
        except Exception as e:
            print(f"  [skip] {os.path.basename(p)} 读取失败: {e}")
            continue
        n = len(reader.pages)
        for pg in reader.pages:
            if args.orientation != "keep":
                rotate_pages_for_orientation([pg], args.orientation)
            if args.rotate_extra:
                pg.rotate(args.rotate_extra)
            writer.add_page(pg)
        total += n
        print(f"  {os.path.basename(p)}  ({n} 页)")

    with open(output, "wb") as f:
        writer.write(f)

    # 校验
    rd = pypdf.PdfReader(output)
    print(f"\n输出: {output}")
    print(f"总页数: {len(rd.pages)} (预期 {total})")
    size_mb = os.path.getsize(output) / 1048576
    print(f"大小: {size_mb:.1f} MB")
    if args.orientation != "keep":
        bad = 0
        for i, pg in enumerate(rd.pages):
            w, h = page_effective_size(pg)
            ok = (w > h) if args.orientation == "landscape" else (h > w)
            if not ok:
                bad += 1
                print(f"  [warn] 第 {i+1} 页方向不符")
        print("方向检查:", "全部符合" if bad == 0 else f"{bad} 页不符，可用 --rotate-extra 调整")
    return 0


if __name__ == "__main__":
    sys.exit(main())
