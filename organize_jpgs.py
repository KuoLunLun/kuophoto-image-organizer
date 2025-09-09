import re
import shutil
from pathlib import Path
import argparse
from typing import Optional, Iterable

# 僅抓取檔名(去掉最外層副檔名)中 IMGK/IMG_ 後緊接的 4 位數字
PATTERN_IMGK = re.compile(r"IMGK(\d{4})", flags=re.IGNORECASE)
PATTERN_IMG = re.compile(r"IMG_(\d{4})", flags=re.IGNORECASE)
# 支援 QR 檔名鍵值擷取，如 QR_2081.jpg / qr-2081.jpeg
PATTERN_QR = re.compile(r"QR[_-]?(\d{4})", flags=re.IGNORECASE)
PATTERN_TRAILING_KEY = re.compile(r".*[-_](\d{4})$")


def extract_key(filename: str) -> Optional[str]:
    """從檔名擷取 IMGK 後 4 位數字作為資料夾名稱。

    僅處理外層副檔名，能處理像 a.jpg-0.jpg → a.jpg-0。
    未找到符合者返回 None。
    """
    stem = Path(filename).stem
    # 1) 先嘗試 IMGK 後 4 位
    m = PATTERN_IMGK.search(stem)
    if m:
        return m.group(1)
    # 2) 再嘗試 IMG_ 後 4 位
    m2 = PATTERN_IMG.search(stem)
    if m2:
        return m2.group(1)
    return None


def unique_destination(dest_dir: Path, filename: str) -> Path:
    """在目標資料夾內產生不覆蓋的目的路徑。

    若已存在同名檔，會在檔名後追加 (1)、(2)...
    """
    dest = dest_dir / filename
    if not dest.exists():
        return dest
    stem = dest.stem
    suffix = dest.suffix
    i = 1
    while True:
        candidate = dest_dir / f"{stem} ({i}){suffix}"
        if not candidate.exists():
            return candidate
        i += 1


def _extract_qr_to_root(root: Path, *, dry_run: bool, copy: bool) -> int:
    """將 root 底下所有子層的 QR 資料夾中的 QR_*.jpg 搬到 root，並在清空後移除 QR 資料夾。

    回傳已處理(搬移/複製)的檔案數。
    """
    exts = {".jpg", ".jpeg"}
    moved = 0
    # 尋找所有名為 QR 的資料夾
    for qr_dir in sorted([p for p in root.rglob("QR") if p.is_dir()]):
        # 解析父層名末四碼（可用於訊息，但不硬性要求）
        parent_name = qr_dir.parent.name
        m_key = PATTERN_TRAILING_KEY.match(parent_name)
        key_hint = m_key.group(1) if m_key else None

        for f in qr_dir.iterdir():
            if not f.is_file():
                continue
            if f.suffix.lower() not in exts:
                continue
            # 僅處理 QR_* 檔名（避免誤搬）
            if not PATTERN_QR.search(f.name):
                continue

            dest = unique_destination(root, f.name)
            action = "COPY" if copy else "MOVE"
            print(f"[QR-{action}] {f.relative_to(root)} -> {dest.relative_to(root)}")
            if not dry_run:
                if copy:
                    shutil.copy2(f, dest)
                else:
                    shutil.move(str(f), str(dest))
                moved += 1

        # 嘗試移除已空的 QR 資料夾（僅在非 dry_run 且非 copy 情況下）
        if not dry_run and not copy:
            try:
                next(qr_dir.iterdir())
            except StopIteration:
                try:
                    qr_dir.rmdir()
                    print(f"[QR-RMDIR] {qr_dir.relative_to(root)}")
                except Exception as e:
                    print(f"[警告] 無法刪除 {qr_dir}: {e}")
    return moved


