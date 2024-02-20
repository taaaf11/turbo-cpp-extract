import asyncio
import glob
import io
import os
import zipfile
from pathlib import Path

import flet as ft
import requests


class BoldTextSpan(ft.TextSpan):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style = ft.TextStyle(weight=ft.FontWeight.BOLD)


class InstallTurbo(ft.Column):
    def __init__(
        self, page: ft.Page, turbo_download_link: str | None = None, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.turbo_dl_link = (
            turbo_download_link
            if turbo_download_link is not None
            else "https://github.com/taaaf11/turbo-c--for-download/raw/main/TURBOC3.zip"
        )

        self.start_btn = ft.FilledButton(text="Install!", on_click=self.start)

        # text to be displayed above progress bar
        self.prog_bar_text = ft.Text(weight=ft.FontWeight.BOLD, visible=False)
        self.progress_bar = ft.ProgressBar(
            opacity=0,
            animate_opacity=ft.animation.Animation(2000, ft.AnimationCurve.DECELERATE),
            visible=False,
        )

        self.logs_container = ft.Container(
            content=ft.ListView(auto_scroll=True, height=page.height / 4, expand=True),
            border=ft.border.all(2, ft.colors.SECONDARY_CONTAINER),
            border_radius=10,
            padding=10,
            opacity=0,
            visible=False,
            animate_opacity=ft.animation.Animation(2000, ft.AnimationCurve.DECELERATE),
        )

        self.controls = [
            self.start_btn,
            ft.Column(
                [
                    ft.Column(
                        [self.prog_bar_text, self.progress_bar],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    self.logs_container,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=30,
            ),
        ]

        self.turbo_file = b""

        self.spacing = 30

    async def do_log(self, log_: ft.TextSpan):
        self.logs_container.content.controls.append(ft.Text(spans=[log_]))
        await self.logs_container.update_async()

    async def reset_logs(self):
        self.logs_container.content.controls = []
        await self.update_async()

    async def start(self, e):
        await self.reset_logs()

        self.logs_container.visible = True
        self.progress_bar.visible = True

        self.logs_container.opacity = 1
        self.progress_bar.opacity = 1

        await self.progress_bar.update_async()

        await self.update_async()

        await self.download_turbo()
        await self.extract_turbo()
        await self.write_dosbox_conf()

        self.prog_bar_text.value = "Done!"
        self.progress_bar.opacity = 0

        await self.do_log(ft.TextSpan(spans=[BoldTextSpan("Done!")]))

        await self.update_async()

    async def download_turbo(self):
        self.prog_bar_text.value = "Downloading: TURBOC3.zip"
        self.progress_bar.visible = True
        self.prog_bar_text.visible = True

        await self.update_async()

        await self.do_log(
            ft.TextSpan(
                spans=[
                    ft.TextSpan("Downloading "),
                    BoldTextSpan("TurboC3.zip "),
                    ft.TextSpan("from "),
                    BoldTextSpan(self.turbo_dl_link),
                    ft.TextSpan("\n"),
                ]
            )
        )
        await self.logs_container.update_async()

        r = await asyncio.to_thread(requests.get, self.turbo_dl_link, stream=True)

        recvd_len = 0
        tot_len = int(r.headers.get("content-length"))

        for data in r.iter_content(tot_len // 100):
            recvd_len += len(data)
            self.progress_bar.value = recvd_len / tot_len
            self.turbo_file += data
            await self.progress_bar.update_async()

    async def extract_turbo(self):
        self.progress_bar.value = 0
        await self.progress_bar.update_async()

        documents_dir = os.path.join(Path.home(), "Documents")

        workdir_path = os.path.join(documents_dir, "TURBOC3_extract_dir")

        try:
            os.mkdir(workdir_path)
        except FileExistsError:
            await self.do_log(
                ft.TextSpan(
                    spans=[
                        ft.TextSpan(f"Directory "),
                        BoldTextSpan(workdir_path),
                        ft.TextSpan(" already exists\n"),
                    ]
                )
            )
            return

        buff = io.BytesIO(self.turbo_file)

        with zipfile.ZipFile(buff) as file:
            extracted_size = 0
            tot_size = len(self.turbo_file)

            for info in file.infolist():
                filename = info.filename
                filename_compressed_size = info.compress_size

                self.prog_bar_text.value = f"Extracting: {filename}"
                await self.do_log(
                    ft.TextSpan(
                        spans=[
                            ft.TextSpan("Extracting: "),
                            BoldTextSpan(f"{filename}\n"),
                        ]
                    )
                )

                file.extract(info.filename, path=workdir_path)
                extracted_size += filename_compressed_size

                self.progress_bar.value = round(extracted_size / tot_size, 1)

                await self.update_async()

        self.prog_bar_text.value = ""

        await self.update_async()

    async def write_dosbox_conf(self):
        await self.do_log(
            ft.TextSpan(spans=[ft.TextSpan("Writing configuration files...\n")])
        )

        dosbox_config_dir = os.path.join(os.environ["LOCALAPPDATA"], "DOSBox")
        if not os.path.exists(dosbox_config_dir):
            self.controls.append(ft.Text("Please install dosbox, then try again..."))
            await self.update_async()

        conf_file_path = glob.glob(os.path.join(dosbox_config_dir, "dosbox*.conf"))[0]

        with open(conf_file_path, "r+") as self.conf_file:
            old_conf = self.conf_file.read()
            last_5_lines = old_conf.split("\n")[-5:]

            # user has already run the program before
            if last_5_lines == [
                "[autoexec]",
                f"mount c {Path.home()}\\Documents\\TURBOC3_extract_dir",
                "c:",
                "cd TURBOC3\\BIN",
                "tc.exe",
            ]:
                return

            self.conf_file.seek(0)

            with open(f"{conf_file_path}.bak", "w") as backup_file:
                backup_file.write(old_conf)

            new_config = (
                "[autoexec]\n"
                f"mount c {Path.home()}\\Documents\\TURBOC3_extract_dir\n"
                "c:\n"
                "cd TURBOC3\\BIN\n"
                "tc.exe"
            )
            self.conf_file.write(new_config)
