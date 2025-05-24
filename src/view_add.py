import flet as ft
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse, parse_qsl
from PIL import Image
import pyzbar.pyzbar as pyzbar


# ft.Viewを継承してクラス化
class ViewAdd(ft.View):
    # イニシャライザ定義
    def __init__(self, token_dict: dict):
        super().__init__()
        self.appbar = ft.AppBar(title=ft.Text("新規登録"))
        self.token_dict = token_dict
        self.define_view_components()

    #
    # イベント定義
    #

    # QRコードチェックボックス切替時の動作定義
    def event_checkbox_enable_qrcode(self, e):
        value = e.control.value
        if value:
            self.button_select_qrcode_file.disabled = False
            self.text_field_qrcode_file_path.disabled = False
            self.text_field_user.read_only = True
            self.text_field_secret.read_only = True
            self.text_field_issuer.read_only = True
        else:
            self.button_select_qrcode_file.disabled = True
            self.text_field_qrcode_file_path.disabled = True
            self.text_field_user.read_only = False
            self.text_field_secret.read_only = False
            self.text_field_issuer.read_only = False

        self.update()

    # QRコード画像ファイルパスの指定
    def event_select_qrcode_filepath(self, e):
        if e.files:
            # ファイルパスの取得
            input_file_path = e.files[0].path
            self.text_field_qrcode_file_path.value = input_file_path
            self.text_field_qrcode_file_path.update()

            # QRコード画像の読み込み・OTP auth URI取得
            img = Image.open(input_file_path)
            decoded_objects = pyzbar.decode(img)
            if decoded_objects:
                # OTP auth URIの取得
                otp_auth_uri = decoded_objects[0].data.decode("utf-8")

                # 内容の解析および各入力項目への入力
                u = urlparse(otp_auth_uri)
                params = dict(parse_qsl(u.query))

                self.text_field_user.value = u.path[1:]
                self.text_field_secret.value = params["secret"]
                self.text_field_issuer.value = params["issuer"]
                self.text_field_auth_uri.value = otp_auth_uri
                self.switch_button_register_new_token()

                self.update()
            else:
                # 読み取り失敗時のダイアログ表示
                dialog = ft.AlertDialog(
                    content=ft.Text(
                        "有効なファイルをアップロードしてください。"),
                    actions=[ft.TextButton(
                        "OK",
                        on_click=lambda _: self.page.close(dialog))],
                    actions_alignment=ft.MainAxisAlignment.CENTER
                )
                self.page.open(dialog)
        else:
            print("Notice: QRコードファイル指定がキャンセルされました")

    # OTPトークンの新規登録処理
    def event_add_new_token(self):
        # dictへのトークン情報の追加
        dt_now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        token_item = {
            "index": len(self.token_dict) + 1,
            "user": self.text_field_user.value,
            "secret": self.text_field_secret.value,
            "issuer": self.text_field_issuer.value,
            "auth_uri": self.text_field_auth_uri.value,
            "note": self.text_field_note.value,
            "created_at": dt_now_str,
            "updated_at": dt_now_str
        }
        self.token_dict[self.text_field_user.value] = token_item

        # ページ移動処理
        self.page.go("/")

    # 新規登録ボタンの状態の切り替え
    def switch_button_register_new_token(self):
        disable_flag = not ( \
                    self.text_field_user.value != "" and \
                    self.text_field_secret.value != "" and \
                    self.text_field_issuer.value != "")
        self.button_add_new_token.disabled = disable_flag

    # View内のUIオブジェクト定義
    # Note: 他のメソッドやイベントから呼び出されるものはselfつきで宣言
    def define_view_components(self):
        token_dict = self.token_dict

        # FilePickerの定義
        # Note: viewもしくはpageへの追加がないとエラー発生
        dialog_select_qrcode_file = ft.FilePicker(
            on_result=self.event_select_qrcode_filepath)
        self.controls.append(dialog_select_qrcode_file)

        # QRコード項目の作成
        self.checkbox_enable_qrcode = ft.Checkbox(
            label="QRコード登録を利用", value=True,
            on_change=lambda e: self.event_checkbox_enable_qrcode(e)
        )
        self.text_field_qrcode_file_path = ft.TextField(
            label="QRコードファイルパス", width=400, read_only=True)
        self.button_select_qrcode_file = ft.ElevatedButton(
            "選択",
            on_click=lambda _: dialog_select_qrcode_file.pick_files(
                "QRコードファイル指定",
                allow_multiple=False,
                allowed_extensions=["jpg", "jpeg", "png", "gif"],
                initial_directory=str(Path.home()),
            )
        )

        # 直接入力項目の作成
        self.text_field_user = ft.TextField(
            label="認証対象者", width=400, read_only=True,
            on_change=lambda _: self.switch_button_register_new_token)
        self.text_field_secret = ft.TextField(
            label="秘密鍵", width=400, read_only=True,
            on_change=lambda _: self.switch_button_register_new_token)
        self.text_field_issuer = ft.TextField(
            label="発行者", width=400, read_only=True,
            on_change=lambda _: self.switch_button_register_new_token)
        self.text_field_auth_uri = ft.TextField(
            label="認証URI", width=400, read_only=True)
        self.text_field_note = ft.TextField(
            label="説明文・メモ書き", width=400,
            multiline=True, min_lines=3)

        # ボタンの定義
        self.button_add_new_token = ft.CupertinoFilledButton(
            text="新規登録", disabled=True,
            on_click=lambda _: self.event_add_new_token())

        # 行データの定義
        row_spacer = ft.Row(controls=[ft.Divider(height=10)])
        row_register_header = ft.Row(
            controls=[ft.Text("QRコード登録", size=20)])
        row_checkbox_enable_qrcode = ft.Row(
            controls=[self.checkbox_enable_qrcode])
        row_select_qrcode_file = ft.Row(
            controls=[self.text_field_qrcode_file_path,
                      self.button_select_qrcode_file])
        row_otp_token_info_header = ft.Row(
            controls=[ft.Text("OTPトークン情報", size=20)])
        row_text_field_user = ft.Row(
            controls=[self.text_field_user])
        row_text_field_secret = ft.Row(
            controls=[self.text_field_secret])
        row_text_field_issuer = ft.Row(
            controls=[self.text_field_issuer])
        row_text_field_auth_uri = ft.Row(
            controls=[self.text_field_auth_uri])
        row_text_field_note = ft.Row(
            controls=[self.text_field_note])
        row_button_add_new_token = ft.Row(
            controls=[self.button_add_new_token])

        # Viewに対する行の追加
        self.controls.extend([
            row_register_header,
            row_checkbox_enable_qrcode,
            row_select_qrcode_file,
            row_spacer,
            row_otp_token_info_header,
            row_text_field_user,
            row_text_field_secret,
            row_text_field_issuer,
            row_text_field_auth_uri,
            row_spacer,
            row_text_field_note,
            row_spacer,
            row_button_add_new_token,
        ])
