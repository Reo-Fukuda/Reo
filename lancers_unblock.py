# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright
import time
import logging
import os

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# ==== 設定 ====
BLOCK_PAGE_URL = "https://www.lancers.jp/blacklist"
SLEEP_SEC = 1.0  # 解除処理間隔（高速化）
MAX_RETRIES = 3  # リトライ回数

# Chromeのユーザープロファイルパスを取得
CHROME_DEFAULT_PROFILE = os.path.join(os.path.dirname(__file__), "lancers_profile")
if not os.path.exists(CHROME_DEFAULT_PROFILE):
    CHROME_PROFILE = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")
    CHROME_DEFAULT_PROFILE = os.path.join(CHROME_PROFILE, "Default")


def _get_failure_text(req) -> str:
    try:
        failure_attr = getattr(req, "failure", None)
        failure_val = failure_attr() if callable(failure_attr) else failure_attr
        if isinstance(failure_val, dict):
            return (
                failure_val.get("errorText")
                or failure_val.get("error_text")
                or str(failure_val)
            )
        if isinstance(failure_val, str):
            return failure_val
        return ""
    except Exception:
        return ""


def safe_get_title(page, attempts: int = 3) -> str:
    for _ in range(attempts):
        try:
            return page.title() or ""
        except Exception:
            time.sleep(0.5)
    return ""


def safe_locator_visible(page, selector: str) -> bool:
    try:
        return page.locator(selector).first.is_visible()
    except Exception:
        return False


def find_unblock_buttons(page):
    """解除ボタンを全て見つける"""
    unblock_selectors = [
        'a:has-text("解除する")',
        'button:has-text("解除する")',
        'a[href*="unblock"]',
        '.unblock-button',
        '[data-action*="unblock"]'
    ]

    found_buttons = []
    for selector in unblock_selectors:
        try:
            buttons = page.locator(selector).all()
            if buttons:
                found_buttons.extend(buttons)
                break
        except Exception:
            continue

    return found_buttons


# 不要な関数を削除

def wait_for_dialog_and_click(page, max_wait_time=5):
    """確認ダイアログを待機してクリックする（高速版）"""
    start_time = time.time()

    # 最も可能性の高いセレクタを最初にチェック
    priority_selectors = [
        'button:has-text("OK")',
        'button:has-text("はい")',
        'button:has-text("解除")',
        '.modal .btn-primary',
    ]

    # その他のセレクタ
    other_selectors = [
        'button:has-text("確認")',
        'input[type="submit"][value*="OK"]',
        'input[type="button"][value*="OK"]',
        '.modal button:has-text("OK")',
        '.modal .btn-confirm',
        '.confirm-ok',
        '.dialog-ok',
        '[data-action="confirm"]',
        '[data-action="ok"]',
        'button[onclick*="confirm"]'
    ]

    all_selectors = priority_selectors + other_selectors

    while time.time() - start_time < max_wait_time:
        # 各セレクタを順番に試す
        for selector in all_selectors:
            try:
                element = page.locator(selector).first
                if element.is_visible():
                    logger.info(f"確認ボタンを発見: {selector}")
                    element.click()
                    logger.info("確認ボタンをクリックしました")
                    return True
            except Exception:
                continue

        # 短い間隔で再チェック
        time.sleep(0.1)  # 100msに短縮

    logger.warning(f"確認ダイアログが{max_wait_time}秒以内に見つかりませんでした")
    return False


def unblock_user(page, unblock_button, retry_count=0):
    """ユーザーのブロックを解除する（シンプル高速版）"""
    try:
        logger.info("ブロック解除処理を開始...")

        # シンプルなダイアログハンドラーを設定
        def dialog_handler(dialog):
            try:
                logger.info(f"ネイティブダイアログを検出: {dialog.type} - {dialog.message}")
                dialog.accept()  # OKをクリック
                logger.info("ネイティブダイアログでOKをクリックしました")
            except Exception as e:
                logger.warning(f"ダイアログ処理中にエラー: {e}")

        # ダイアログハンドラーを設定
        page.on("dialog", dialog_handler)

        # ボタンが見えるところまでスクロール
        unblock_button.scroll_into_view_if_needed()
        time.sleep(0.3)

        # 解除ボタンをクリック
        logger.info("解除ボタンをクリックします...")
        unblock_button.click()

        # ダイアログ処理の待機
        time.sleep(1.5)

        # 処理完了
        logger.info("解除処理完了")
        return True

    except Exception as e:
        logger.error(f"ブロック解除中にエラー: {e}")

        # リトライ
        if retry_count < MAX_RETRIES:
            logger.info(f"リトライします ({retry_count + 1}/{MAX_RETRIES})")
            time.sleep(1)
            return unblock_user(page, unblock_button, retry_count + 1)

        return False


