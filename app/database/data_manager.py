#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

import logging
from contextlib import contextmanager

import mysql.connector as database
from loguru import logger

from config import config
from models.directory import DirectoryModel
from models.file import FileModel
from models.path import PathModel
from models.path_type import PathType


class PathDataManager:

    def __init__(self) -> None:
        super().__init__()
        try:
            logger.info(f"Connecting to DB {config.DATABASE_HOST}:{config.DATABASE_PORT}/{config.DATABASE_NAME}...")
            self.connection = database.connect(
                user=config.DATABASE_USER,
                password=config.DATABASE_PASSWORD,
                host=config.DATABASE_HOST,
                port=config.DATABASE_PORT,
                database=config.DATABASE_NAME
            )
            logger.success(f"Connected to DB!")
        except Exception as ex:
            logger.error(
                f"Unable to login to DB {config.DATABASE_HOST}:{config.DATABASE_PORT}/{config.DATABASE_NAME}: {ex}")

    @contextmanager
    def cursor(self, *args, **kwargs):
        cursor = self.connection.cursor(buffered=True, *args, **kwargs)
        try:
            yield cursor
        finally:
            try:
                if self.connection:
                    self.connection.commit()
                if cursor:
                    cursor.close()
            except Exception as ex:
                logger.error(ex)
                if self.connection:
                    self.connection.rollback()
                if cursor:
                    cursor.close()

    def __del__(self):
        try:
            self.connection.commit()
        except Exception as ex:
            logger.error(f"Error while committing DB transaction: {ex}")
        finally:
            self.connection.close()

    def path_exists(self, path: str) -> bool:
        path: PathModel = self.get_path(path=path)
        return path is not None

    def get_path(self, path: str) -> PathModel:
        sql_statement: str = f'SELECT id, `path`, extension, name, owner, `group`, root, drive, size_in_mb, ' \
                             f'hash_md5, hash_sha256, is_windows_path, hidden, archive, compressed, encrypted, ' \
                             f'offline, readonly, `system`, `temporary`, content_family, mime_type, path_type, ' \
                             f'path_stage, date_created, date_updated ' \
                             f'FROM `path` WHERE `path` like %s'
        path_model: PathModel = None
        try:
            with self.cursor() as cur:
                cur.execute(sql_statement, [f"%{path}"])
                row = cur.fetchone()
                if not row:
                    return path_model

                path = row[1]
                root = row[6]
                if row[22] == PathType.FILE.name:
                    path_model = FileModel(path=path, root=root)
                elif row[22] == PathType.DIRECTORY.name:
                    path_model = DirectoryModel(path=path, root=root)
                else:
                    raise ValueError(f"The path type can not be defined: '{row[22]}' is neither a file, "
                                     f"nor a dictionary. Row: {row}")
                path_model.id = row[0]
                path_model.extension = row[2]
                path_model.name = row[3]
                path_model.owner = row[4]
                path_model.group = row[5]
                path_model.drive = row[7]
                path_model.size_in_mb = row[8]
                path_model.hash_md5 = row[9]
                path_model.hash_sha256 = row[10]
                path_model.is_windows_path = row[11].decode()
                path_model.hidden = row[12].decode()
                path_model.archive = row[13].decode()
                path_model.compressed = row[14].decode()
                path_model.encrypted = row[15].decode()
                path_model.offline = row[16].decode()
                path_model.readonly = row[17].decode()
                path_model.system = row[18].decode()
                path_model.temporary = row[19].decode()
                path_model.content_family = row[20]
                path_model.mime_type = row[21]
                path_model.path_stage = row[23]
                path_model.date_created = row[24]
                path_model.date_updated = row[25]
            logging.debug(f"Fetched path '{path}'")
            return path_model
        except Exception as ex:
            logger.error(f"Unable to execute SQL command:\n{sql_statement}\nError: {ex}\nPath: '{path}'")
            return path_model

    def save_path(self, path_model: PathModel) -> None:
        sql_statement: str = f'INSERT INTO `path` (`path`, extension, name, owner, `group`, root, drive, size_in_mb, ' \
                             f'hash_md5, hash_sha256, is_windows_path, hidden, archive, compressed, encrypted, offline, ' \
                             f'readonly, `system`, `temporary`, content_family, mime_type, path_type, path_stage) ' \
                             f'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ' \
                             f'%s, %s, %s)' \
                             f'ON DUPLICATE KEY UPDATE extension=VALUES(extension), name=VALUES(name), ' \
                             f'owner=VALUES(owner), `group`=VALUES(`group`), root=VALUES(root), drive=VALUES(drive), ' \
                             f'size_in_mb=VALUES(size_in_mb), hash_md5=VALUES(hash_md5), hash_sha256=VALUES(hash_sha256), ' \
                             f'is_windows_path=VALUES(is_windows_path), hidden=VALUES(hidden), archive=VALUES(archive), ' \
                             f'compressed=VALUES(compressed), encrypted=VALUES(encrypted), offline=VALUES(offline), ' \
                             f'readonly=VALUES(readonly), `system`=VALUES(`system`), `temporary`=VALUES(`temporary`), ' \
                             f'content_family=VALUES(content_family), mime_type=VALUES(mime_type), ' \
                             f'path_type=VALUES(path_type), path_stage=VALUES(path_stage), date_updated=sysdate()'
        try:
            params = (path_model.relative_path, path_model.extension, path_model.name, path_model.owner,
                      path_model.group, path_model.root, path_model.drive, path_model.size_in_mb,
                      path_model.hash_md5, path_model.hash_sha256, path_model.is_windows_path,
                      path_model.hidden, path_model.archive, path_model.compressed,
                      path_model.encrypted, path_model.offline, path_model.readonly,
                      path_model.system, path_model.temporary, str(path_model.content_family),
                      path_model.mime_type, str(path_model.path_type), str(path_model.path_stage))
            with self.cursor() as cur:
                cur.execute(sql_statement, params)
            logging.debug(f"Saved path '{path_model.full_path}' into DB")
        except Exception as ex:
            logger.error(
                f"Unable to execute SQL command:\n{sql_statement}\nError: {ex}\nPath: '{path_model.relative_path if path_model else 'None'}'")

# if __name__ == '__main__':
#     adm = AmiDataManager()
#     adm.save_path()
