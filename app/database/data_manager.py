#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

import logging
from contextlib import contextmanager

import mysql.connector as database
from loguru import logger

from config import config
from models.path import PathModel


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
        cursor = self.connection.cursor(*args, **kwargs)
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

    def save_path(self, path_model: PathModel):
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
            params = (path_model.path, path_model.extension, path_model.name, path_model.owner,
                      path_model.group, path_model.root, path_model.drive, path_model.size_in_mb,
                      path_model.hash_md5, path_model.hash_sha256, path_model.is_windows_path,
                      path_model.hidden, path_model.archive, path_model.compressed,
                      path_model.encrypted, path_model.offline, path_model.readonly,
                      path_model.system, path_model.temporary, str(path_model.content_family),
                      path_model.mime_type, str(path_model.path_type), str(path_model.path_stage))
            with self.cursor() as cur:
                cur.execute(sql_statement, params)
            logging.debug(f"Saved path '{path_model.path}'")
        except Exception as ex:
            logger.error(f"Unable to execute SQL command:\n{sql_statement}\nError: {ex}")

# if __name__ == '__main__':
#     adm = AmiDataManager()
#     adm.save_path()
