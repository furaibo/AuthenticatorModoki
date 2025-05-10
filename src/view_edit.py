import flet as ft
from datetime import datetime


# ft.Viewを継承してクラス化
class ViewEdit(ft.View):
    # イニシャライザ定義
    def __init__(self, token_dict: dict, key: str):
        super().__init__()
        self.appbar = ft.AppBar(title=ft.Text("更新"))
        self.token_dict = token_dict
        self.key = key
        self.define_view_components()

    # OTPトークンの更新処理
    def event_edit_token(self, e):
        key = e.control.data

        # dict内のトークン情報の更新
        dt_now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.token_dict[key].update({
            "note": self.text_field_note.value,
            "updated_at": dt_now_str
        })

        # ページ移動処理
        self.page.go("/")

    # View内のUIオブジェクト定義
    # Note: 他のメソッドやイベントから呼び出されるものはselfつきで宣言
    def define_view_components(self):
        token_dict = self.token_dict
        key = self.key

        # 直接入力項目の作成
        text_field_user = ft.TextField(
            label="認証対象者", width=400, read_only=True,
            value=token_dict[key]["user"])
        text_field_secret = ft.TextField(
            label="秘密鍵", width=400, read_only=True,
            value=token_dict[key]["secret"])
        text_field_issuer = ft.TextField(
            label="発行者", width=400, read_only=True,
            value=token_dict[key]["issuer"])
        text_field_auth_uri = ft.TextField(
            label="認証URI", width=400, read_only=True,
            value=token_dict[key]["auth_uri"])

        # Note: Noteのみイベントから呼び出せるようにselfつきで宣言
        self.text_field_note = ft.TextField(
            label="説明文・メモ書き", width=400, multiline=True, min_lines=3,
            value=token_dict[key]["note"])

        # ボタンの定義
        button_edit_token = ft.CupertinoFilledButton(
            text="更新", data=key,
            on_click=lambda e: self.event_edit_token(e))

        # 行データの定義
        row_spacer = ft.Row(controls=[ft.Divider(height=10)])
        row_text_field_user = ft.Row(controls=[text_field_user])
        row_text_field_secret = ft.Row(controls=[text_field_secret])
        row_text_field_issuer = ft.Row(controls=[text_field_issuer])
        row_text_field_auth_uri = ft.Row(controls=[text_field_auth_uri])
        row_text_field_note = ft.Row(controls=[self.text_field_note])
        row_button_edit_token = ft.Row(controls=[button_edit_token])

        # Viewに対する行の追加
        self.controls.extend([
            row_text_field_user,
            row_text_field_secret,
            row_text_field_issuer,
            row_text_field_auth_uri,
            row_spacer,
            row_text_field_note,
            row_spacer,
            row_button_edit_token
        ])
