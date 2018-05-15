from zipfile import ZipFile
import os


def compress_zip(archive, files):
    with ZipFile(archive, 'w') as compress:
        for file in files:
            compress.write(file, arcname=os.path.basename(file))


def get_all_abs_path(m_object):
    for path in m_object.__dict__.keys():
        try:
            yield getattr(m_object, path).path
        except AttributeError:
            pass
        except ValueError:
            pass
