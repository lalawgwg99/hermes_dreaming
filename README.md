# hermes_dreaming brain repo

這是你的「知識腦」真相來源（Source of Truth）。
規則很簡單：人類修改永遠優先；代理只補充、整理與追加證據。

This repo is the source of truth for the brain.
Human edits always win. Agents only append evidence.

## 一句話使用
把新資訊丟進 inbox/ → 代理人整理 → timeline 留證據 → compiled truth 更新

## 快速開始
1) 把新資訊丟進 inbox/
2) 代理人整理到正確分類（people/ companies/ ideas/...）
3) 夜間 Dream Cycle 產生摘要與建議

## 核心設計
- 上半部是 Compiled Truth：當前結論，可修正
- 下半部是 Timeline：只追加，不回寫，保留證據軌跡
- 每個新事實必須帶來源（source + confidence）
- 代理人先讀再寫，避免覆蓋人類結論
- Human edits always win

## 混合模式（Hybrid）
- L0：brain repo 是唯一真相來源
- 外部資料只作「來源輸入」
- 先讀 L0，缺口才查外部
- 外部資料先進 inbox 或 timeline，不直接改 compiled truth

## 資料夾結構
- people/      人物頁（一人一檔）
- companies/   公司頁（一公司一檔）
- ideas/       概念/論點（一概念一檔）
- meetings/    會議紀錄、逐字稿
- media/       文章/書/影片/Podcast 等素材
- originals/   原創想法與產出
- inbox/       未整理輸入
- meta/        規則、夢檔、系統設定
- templates/   統一格式模板

## 重要規則
- Compiled truth 在上，timeline append-only 在下
- 每個新事實都要有來源（source + confidence）
- 任何自動寫入都需可回溯、可撤銷

## 導航（必讀）
- meta/AGENT_RULES.md：代理讀寫規則
- meta/WORKFLOW.md：日常流程（含混合模式）
- meta/MIXED_MODE.md：混合模式完整設計
- meta/TELEGRAM_INTAKE.md：手機端輸入規則
- meta/SIMPLIFIED_MODE.md：一般使用者版本
