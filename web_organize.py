from flask import Flask, render_template, request
from pathlib import Path
from io import StringIO
import sys

# 從同目錄導入先前的整理功能
from organize_jpgs import organize, iter_target_dirs, _extract_qr_to_root


def create_app() -> Flask:
    # 讓 Flask 在 PyInstaller onefile 下能找到 templates
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        template_dir = Path(sys._MEIPASS) / "templates"  # type: ignore[attr-defined]
        return Flask(__name__, template_folder=str(template_dir))
    return Flask(__name__)


app = create_app()


@app.route("/", methods=["GET", "POST"])
def index():
    default_folder = str(Path.cwd())
    output = None
    folder = default_folder
    copy_flag = False
    extract_qr = False
    scope = "current"

    if request.method == "POST":
        folder = request.form.get("folder", default_folder).strip() or default_folder
        copy_flag = request.form.get("copy") == "on"
        action = request.form.get("action", "preview")
        scope = request.form.get("scope", "current")
        extract_qr = request.form.get("extract_qr") == "on"
        qr_only = action in ("qr_preview", "qr_execute")

        # 捕捉 organize() 的標準輸出
        buf = StringIO()
        old_stdout = sys.stdout
        try:
            sys.stdout = buf
            dry_run = action in ("preview", "qr_preview")
            root = Path(folder)
            any_processed = False
            for d in iter_target_dirs(root, scope):
                any_processed = True
                print(f"\n=== 目錄: {d} ===")
                try:
                    if extract_qr or qr_only:
                        try:
                            _extract_qr_to_root(d, dry_run=dry_run, copy=copy_flag)
                        except Exception as e:
                            print(f"[警告] QR: {e}")
                    if not qr_only:
                        organize(d, dry_run=dry_run, copy=copy_flag)
                except Exception as e:
                    print(f"[錯誤] {e}")
            if not any_processed:
                print("未找到要處理的目錄。")
        except Exception as e:
            print(f"[錯誤] {e}")
        finally:
            sys.stdout = old_stdout
        output = buf.getvalue()

    return render_template(
        "index.html",
        folder=folder,
        copy_flag=copy_flag,
        output=output,
        scope=scope,
        extract_qr=extract_qr,
    )


if __name__ == "__main__":
    # 在本機啟動開發伺服器
    app.run(host="127.0.0.1", port=5000, debug=False)

