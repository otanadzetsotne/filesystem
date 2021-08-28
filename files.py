import os
import shutil
import platform
import asyncio
from typing import List
from pathlib import Path

import aiofile
import aiohttp
from aiohttp.web_exceptions import HTTPError


class Web:
    @staticmethod
    def url_to_file_name(
            url: str,
    ):
        """
        Transform url to file name
        :param url: file url
        :return: file name
        """

        return Path(url).name


class Files:
    web = Web

    @staticmethod
    def __check_copy_prefix(
            prefix: str,
    ):
        """
        Check functions arguments
        :param prefix: prefix for recurring file names
        :return: void
        """

        if len(prefix) == 0:
            raise ValueError('copy_prefix argument can not be empty string if replace_files argument is False')

    @classmethod
    def __file_copy_name(
            cls,
            copy_prefix: str,
            file_name: str,
            path: str,
    ):
        """
        Generates unique file name with prefix
        :param copy_prefix: file name prefix
        :param file_name: base file name
        :param path: path to file directory
        :return: new path
        """

        # Throw Error if prefix is empty
        cls.__check_copy_prefix(copy_prefix)

        while os.path.exists(f'{path}/{file_name}'):
            file_name = f'{copy_prefix}{file_name}'

        return file_name

    @classmethod
    def flatten(
            cls,
            path_base: str,
            path_current: str = '',
            replace_files: bool = True,
            copy_prefix: str = 'cp_',
    ):
        """
        Flattens directory's inner file structure
        :param path_base: path to root dir
        :param path_current: current working dir
        :param replace_files: flag for rewrite files with same names
        :param copy_prefix: copied files prefix
        :return True for success
        """

        # Iter each file/directory in current directory
        for path_target in os.listdir(f'{path_base}/{path_current}'):
            # Target file/directory to process
            path_target_abs = f'{path_base}/{path_current}/{path_target}'.replace('//', '/')

            # If target is directory, then call that func recursive
            if os.path.isdir(path_target_abs):
                cls.flatten(
                    path_base,
                    f'{path_current}/{path_target}',
                    replace_files,
                    copy_prefix,
                )
            else:
                # If file already is in base directory
                if path_target_abs == f'{path_base}/{path_target}':
                    continue

                # If replace files is False we add prefix to filename
                while not replace_files and os.path.exists(f'{path_base}/{path_target}'):
                    path_target = f'{copy_prefix}{path_target}'

                if not replace_files:
                    path_target = cls.__file_copy_name(copy_prefix, path_target, path_base)

                # Move file to base directory
                shutil.move(path_target_abs, f'{path_base}/{path_target}')

        # Remove directory
        if path_current:
            os.rmdir(f'{path_base}/{path_current}')

            return True

    @classmethod
    async def __download(
            cls,
            url: str,
            path: str,
            replace_files: bool,
            copy_prefix: str,
            semaphore: asyncio.locks.BoundedSemaphore,
    ):
        """
        Async download file
        :param url: url to file
        :param path: path to save file
        :param replace_files: enable non unique files replace
        :param copy_prefix: file name prefix for non unique files
        :param semaphore: semaphore \(0_0)/
        :return:
        """

        # Async download file
        async with semaphore, aiohttp.ClientSession() as session:
            # Make request
            async with session.get(url) as response:
                # Check status
                if response.status != 200:
                    raise HTTPError()

                # Download file
                data = await response.read()

            # Base file name
            file_name = cls.web.url_to_file_name(url)
            # Copy file name
            file_name = file_name if replace_files else cls.__file_copy_name(copy_prefix, file_name, path)
            # Absolute path to file
            file_path = os.path.join(path, file_name)
            # Save file
            async with aiofile.async_open(file_path, 'wb+') as f_aio:
                await f_aio.write(data)

    @classmethod
    def download_map(
            cls,
            urls: List[str],
            path: str = '',
            replace_files: bool = False,
            copy_prefix: str = 'cp_',
    ):
        """
        Download remote files to local file system
        :param urls: list of files to download
        :param path: directory to store files
        :param replace_files: flag for rewrite files with same names
        :param copy_prefix: copied files prefix
        :return:
        """

        try:
            semaphore = asyncio.BoundedSemaphore(10)
            loop = asyncio.get_event_loop()
            tasks = [loop.create_task(cls.__download(url, path, replace_files, copy_prefix, semaphore)) for url in urls]
            loop.run_until_complete(asyncio.wait(tasks))
            loop.close()
        except RuntimeError as e:
            # Windows specific error patch
            if platform.system() != 'Windows' or str(e) != 'Event loop is closed':
                raise


if __name__ == '__main__':
    urls_list = [
        'http://img.gazeta.ru/files3/501/12982501/upload-05-pic905v-895x505-22420.jpg',
        'https://icdn.lenta.ru/images/2020/11/15/14/20201115143852578/pwa_vertical_1280_6027c3a00df85e12c17887301d8dec32.jpg',
    ]

    Files.download_map(urls_list, '', True)
