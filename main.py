from install_turbo import InstallTurbo
import flet as ft


async def main(page: ft.Page):
    page.title = "Turbo Setup"
    
    page.window_width = 747
    page.window_height = 483

    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    page.theme = ft.Theme(color_scheme_seed="Pink")
    await page.add_async(
        InstallTurbo(
            page=page,
            # alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            width=page.width / 2,
            spacing=20
        )
    )

    # page.on_resize = lambda _: print(page.window_width, page.window_height)


ft.app(main)
