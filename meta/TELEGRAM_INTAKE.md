# Telegram Intake (智能自動人性化)

目標：手機端「像聊天一樣」就能記錄。

## 支援格式（自動判斷）
1) 明確前綴
- inbox: <內容>
- idea: <一句話>
- meeting: <摘要>
- person: <姓名> | <一句話關係>
- company: <公司> | <一句話摘要>

2) 無前綴（智能推斷）
- 只要一句話 + 連結 → media
- 出現「跟誰開會/會議」 → meeting
- 出現人名 + 角色描述 → people
- 出現公司名 + 做什麼 → companies
- 其他 → inbox

## 自動命名規則
- inbox/ YYYY-MM-DD_<slug>.md
- meetings/ YYYY-MM-DD_<slug>.md
- ideas/ YYYY-MM-DD_<slug>.md
- people/ <name>.md
- companies/ <company>.md

## 寫入規則
- 先讀再寫
- timeline 只追加
- 每條新增事實附 source + confidence
- 若不確定就寫入 inbox/
