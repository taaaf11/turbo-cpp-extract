from install_turbo import InstallTurbo
import flet as ft


async def main(page: ft.Page):
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    page.theme = ft.Theme(color_scheme_seed="Pink")
    await page.add_async(
        InstallTurbo(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            width=page.width / 2,
            spacing=20
        )
    )


ft.app(main)
