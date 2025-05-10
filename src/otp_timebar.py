import flet as ft
import asyncio
from datetime import datetime


# ft.ProgressBarを継承してクラス化
class OtpTimeBar(ft.ProgressBar):
    def __init__(self):
        super().__init__()
        self.value = 1
        self.width = 450

    # did_mountおよびwill_unmountの定義
    # Note: Flet指定のメソッドでそれぞれpage.controlsへの割当/削除時に実行される
    def did_mount(self):
        self.running = True
        self.page.run_task(self.update_time_bar)

    def will_unmount(self):
        self.running = False

    # 残り時間バー表示処理
    # Note: runningフラグが有効な限り無限ループ処理とする
    async def update_time_bar(self):
        while self.running:
            now = datetime.now()
            remaining_sec = now.second % 30
            self.value = remaining_sec / 30
            self.update()
            await asyncio.sleep(0.05)
