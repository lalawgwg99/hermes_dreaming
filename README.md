# hermes_dreaming

一個「給人與 AI 共用」的知識作業系統。

把你的工作資訊變成可持續更新、可追溯、可被 AI 正確讀寫的長期知識庫。

## 安裝

```bash
cd hermes_dreaming
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```

## 快速開始

```bash
# 看 brain 狀態
brain status

# 建立一個人物頁
brain add person "Jordan Lee" --tags "bd,partner"

# 快速丟東西進 inbox
brain inbox "Jordan 要從 A 公司轉去 B 公司"

# 搜尋
brain search "Jordan"

# 看某個實體的時間線
brain timeline Amazon

# 驗證所有 entity 格式
brain validate

# 跑 Dream Cycle（夜間整理摘要）
brain dream
```

## CLI 命令一覽

| 命令 | 說明 |
|---|---|
| `brain status` | 總覽：檔案數量、entity 統計、標籤、近期活動 |
| `brain validate` | 驗證 frontmatter、結構、來源完整性 |
| `brain add <type> <name>` | 從模板建立 entity（person/company/idea/meeting/...） |
| `brain search <query>` | 全文搜尋所有 entity |
| `brain inbox <text>` | 快速捕獲到 inbox/ |
| `brain timeline <entity>` | 顯示某 entity 的時間線 |
| `brain dream` | 執行 Dream Cycle，生成每日摘要 |

所有命令都支援 `--json` 輸出。

## 資料模型

每個 entity（`people/`、`companies/`、`ideas/`）包含：

1. **YAML frontmatter** — `type`、`updated_at`、`tags`
2. **Compiled Truth** — 當前結論
3. **Timeline (append-only)** — 證據事件流，每條帶 `(source: ...)`

```md
---
type: company
updated_at: 2026-04-11
tags:
  - ai
---

# Example Co

## Compiled Truth
- What it does: ...
- Stage: ...

## Timeline (append-only)
- 2026-04-11 — Signed pilot with Acme. (source: meeting | Weekly Sync | 2026-04-11)
```

## 核心原則

- Source of Truth 在這個 repo（L0）
- Human edits always win
- 先讀再寫（Read before write）
- Timeline 只追加，不回寫
- 沒來源不升級為結論

## 資料夾說明

| 資料夾 | 內容 |
|---|---|
| `people/` | 人物頁（一人一檔） |
| `companies/` | 公司頁（一公司一檔） |
| `ideas/` | 概念與論點 |
| `meetings/` | 會議紀錄 |
| `media/` | 文章/書/影片摘要 |
| `originals/` | 原創想法 |
| `inbox/` | 待整理輸入 |
| `templates/` | 模板 |
| `meta/` | 規則、流程、整合文件 |
| `brain/` | Python CLI 套件 |

## 品質保證

```bash
# 本地驗證
brain validate

# JSON 格式
brain validate --json
```

CI 在每次 push/PR 時自動驗證（`.github/workflows/brain-guard.yml`）。

## 每日流程

1. 新資訊用 `brain inbox` 快速捕獲
2. 用 `brain add` 建立 entity 或手動整理到對應資料夾
3. 在 Timeline 追加事件與來源
4. 有足夠證據才更新 Compiled Truth
5. `brain validate` 後 commit

## 重要文件

- `meta/AGENT_RULES.md` — 代理讀寫規範
- `meta/WORKFLOW.md` — 日常流程
- `meta/MIXED_MODE.md` — 混合模式（L0/L1）
- `meta/GBRAIN_INTEGRATION.md` — gbrain 整合
- `meta/MATURITY_ROADMAP.md` — 成熟化路線圖
