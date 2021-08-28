import os
import tarfile


class Tar:
    @staticmethod
    def unpack(
            path: str,
            path_target: str = '',
            unpack_files: str = '',
            replace_files: bool = False,
    ):

        """
        Unpacks .tar archive files iteratively
        :param path: path to .tar file
        :param path_target: path to extract
        :param unpack_files: base path in .tar to extract
        :param replace_files: flag for rewrite files with same names
        :return: True for success
        """

        try:
            # Open tar archive
            with tarfile.open(path, 'r:*') as f_tar:
                # Process all files in archive
                for tarinfo in f_tar:
                    # File don't compare pattern
                    if not tarinfo.name.startswith(unpack_files):
                        continue

                    # File exists
                    if not replace_files and os.path.exists(f'{path_target}/{tarinfo.name}'):
                        continue

                    f_tar.extract(tarinfo, path_target)

            return True

        except Exception as e:
            raise e