def organize(folder: Path, dry_run: bool = False, copy: bool = False, extract_qr: bool = False) -> None:
    """依 IMGK/IMG_ 後 4 位數字建立資料夾並移動/複製 JPG 檔（僅處理該資料夾直屬檔案）。"""
    if not folder.exists() or not folder.is_dir():
        raise ValueError(f"指定路徑不存在或不是資料夾: {folder}")

    exts = {".jpg", ".jpeg"}
    moved = 0
    skipped = 0
    missing_key = 0

    # 先處理 QR 特殊需求：將各子層 QR_*.jpg 拉回根層並清除空的 QR 資料夾
    if extract_qr:
        _extract_qr_to_root(folder, dry_run=dry_run, copy=copy)

    for p in folder.iterdir():
        if not p.is_file():
            continue
        if p.suffix.lower() not in exts:
            continue

        key = extract_key(p.name)
        if not key:
            missing_key += 1
            print(f"[略過] 找不到 IMGK 後4位數字 -> {p.name}")
            continue

        if folder.name == key:
            target_dir = folder
        else:
            target_dir = folder / key
        # 已在正確資料夾中則略過
        if p.parent == target_dir:
            skipped += 1
            continue

        if not dry_run:
            target_dir.mkdir(parents=True, exist_ok=True)
        dest = unique_destination(target_dir, p.name)

        action = "COPY" if copy else "MOVE"
        print(f"[{action}] {p.name} -> {target_dir.name}/{dest.name}")

        if not dry_run:
            if copy:
                shutil.copy2(p, dest)
            else:
                shutil.move(str(p), str(dest))
            moved += 1

    print("\n--- 完成 ---")
    print(f"已處理: {moved} 檔")
    print(f"略過(已在正確資料夾/不需移動): {skipped} 檔")
    print(f"未找到關鍵數字: {missing_key} 檔")


def iter_target_dirs(root: Path, scope: str) -> Iterable[Path]:
    """根據 scope 產生要處理的目錄清單。

    scope: 'current' | 'subdirs' | 'recursive'
    - current: 僅處理 root 自身
    - subdirs: 僅處理 root 的第一層子目錄
    - recursive: 處理 root 及其所有子孫目錄
    """
    if scope == "current":
        yield root
    elif scope == "subdirs":
        for d in sorted([p for p in root.iterdir() if p.is_dir()]):
            yield d
    elif scope == "recursive":
        # 先處理 root 本身，再走訪所有子孫目錄
        yield root
        for d in sorted(root.rglob("*")):
            if d.is_dir():
                yield d
    else:
        raise ValueError(f"未知的 scope: {scope}")


def main():
    parser = argparse.ArgumentParser(
        description="依檔名 IMGK/IMG_ 後4位數建立資料夾並整理 JPG/JPEG"
    )
    parser.add_argument("folder", nargs="?", default=".", help="要整理的根目錄路徑，預設為目前資料夾")
    parser.add_argument("--dry-run", action="store_true", help="僅顯示將執行的動作，不實際移動/複製")
    parser.add_argument("--copy", action="store_true", help="改為複製檔案，而不是移動")
    parser.add_argument(
        "--scope",
        choices=["current", "subdirs", "recursive"],
        default="current",
        help="處理範圍：current=僅根目錄、subdirs=僅第一層子目錄、recursive=根目錄與全部子目錄",
    )
    parser.add_argument(
        "--extract-qr",
        action="store_true",
        help="先將所有子層 QR 資料夾內的 QR_*.jpg 搬到根層；搬移模式下若 QR 變空會嘗試刪除",
    )
    args = parser.parse_args()

    root = Path(args.folder)
    any_processed = False
    for d in iter_target_dirs(root, args.scope):
        any_processed = True
        print(f"\n=== 目錄: {d} ===")
        try:
            organize(d, dry_run=args.dry_run, copy=args.copy, extract_qr=args.extract_qr)
        except Exception as e:
            print(f"[錯誤] {e}")

    if not any_processed:
        print("未找到要處理的目錄。")


if __name__ == "__main__":
    main()
