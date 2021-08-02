import os
import shutil


class Files:
    @classmethod
    def dir_flatten(
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

        try:
            # iter each file/directory in current directory
            for path_target in os.listdir(f'{path_base}/{path_current}'):
                # target file/directory to process
                path_target_abs = f'{path_base}/{path_current}/{path_target}'

                # if target is directory, then call that func recursive
                if os.path.isdir(path_target_abs):
                    cls.dir_flatten(
                        path_base,
                        f'{path_current}/{path_target}',
                        replace_files,
                        copy_prefix,
                    )
                else:
                    # if file already is in base directory
                    if path_target_abs == f'{path_base}/{path_target}':
                        continue

                    # if replace files is False we add prefix to filename
                    while not replace_files and os.path.exists(f'{path_base}/{path_target}'):
                        path_target = f'{copy_prefix}{path_target}'

                    # move file to base directory
                    shutil.move(path_target_abs, f'{path_base}/{path_target}')

            # remove directory
            if path_current:
                os.rmdir(f'{path_base}/{path_current}')

                return True

        except Exception as e:
            raise e
