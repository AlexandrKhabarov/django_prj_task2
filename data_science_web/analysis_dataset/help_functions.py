from zipfile import ZipFile
import os


def compress_zip(archive, files):
    with ZipFile(archive, 'w') as compress:
        for file in files:
            compress.write(file, arcname=os.path.basename(file))


def get_all_abs_paths(path_dir):
    for f in os.listdir(path_dir):
        yield os.path.join(path_dir, f)