def manual_login_first():
    """最初に手動でログインしてもらう"""
    print("\n" + "="*60)
    print("📌 初回セットアップ")
    print("="*60)
    print("\n以下の手順でログインしてください：\n")
    print("1. 通常のChromeブラウザを開く")
    print("2. ランサーズ（https://www.lancers.jp）にアクセス")
    print("3. 通常通りログインする")
    print("4. 「ログイン状態を保持する」にチェックを入れる")
    print("5. ログイン完了後、Chromeを完全に閉じる")
    print("\n重要: すべてのChromeウィンドウを閉じてください！")
    print("="*60)
    input("\n準備ができたらEnterキーを押してください...")


def main():
    try:
        # Chromeプロファイルの確認
        if not os.path.exists(CHROME_DEFAULT_PROFILE):
            logger.error(f"Chrome既定プロファイルが見つかりません: {CHROME_DEFAULT_PROFILE}")
            manual_login_first()
            return

        logger.info("🚀 ブロック解除処理を開始します")

        with sync_playwright() as p:
            try:
                # 既存のChromeプロファイルを使用してブラウザ起動（設定改良）
                logger.info("Chromeブラウザを起動中...")

                context = p.chromium.launch_persistent_context(
                    user_data_dir=CHROME_DEFAULT_PROFILE,
                    channel="chrome",
                    headless=False,
                    slow_mo=50,  # 操作速度を高速化（200→50ms）
                    viewport={"width": 1280, "height": 720},
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--disable-features=IsolateOrigins,site-per-process",
                        "--disable-popup-blocking",  # ポップアップブロック無効
                        "--disable-default-apps",
                        "--no-first-run",
                    ]
                )

                if context.pages:
                    page = context.pages[0]
                else:
                    page = context.new_page()

                # 画面にフォーカスを持ってくる
                try:
                    page.bring_to_front()
                except Exception:
                    pass

                # デバッグ用ログイベント
                try:
                    page.on("console", lambda msg: logger.info(f"[console] {msg.type}: {msg.text}"))
                    page.on("requestfailed", lambda req: logger.warning(f"[requestfailed] {req.url} - {_get_failure_text(req)}"))
                except Exception:
                    pass

                # デフォルトタイムアウト設定
                try:
                    context.set_default_navigation_timeout(60_000)
                    context.set_default_timeout(15_000)  # 30秒→15秒に短縮
                    page.set_default_navigation_timeout(60_000)
                    page.set_default_timeout(15_000)
                except Exception:
                    pass

                # ブロックページへアクセス
                logger.info(f"ブロックページへアクセス: {BLOCK_PAGE_URL}")
                page.goto(BLOCK_PAGE_URL, wait_until="domcontentloaded")
                time.sleep(2)  # 初期待機時間を短縮（5秒→2秒）

                # ログイン確認
                title_text = safe_get_title(page)
                logout_visible = safe_locator_visible(page, 'a[href="/logout"]')

                if ('login' in page.url) or ((title_text and "ログイン" in title_text) or not logout_visible):
                    logger.warning("ログインが必要です。")
                    print("\n" + "="*60)
                    print("ブラウザ画面でランサーズにログインしてください。")
                    print("ログイン完了後、自動でブロックページへ遷移します。")
                    print("="*60)
                    input("ログイン完了後、Enterキーを押してください...")
                    page.goto(BLOCK_PAGE_URL, wait_until="domcontentloaded")
                    time.sleep(2)  # 短縮

                # URLの確認
                current_url = page.url
                if "blacklist" not in current_url:
                    logger.error(f"ブロックページへのアクセスに失敗: {current_url}")
                    logger.info("手動でブロックページへ移動してください。")
                    input("移動完了後、Enterキーを押してください...")

                # 解除処理のメインループ
                success_count = 0
                failed_count = 0
                total_processed = 0

                logger.info("🎯 ブロック解除処理を開始します...")
                print("-" * 50)
                print("⚠️  停止する場合は Ctrl+C を押してください")
                print("-" * 50)

                while True:
                    try:
                        # ページをリフレッシュして最新の状態を取得
                        if total_processed > 0 and total_processed % 10 == 0:  # 10件ごとにリフレッシュ
                            logger.info("ページをリフレッシュします...")
                            page.reload()
                            time.sleep(2)  # 短縮

                        # 解除ボタンを探す
                        unblock_buttons = find_unblock_buttons(page)

                        if not unblock_buttons:
                            logger.info("✅ 解除可能なユーザーが見つかりません。全て解除完了の可能性があります。")
                            break

                        # 最初の解除ボタンを処理
                        first_button = unblock_buttons[0]

                        # ユーザー名を取得（可能であれば）
                        username = "不明"
                        try:
                            # 親要素や近くの要素からユーザー名を取得
                            parent = first_button.locator("xpath=../..")
                            username_element = parent.locator("a").first
                            if username_element.is_visible():
                                username = username_element.text_content().strip()
                        except Exception:
                            pass

                        logger.info(f"🎯 処理対象: {username}")

                        # ブロック解除実行
                        result = unblock_user(page, first_button)

                        if result:
                            success_count += 1
                            logger.info(f"✅ {username} - 解除成功")
                        else:
                            failed_count += 1
                            logger.warning(f"❌ {username} - 解除失敗")

                        total_processed += 1

                        # リアルタイム進捗表示
                        logger.info(f"📊 進捗: 成功{success_count}件, 失敗{failed_count}件, 合計{total_processed}件処理")

                        # 次の処理まで待機（高速化）
                        time.sleep(SLEEP_SEC)

                    except KeyboardInterrupt:
                        logger.info("🛑 ユーザーによって処理が中断されました")
                        break
                    except Exception as e:
                        logger.error(f"処理中にエラーが発生: {e}")
                        failed_count += 1
                        time.sleep(SLEEP_SEC)
                        continue

                # 結果サマリー
                print("\n" + "="*50)
                print("📊 処理結果")
                print("="*50)
                print(f"✅ 成功: {success_count}件")
                print(f"❌ 失敗: {failed_count}件")
                print(f"📝 合計: {total_processed}件")
                print("="*50)

                input("\n処理が完了しました。Enterキーを押して終了...")

            except KeyboardInterrupt:
                logger.info("🛑 処理が中断されました")
            except Exception as e:
                logger.exception("予期しないエラーが発生しました")
                try:
                    page.screenshot(path="unblock_error.png", full_page=True)
                    logger.info("スクリーンショットを保存: unblock_error.png")
                except Exception:
                    pass
                input("Enterキーを押して終了...")
            finally:
                try:
                    context.close()
                except Exception:
                    pass

    except Exception as e:
        logger.error(f"メイン関数でエラーが発生: {e}")
        import traceback
        traceback.print_exc()
        input("Enterキーを押して終了...")


