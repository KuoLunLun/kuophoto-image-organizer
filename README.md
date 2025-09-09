# Kuo Photo 影像整理工具

這是一個在 Windows 上使用的影像整理小工具，支援依檔名中的 IMGK/IMG_ 後 4 位數字自動分組（例如 IMGK2081.jpg 會被放到 2081 資料夾）。同時內建小型 Flask 網頁介面，並提供「QR 檔抽出」功能：把子層 `QR` 資料夾內的 `QR_*.jpg/.jpeg` 搬到目前處理的根層，搬移模式下若 `QR` 變成空資料夾會自動刪除。

## 功能特色
- 分組規則：擷取檔名中 `IMGK` 或 `IMG_` 後面緊接的 4 位數字（不分大小寫）。
- 支援副檔名：`.jpg`、`.jpeg`。
- 檔名衝突處理：自動在檔名後加上 `(1)`、`(2)`…。
- 網頁介面：深色/淺色主題（預設 Dracula 深色主題）、額外的 QR 操作區塊。
- 命令列（CLI）：批次處理快速，另提供 `--extract-qr` 旗標先抽出 QR 檔。

## 可執行檔
- `dist/web_organize.exe`（網頁介面）
- `dist/organize_jpgs.exe`（命令列）

## 快速開始（Web）
1. 直接執行 `dist/web_organize.exe`。
2. 瀏覽器開啟 `http://127.0.0.1:5000`。
3. 設定「目標資料夾」、選擇處理範圍（僅此資料夾 / 第一層子資料夾 / 遞迴全部）；可選：
   - 勾選「以複製方式」以保留原檔（不刪除 QR）。
   - 勾選「將子層 QR 搬至根層並清空」：在一般整理前，先把各子層 `QR` 內的 `QR_*.jpg` 搬到根層。
4. 建議先按「預覽（Dry Run）」確認，再按「執行整理」。
5. 另有「額外操作」區塊，可單獨執行／預覽 QR 檔抽出與清空。

## 命令列（CLI）使用範例
```
# 預覽流程，處理第一層子資料夾
organize_jpgs.exe "D:\\Photos\\Root" --scope subdirs --dry-run

# 實際執行，遞迴處理全部，並在分組前先抽出 QR 檔
organize_jpgs.exe "D:\\Photos\\Root" --scope recursive --extract-qr

# 以複製方式（保留原檔；不會刪除 QR 資料夾）
organize_jpgs.exe "D:\\Photos\\Root" --copy
```

## 建置（可重現）
- 已將 PyInstaller 規格檔版控：`web_organize.spec`、`organize_jpgs.spec`（保證同樣設定可重建）。
- 提供目前環境凍結版本：`requirements.freeze.txt`（可在新機器重現打包環境）。

方式 A：一鍵建置（建議在 Windows）
```
powershell -ExecutionPolicy Bypass -File .\\build\\build_windows_exe.ps1
```

方式 B：手動建置
```
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.freeze.txt
pip install pyinstaller
pyinstaller web_organize.spec
pyinstaller organize_jpgs.spec
```

## 注意事項
- `web_organize.exe` 已啟用主控台視窗（console=True），可直接觀察執行日誌。
- 若防毒軟體誤擋，請將 `dist/` 路徑加入排除清單。
- 建議路徑避免含有受限權限或需系統許可的資料夾。
- 若需要調整主題（如按鈕色、字級），可直接修改 `templates/index.html` 內的 CSS 變數。

## 版本
- v0.2.0：加入 QR 檔抽出、巢狀資料夾修正、Dracula 主題、網頁介面改良、版本化 spec。

## 授權
僅供作者／專案內部使用（Proprietary）。保留一切權利。
