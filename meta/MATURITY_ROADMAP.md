# Hermes Dreaming Maturity Roadmap

## 現況評估（2026-04-11）
- 優勢：知識模型清楚（Compiled Truth + append-only Timeline + source）。
- 缺口：缺自動驗證、缺 CI gate、缺正式整合檢索層 runbook。

## M1：Operational Baseline（本次已完成）
- `scripts/validate_brain.sh`：檢查核心結構與 source。
- `.github/workflows/brain-guard.yml`：PR/Push 自動把關。
- `meta/GBRAIN_INTEGRATION.md`：L0/L1 邊界與操作規範。
- `scripts/setup_gbrain.sh`：一鍵啟動 gbrain 流程。

## M2：Data Quality（下一步）
- 已加 frontmatter 最小 schema 驗證（type, updated_at, tags）。
- 增加 dead-link 檢查與重複實體檢查（同人異名）。
- 定義 confidence 分級字典（L0/L1/L2）並機器驗證。

## M3：Automation
- 建 nightly dream cycle job（只整理/摘要，不覆寫結論）。
- 建 weekly hygiene job（清 inbox、補來源、修壞引用）。
- 每次自動化都輸出變更報告到 `meta/dreams/`。

## M4：Scale
- gbrain 全量導入（sync + embed + query 納入標準流程）。
- 加 retrieval quality baseline（固定問題集 + 命中率回歸測試）。
- 當檔案量破 5k 時，調整分桶與索引策略。
