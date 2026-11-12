---
name: pdf-folder-merge
name_display: 文件夹PDF合并
description: 将一个文件夹下的多个 PDF 按文件名顺序合并成一个 PDF，支持自然排序（气路1、气路2…气路10 正确排序）、可选横向/竖向显示（工程图纸合并后横放）、递归子文件夹、自定义匹配模式。当用户要求"合并某文件夹下的 PDF""把这几个 PDF 按顺序合成一个""合并后横向显示"时使用本技能。
agent_created: true
---

# Pdf Folder Merge — 文件夹 PDF 按名合并

## Overview

把一个文件夹里的所有 PDF 按文件名顺序（自然排序）合并为一个 PDF。核心是固定复用的脚本 `scripts/merge_folder_pdfs.py`，不要每次现写合并代码。

## 何时使用

- 用户给出一个文件夹路径，要求"合并/合成"其中的 PDF
- 用户提到"按文件名顺序""按顺序合成一个"
- 用户要求合并后"横向显示"（典型：CAD 导出的工程图纸，单页竖版但内容横排）
- 单独指定几个 PDF 文件的合并也适用（先复制/列出到临时清单再调用脚本，或用 --pattern 精确匹配）

不适用：需要对单个 PDF 做编辑/拆分/提取等操作（用 pdfkit-py 或其他工具）。

## 快速开始

```bash
# 基本合并（保持原方向），输出到 <folder>/<folder名>-合并.pdf
python scripts/merge_folder_pdfs.py "D:\图纸\气路图 - 261028"

# 合并并让所有页横向显示（工程图纸常用）
python scripts/merge_folder_pdfs.py "D:\图纸\气路图" --orientation landscape

# 指定输出名 + 只合并 01 开头的文件
python scripts/merge_folder_pdfs.py "D:\图纸" --output "D:\图纸\合并版.pdf" --pattern "气路*.pdf"

# 递归子文件夹
python scripts/merge_folder_pdfs.py "D:\图纸" --recursive
```

Python 用任意 3.10+ 解释器均可；pypdf 缺失时脚本自动 `pip install --user pypdf`。

## 工作流程

1. **确认文件夹**：路径含空格/中文时必须加引号。先 `ls` 看一眼文件夹里有哪些 PDF，确认匹配范围（是否要排除同名合并产物、dwg 等非 PDF 不受影响）。
2. **确认方向需求**：用户没提方向 → 默认 `keep`；用户说"横向显示/横版" → `--orientation landscape`；说"竖向" → `--orientation portrait`。
3. **执行脚本**，核对输出的合并顺序、页数、方向检查结果。
4. **方向验证（landscape/portrait 时）**：脚本已按 mediabox+rotation 做几何校验；如需人工确认内容方向，可用 pymupdf 渲染任一页抽帧查看（`pip install --user pymupdf`）。若发现上下颠倒，用 `--rotate-extra 180` 修正后重跑。
5. **报告**：输出路径、合并顺序（文件名→页数）、总页数、大小。原始文件永不修改。

## 关键行为约定

- **自然排序**：`气路1, 气路2, …, 气路10` 按数字大小排，不是字典序。
- **横向旋转方向**：landscape 对竖版页逆时针转 90°（rotate 270）。CAD 图纸实测此方向正确（标题栏落在右下角）；若用户图纸不同，用 --rotate-extra 180 翻转。
- **幂等**：输出文件存在则直接覆盖；扫描输入时自动排除输出文件自身，避免"合并自己"。
- **跳过坏文件**：读取失败的 PDF 会跳过并在日志中注明，不中断整体合并。
- **原始文件只读**：脚本绝不修改输入 PDF。

## 参数速查

| 参数 | 默认 | 说明 |
|---|---|---|
| `folder` | 必填 | 目标文件夹 |
| `--output` | `<folder>/<folder名>-合并.pdf` | 输出路径 |
| `--pattern` | `*.pdf` | glob 匹配 |
| `--recursive` | 关 | 递归子文件夹 |
| `--orientation` | `keep` | `landscape` / `portrait` / `keep` |
| `--rotate-extra` | `0` | 额外整体旋转（90/180/270，顺时针） |
