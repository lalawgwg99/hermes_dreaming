# GBrain Integration Guide

這份文件定義 `hermes_dreaming` 與 `gbrain` 的整合方式。

## 目標
- `hermes_dreaming` 維持 L0 真相來源（markdown + git）。
- `gbrain` 提供檢索、向量索引、混合查詢能力。
- 人類可直接改 markdown；`gbrain sync` 只負責同步，不改寫規則。

## 架構邊界
- L0（System of Record）：本 repo 的 markdown 檔案。
- L1（Retrieval Layer）：gbrain 的 Postgres/pgvector 索引。
- 寫入原則：先寫 L0，再同步到 L1；不要反向由 L1 覆蓋 L0。

## 快速啟用
1. 安裝 bun（若尚未安裝）。
2. 在 repo 根目錄執行：
   - `bash scripts/setup_gbrain.sh`
3. 依提示執行：
   - `gbrain init --supabase`
   - `gbrain import "<repo_path>" --no-embed`
   - `gbrain embed --stale`

## 日常流程（建議）
1. 人工或代理寫入 markdown（符合 Compiled Truth + Timeline 規範）。
2. 提交前跑驗證：
   - `bash scripts/validate_brain.sh`
3. 推送後或定時執行：
   - `gbrain sync --repo "<repo_path>" && gbrain embed --stale`
4. 查詢時優先使用：
   - `gbrain query "<question>"`
   - `gbrain search "<keywords>"`

## Nightly 排程（本機 cron）
- 安裝命令：
  - `bash scripts/setup_gbrain_nightly_cron.sh`
- 預設排程：每天 02:30（本機時區）
- 執行器：`scripts/run_gbrain_nightly.sh`
- 日誌：`meta/logs/gbrain-nightly.log`
- 若尚未安裝 gbrain：任務會記錄 warning 並跳過，不會中斷 cron。

## 衝突與風險控管
- 若 gbrain 查詢結果與 markdown 結論衝突，以 markdown 為準。
- 若來源不明，僅寫入 timeline，避免直接改 compiled truth。
- 每次批次更新後，抽查 3-5 個關鍵頁（people/companies/ideas）。

## 升級策略
- 升級前先跑：
  - `gbrain check-update`
- 只在測試通過後升級：
  - `bash scripts/validate_brain.sh`
- 若升級異常，保留 L0 不變，先停止 sync，再回滾 gbrain 版本。