if __name__ == "__main__":
    try:
        print("="*50)
        print("ランサーズ自動ブロック解除ツール（高速版）")
        print("="*50)
        print()
        print("📌 事前準備:")
        print("1. 通常のChromeでランサーズにログイン済みであること")
        print("2. ブロックリストにユーザーが登録されていること")
        print("3. Chromeのすべてのウィンドウを閉じること")
        print()
        print("⚠️  注意:")
        print("- このツールはブロック済みユーザーを順次解除します")
        print("- 確認ダイアログが表示される場合があります")
        print("- 自動処理できない場合は手動操作を求められます")
        print("- 停止する場合は Ctrl+C を押してください")
        print()

        # Chromeが起動していないか確認
        try:
            import psutil
            chrome_running = False
            for proc in psutil.process_iter(['name']):
                if 'chrome' in proc.info['name'].lower():
                    chrome_running = True
                    break

            if chrome_running:
                print("⚠️  Chromeが起動中です！")
                print("すべてのChromeウィンドウを閉じてください。")
                input("閉じたらEnterキーを押してください...")
        except ImportError:
            print("psutilがインストールされていません。手動でChromeが閉じられていることを確認してください。")

        input("\n準備ができたらEnterキーを押して開始...")
        print()

        main()

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        input("Enterキーを押して終了...")
