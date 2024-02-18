import asyncio
import glob
import io
import os
import zipfile
from pathlib import Path

import flet as ft
import requests


class InstallTurbo(ft.Column):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.start_button = ft.FilledButton(text="Install!", on_click=self.start)

        # text to be displayed above progress bar
        self.prog_bar_text = ft.Text(weight=ft.FontWeight.BOLD, visible=False)
        self.progress_bar = ft.ProgressBar(
            animate_opacity=ft.animation.Animation(800, ft.AnimationCurve.DECELERATE),
            visible=False,
        )

        self.controls = [
            self.start_button,
            ft.Column(
                [self.prog_bar_text, self.progress_bar],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        ]

        self.turbo_file = b""

    async def start(self, e):
        await self.download_turbo_installer()
        await self.extract_turbo()
        await self.write_dosbox_conf()

        self.prog_bar_text.value = "Done!"
        self.progress_bar.opacity = 0

        await self.update_async()

    async def download_turbo_installer(self):
        self.prog_bar_text.value = "Downloading: TURBOC3.zip"
        self.progress_bar.visible = True
        self.prog_bar_text.visible = True

        await self.update_async()

        turbo_download_link = (
            "https://github.com/taaaf11/turbo-c--for-download/raw/main/TURBOC3.zip"
        )
        r = await asyncio.to_thread(requests.get, turbo_download_link, stream=True)

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

        try:
            workdir_path = os.path.join(documents_dir, "TURBOC3_extract_dir")
            os.mkdir(workdir_path)
        except FileExistsError:
            return

        buff = io.BytesIO(self.turbo_file)

        with zipfile.ZipFile(buff) as file:
            extracted_size = 0
            tot_size = len(self.turbo_file)

            for info in file.infolist():
                filename = info.filename
                filename_compressed_size = info.compress_size

                self.prog_bar_text.value = f"Extracting: {filename}"

                file.extract(info.filename, path=workdir_path)
                extracted_size += filename_compressed_size

                self.progress_bar.value = round(extracted_size / tot_size, 1)

                await self.update_async()

        self.prog_bar_text.value = ""

        await self.update_async()

    async def write_dosbox_conf(self):
        dosbox_config_dir = os.path.join(os.environ["LOCALAPPDATA"], "DOSBox")
        if not os.path.exists(dosbox_config_dir):
            self.controls.append(ft.Text("Please install dosbox, then try again..."))
            await self.update_async()

        conf_file_path = glob.glob(os.path.join(dosbox_config_dir, "dosbox*.conf"))[0]

        with open(conf_file_path, "r+") as conf_file:
            old_conf = conf_file.read()
            conf_file.seek(0)

            with open(f"{conf_file_path}.bak", "w") as old_backup:
                old_backup.write(old_conf)

            new_config = (
                "[autoexec]\n"
                f"mount c {Path.home()}\\Documents\\TURBOC3_extract_dir\n"
                "c:\n"
                "cd TURBOC3\n"
                "cd BIN\n"
                "tc.exe\n"
            )
            conf_file.write(new_config)
