# CS2 Steam Blocker v1.2

> 🎮 自動阻擋 Steam 連線以防止 CS2 比賽中途被打斷的工具

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)

## 📖 功能特色

- ✅ **自動偵測比賽狀態** - 透過 CS2 官方 GSI API 即時監控遊戲狀態
- 🔒 **智慧阻擋 Steam** - 比賽開始自動阻擋 UDP 3478-3480 端口
- 🔓 **自動恢復連線** - 比賽結束後自動解除阻擋
- ⌨️ **全域快捷鍵** - 小鍵盤快速控制(無需切換視窗)
- 🎨 **系統托盤整合** - 視覺化狀態指示與選單操作
- 🔔 **聲音通知** - 重要操作伴隨提示音效
- 🛡️ **防火牆規則管理** - 自動建立和清理 Windows 防火牆規則

## 🎯 使用情境

當您在 CS2 競技模式中:
- 朋友透過 Steam 邀請您加入遊戲 → **被強制退出當前比賽** 😱
- 本工具會在比賽期間**自動阻擋 Steam 連線**,防止被打斷
- 比賽結束後**自動恢復連線**,不影響正常使用

## 📋 系統需求

- **作業系統**: Windows 10/11
- **Python**: 3.7 或更高版本
- **權限**: 需要**管理員權限**(用於設定防火牆規則)
- **遊戲**: Counter-Strike 2 (CS2)

## 🔧 安裝步驟

### 1. 安裝 Python 依賴套件

```bash
pip install keyboard pystray pillow pywin32
```

### 2. 下載程式

將 `cs2-steam-blocker-python.py` 下載到任意目錄

### 3. 設定 GSI 配置檔

程式首次執行會自動嘗試建立 GSI 配置檔到以下路徑:

```
C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive\game\csgo\cfg\
```

**如果自動建立失敗**,請手動複製 `gamestate_integration_cs2steamblock.cfg` 到上述目錄。

配置檔內容:
```
"CS2 Steam Blocker GSI"
{
  "uri" "http://127.0.0.1:3000"
  "timeout" "5.0"
  "buffer" "0.1"
  "throttle" "0.5"
  "heartbeat" "30.0"
  "data"
  {
    "provider" "1"
    "map" "1"
    "round" "1"
    "player_state" "1"
  }
}
```

## 🚀 使用方法

### 啟動程式

**右鍵點擊** `cs2-steam-blocker-python.py` → **以系統管理員身分執行**

或使用命令列:
```bash
# 以管理員身分開啟 CMD 或 PowerShell
python cs2-steam-blocker-python.py
```

### 快捷鍵操作

| 按鍵 | 功能 | 說明 |
|------|------|------|
| **小鍵盤 0** | 🔔 測試快捷鍵 | 確認快捷鍵是否正常運作 |
| **小鍵盤 1** | 🚫 手動阻止 Steam | 立即阻擋 Steam 連線 |
| **小鍵盤 2** | ✅ 手動恢復 Steam | 立即解除 Steam 阻擋 |
| **小鍵盤 3** | ⚙️ 切換自動模式 | 開啟/關閉自動阻擋功能 |

> 💡 **建議**: 首次使用請先按 **小鍵盤 0** 測試快捷鍵是否正常

### 托盤圖示說明

系統托盤圖示會根據狀態顯示不同顏色:

- 🟢 **綠色** - 正常狀態(在大廳)
- 🟠 **橘色** - 比賽進行中
- 🔴 **紅色** - Steam 已阻擋

### 托盤選單功能

右鍵點擊托盤圖示可使用:
- 📊 查看當前狀態
- 🔧 測試功能(快捷鍵、防火牆檢查)
- 🎛️ 手動控制阻擋/恢復
- ⚙️ 切換自動模式
- 🔄 重新建立 GSI 配置檔
- ❌ 退出程式(自動清理防火牆規則)

## 🎮 遊戲狀態偵測

程式透過 **Valve 官方 GSI API** 偵測以下遊戲階段:

