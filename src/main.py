import flet as ft
import os
import json
import qrcode
import pyotp
import pyperclip
from pathlib import Path
from urllib.parse import urlparse, parse_qsl

from otp_text import OtpText
from otp_timebar import OtpTimeBar
from view_add import ViewAdd
from view_edit import ViewEdit


# 保存先のパス情報の取得
def get_app_data_path() -> Path:
    # アプリ用のデータパス
    # Note:
    #   最初はFlet標準の環境変数を取得
    #   環境変数の設定がない場合はホームディレクトリ以下のフォルダを指定
    flet_env_path = os.getenv("FLET_APP_STORAGE_DATA")
    if flet_env_path is not None:
        return Path(flet_env_path)
    else:
        home_path = Path.home()
        return home_path.joinpath("flet_data")


# main関数
def main(page: ft.Page):
    # トップページ設定
    page.title = "Authenticatorもどき"
    page.appbar = ft.AppBar(title=ft.Text("Authenticatorもどき"),
        actions=[ft.IconButton(ft.Icons.ADD, on_click=lambda _: page.go("/add"))]
    )

    # ウィンドウサイズの設定
    page.window.width = 520
    page.window.height = 920

    # アプリ用のデータパス
    # Note: Fletの標準の保存用パスを利用
    app_data_path = get_app_data_path()
    token_data_json_path = app_data_path.joinpath("token_data.json")

    # トークン情報のファイル読み込みおよびdictの初期化
    token_data_dict = {}
    if token_data_json_path.exists():
        with open(token_data_json_path, "r", encoding="utf-8") as f:
            token_data_dict = json.load(f)

    # JSONファイルへの保存
    def save_token_data_json():
        # データ保存用のフォルダ作成
        if not app_data_path.exists():
            app_data_path.mkdir()

        # 並び順の保存
        # Note: 検索条件によってListView上の数が減少している場合は値を保存しない
        if len(token_data_dict) == len(list_view_token_info.controls):
            for index, container in enumerate(list_view_token_info.controls, start=1):
                key = container.data
                token_data_dict[key]["index"] = index

        # ファイルの保存処理
        with open(token_data_json_path, "w", encoding="utf-8") as f:
            json_str = json.dumps(token_data_dict, indent=4)
            f.write(json_str)

    # トークン情報描画処理
    def update_token_info_containers(query=""):
        list_view_items_list = []

        # 行データの再描画処理
        for key, info in sorted(token_data_dict.items(), key=lambda x: x[1]["index"]):
            if query == "" or query in info["user"]:
                # OTP情報の行データ定義
                # Note: 名称表示に加えて、QRコードDL・編集・削除ボタンを設定
                row_top = ft.Row(controls=[
                    ft.Text(info["user"], width=300, size=16),
                    ft.IconButton(ft.Icons.QR_CODE, data=key,
                                  on_click=lambda e: dialog_select_qrcode_save_path.save_file(
                                        "QRコード画像保存先の指定",
                                        allowed_extensions=["png"])),
                    ft.IconButton(ft.Icons.EDIT, data=key,
                                  on_click=lambda e: event_click_edit_button(e)),
                    ft.IconButton(ft.Icons.REMOVE, data=key,
                                  on_click=lambda e: event_click_remove_button(e))
                ])
                row_otp = ft.Row(controls=[OtpText(info["secret"])])
                row_spacer1 = ft.Row(controls=[ft.Divider(height=15)])
                row_spacer2 = ft.Row(controls=[ft.Divider(height=30)])

                # OTPの有効期限を表示する残り時間のバー表示
                row_otp_time_bar = ft.Row(controls=[OtpTimeBar()])

                # Columnおよびコンテナの定義
                token_info_column = ft.Column(controls=[
                    row_top, row_otp, row_spacer1,
                    row_otp_time_bar, row_spacer2
                ])
                token_info_container = ft.Container(
                    content=token_info_column, data=key,
                    on_long_press=lambda e: event_long_press_token_info(e))

                # リストへの行追加
                list_view_items_list.append(token_info_container)

        list_view_token_info.controls = list_view_items_list
        list_view_token_info.update()

    # 検索時の動作
    def event_search_token_info(e):
        query = e.control.value
        update_token_info_containers(query)

    # QRコードファイル保存先パスの指定
    def event_save_qrcode(e: ft.FilePickerResultEvent):
        if e.path:
            # QRコード化対象情報の取得
            key = e.control.data
            auth_uri = token_data_dict[key]["auth_uri"]

            # QRコード画像生成と保存
            qr = qrcode.QRCode()
            qr.add_data(auth_uri)
            qr.make()
            img = qr.make_image()
            img.save(e.path)
        else:
            print("Notice: QRコード画像ファイル保存がキャンセルされました")

    def event_click_edit_button(e):
        key = e.control.data
        page.go("/edit", key=key)

    def event_click_remove_button(e):
        key = e.control.data

        # 確認のダイアログ表示
        dialog = ft.AlertDialog(
            content=ft.Text("このOTPトークンを削除しますか？"),
            actions=[
                ft.TextButton("Yes", on_click=lambda _: [
                                  token_data_dict.pop(key),
                                  update_token_info_containers(),
                                  page.close(dialog)]),
                ft.TextButton("No", on_click=lambda _: page.close(dialog))
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER
        )
        page.open(dialog)

    # 並び替え時の動作
    # Note: controls内の要素のindex入れ替え処理
    def event_sort_token_info(e):
        # 見た目上の入れ替え処理
        controls = e.control.controls
        controls[e.old_index], controls[e.new_index] = \
            controls[e.new_index], controls[e.old_index]

        # indexの入れ替え処理
        key1 = controls[e.old_index].data
        key2 = controls[e.new_index].data
        token_data_dict[key1]["index"], token_data_dict[key2]["index"] = \
            token_data_dict[key2]["index"], token_data_dict[key1]["index"]

        # ページの更新・index情報の保存
        page.update()
        save_token_data_json()

    # 長くクリックしたときの動作
    # Note: 現在のOTPの文字列をクリップボードに保存
    def event_long_press_token_info(e):
        key = e.control.data
        totp = pyotp.TOTP(token_data_dict[key]["secret"])
        current_otp = str(totp.now())
        pyperclip.copy(current_otp)
        page.open(ft.SnackBar(ft.Text("ワンタイムパスワードをコピーしました")))

    # routeごとの分岐処理
    def route_change(route: str):
        u = urlparse(page.route)
        path = u.path

        if path == "/":
            root_view = page.views[0]
            page.views.clear()
            page.views.append(root_view)
            update_token_info_containers()
            save_token_data_json()
        elif path == "/add":
            view_add = ViewAdd(token_data_dict)
            page.views.append(view_add)
        elif path == "/edit":
            params = dict(parse_qsl(u.query))
            view_edit = ViewEdit(token_data_dict, params["key"])
            page.views.append(view_edit)

        page.update()

    # Viewで戻るボタンを押した際の処理
    def view_pop(view):
        if len(page.views) > 1:
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)

    # ルート変更時・戻る際のロジックを設定
    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # FilePickerの定義
    # Note: appendによるpage/viewへの追加がないとエラー発生
    dialog_select_qrcode_save_path = ft.FilePicker(on_result=event_save_qrcode)
    page.overlay.append(dialog_select_qrcode_save_path)

    # 検索用テキストフィールドの追加
    text_field_query = ft.TextField(
        label="検索", width=400, on_submit=lambda e: event_search_token_info(e))
    row_text_field_query = ft.Row(controls=[text_field_query])
    page.add(row_text_field_query)

    # 表示用ListViewの定義と各行の表示
    list_view_token_info = ft.ReorderableListView(
        width=500, height=750, on_reorder=lambda e: event_sort_token_info(e))
    page.add(list_view_token_info)
    update_token_info_containers()

    # pageの表示
    page.update()


# main関数
if __name__ == "__main__":
    ft.app(target=main)
