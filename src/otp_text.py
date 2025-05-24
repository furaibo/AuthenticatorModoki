import flet as ft
import pyotp
import asyncio


# ft.Textを継承してクラス化
class OtpText(ft.Text):
    def __init__(self, secret: str):
        super().__init__()
        self.size = 40
        self.secret = secret

    # did_mountおよびwill_unmountの定義
    # Note: それぞれpage.controlsへの割当/削除時に実行される
    def did_mount(self):
        self.running = True
        self.page.run_task(self.update_otp_text)

    def will_unmount(self):
        self.running = False

    # OTPテキスト更新処理
    # Note: runningフラグが有効な限り無限ループ処理とする
    async def update_otp_text(self):
        while self.running:
            totp = pyotp.TOTP(self.secret)
            current_otp = str(totp.now())
            self.value = current_otp
            self.update()
            await asyncio.sleep(1)