### 會保持阻擋的階段
- ✅ `warmup` - 熱身階段
- ✅ `live` - 比賽進行中
- ✅ `intermission` - **中場休息** (v3.5 修復)

### 會解除阻擋的階段
- ❌ `gameover` - 比賽結束
- ❌ 回到主選單

## 🔒 技術原理

### 阻擋機制
程式透過 Windows 防火牆規則阻擋 Steam 的特定 UDP 端口:
- **端口**: 3478-3480 (Steam 語音和遊戲邀請)
- **方向**: 雙向(入站 + 出站)
- **協定**: UDP
- **目標**: Steam.exe 程式

### 防火牆規則
```
規則名稱: CS2_Block_Steam_Out / CS2_Block_Steam_In
協定: UDP
端口: 3478-3480
動作: 阻擋
```

程式退出時會**自動清除**所有防火牆規則,不會留下殘留設定。

## 🐛 常見問題

### Q: 為什麼需要管理員權限?
**A**: 修改 Windows 防火牆規則需要管理員權限。

### Q: 快捷鍵沒有反應?
**A**: 
1. 確認是否以管理員身分執行
2. 按小鍵盤 0 測試功能
3. 檢查 NumLock 是否開啟

### Q: 中場休息時被解除阻擋?
**A**: v3.5 已修復此問題,現在會在整場比賽(包含中場)保持阻擋。

### Q: 程式找不到 Steam?
**A**: 檢查 Steam 是否安裝在以下路徑:
- `C:\Program Files (x86)\Steam\`
- `C:\Program Files\Steam\`
- `~\Steam\`

### Q: GSI 配置檔建立失敗?
**A**: 手動將 `gamestate_integration_cs2steamblock.cfg` 複製到:
```
C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive\game\csgo\cfg\
```

### Q: 如何確認防火牆規則生效?
**A**: 
1. 右鍵托盤圖示 → "檢查防火牆"
2. 或手動執行: `netsh advfirewall firewall show rule name="CS2_Block_Steam_Out"`

### Q: 會影響 CS2 遊戲連線嗎?
**A**: 不會。只阻擋 Steam 的語音和邀請端口,不影響 CS2 伺服器連線。

## 📝 更新日誌

### v3.6 (2025-10-25)
- ✨ **新增斷線自動偵測**: 加入 GSI 心跳監控機制,3秒無回應自動恢復 Steam
- 🔧 **修復被踢出問題**: 解決被踢出後 Steam 連線無法自動恢復的問題
- 🔒 **單一實例檢測**: 防止重複啟動程式,避免防火牆規則衝突
- 📢 **改進通知系統**: 新增自動恢復通知與重複啟動警告視窗
- 🎯 **優化資源管理**: 程式退出時自動釋放端口鎖定

### v1.1 (2024-10-25)
- ✨ **修復中場問題**: 根據 Valve 官方 GSI API 正確處理 `intermission` 階段
- 📚 改進註解說明與程式碼可讀性
- 🎯 優化遊戲狀態判斷邏輯

### v1.0
- 🔧 優化防火牆規則管理
- 🎨 改進托盤圖示與選單
- 🔔 新增音效通知系統

## ⚠️ 注意事項

1. **不要濫用**: 此工具僅用於防止被 Steam 邀請打斷,請勿用於其他用途
2. **比賽期間無法接收 Steam 消息**: 阻擋期間朋友的訊息和邀請會延遲顯示
3. **手動關閉程式**: 請使用托盤選單的"退出程式"選項,以確保防火牆規則被正確清除
4. **防毒軟體**: 某些防毒軟體可能會誤報,請加入白名單

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request!

## 📄 授權

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案

## 🙏 致謝

- Valve Corporation - CS2 Game State Integration API
- Python 社群 - 優秀的開源套件

## 📧 聯絡方式

如有問題或建議,歡迎開 Issue 討論!

---

**⚡ 享受不被打斷的 CS2 競技體驗!**
