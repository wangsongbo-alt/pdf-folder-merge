# pdf-folder-merge · 文件夹 PDF 按名合并

把一个文件夹里的 PDF 按**文件名自然顺序**合并成一个 PDF，支持合并后统一横向/竖向显示 —— 专门针对 CAD 导出的工程图纸场景（单页竖版、内容横排，合并打印时需要横放）。

这是一个 **WorkBuddy / Claude 技能（Skill）** 包，包含 `SKILL.md` 说明书与可直接调用的 Python 脚本。

## 特性

- **自然排序**：`气路1, 气路2, …, 气路10` 按数字大小排，不会出现 `10` 排在 `2` 前面的字典序问题
- **横向显示**：`--orientation landscape` 把竖版页统一旋转，工程图纸合并打印不再需要手动转页
- **精确匹配**：`--pattern` 只合并指定文件（如 `气路图*.pdf`），附件资料不受影响
- **递归子目录**：`--recursive` 一并合并子文件夹
- **幂等**：输出文件已存在则覆盖；扫描时自动排除输出文件自身，不会"合并自己"
- **容错**：读取失败的 PDF 跳过并记录，不中断整体合并
- **只读输入**：原始 PDF 永不修改

## 依赖

- Python 3.10+
- [pypdf](https://pypi.org/project/pypdf/)（缺失时脚本会自动 `pip install --user pypdf`）
- 可选：pymupdf（仅用于人工核验渲染）

## 用法

```bash
# 基本合并，输出 <folder>/<folder名>-合并.pdf，保持原方向
python scripts/merge_folder_pdfs.py "D:\图纸\气路图 - 261028"

# 合并后所有页横向显示（工程图纸常用）
python scripts/merge_folder_pdfs.py "D:\图纸\气路图" --orientation landscape

# 指定输出路径 + 只合并 气路 开头的 PDF
python scripts/merge_folder_pdfs.py "D:\图纸" \
  --output "D:\图纸\气路图01-03合并.pdf" --pattern "气路图*.pdf"

# 递归子文件夹
python scripts/merge_folder_pdfs.py "D:\图纸" --recursive
```

路径含空格或中文时加引号。

## 参数

| 参数 | 默认 | 说明 |
|---|---|---|
| `folder` | 必填 | 目标文件夹 |
| `--output` | `<folder>/<folder名>-合并.pdf` | 输出路径 |
| `--pattern` | `*.pdf` | glob 匹配 |
| `--recursive` | 关 | 递归子文件夹 |
| `--orientation` | `keep` | `landscape` / `portrait` / `keep` |
| `--rotate-extra` | `0` | 额外整体旋转（90/180/270，顺时针） |

## 关于横向方向

`landscape` 对竖版页按逆时针 90°（rotate 270）旋转 —— 实测 CAD 图纸标题栏会落在右下角，方向正确。

若你的图纸来源不同、打开后上下颠倒，用 `--rotate-extra 180` 翻转重跑即可。

## 作为技能安装

把本仓库内容放到技能目录即可：

- 用户级（所有项目可用）：`~/.workbuddy/skills/pdf-folder-merge/`
- 项目级：`<项目>/.workbuddy/skills/pdf-folder-merge/`

目录结构：

```
pdf-folder-merge/
├── SKILL.md
└── scripts/
    └── merge_folder_pdfs.py
```

## 输出示例

```
共 3 个文件，合并顺序：
  气路图01.pdf  (1 页)
  气路图02.pdf  (1 页)
  气路图03.pdf  (1 页)

输出: D:\...\气路图01-03合并.pdf
总页数: 3 (预期 3)
大小: 0.7 MB
方向检查: 全部符合
```
