#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence
import time

if __name__ == '__main__':
    import sys, os
    root_folder = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(root_folder)

import json
import logging
from contextlib import contextmanager
from typing import List, Dict

import psycopg2 as database
from loguru import logger

from config import config
from models.content import ContentFamily, ContentCategory, ContentClassificationPegi
from models.path_stage import PathStage
from models.directory import DirectoryModel
from models.file import FileModel
from models.path import PathModel
from models.path_type import PathType


class PathDataManager:

    def __init__(self) -> None:
        super().__init__()
        try:
            logger.info(f"Connecting to DB {config.DATABASE_HOST}:{config.DATABASE_PORT}/{config.DATABASE_NAME}...")
            with self.cursor():
                logger.success(f"Connected to DB!")
        except Exception as ex:
            logger.error(f"Unable to login to DB {config.DATABASE_HOST}:{config.DATABASE_PORT}/{config.DATABASE_NAME}: {ex}")

    def create_cursor(self):
        connection = database.connect(
            user=config.DATABASE_USER,
            password=config.DATABASE_PASSWORD,
            host=config.DATABASE_HOST,
            port=config.DATABASE_PORT,
            database=config.DATABASE_NAME
        )
        cursor = connection.cursor()
        return cursor

    @contextmanager
    def cursor(self, *args, **kwargs):
        connection = database.connect(
            user=config.DATABASE_USER,
            password=config.DATABASE_PASSWORD,
            host=config.DATABASE_HOST,
            port=config.DATABASE_PORT,
            database=config.DATABASE_NAME
        )
        cursor = connection.cursor()
        try:
            yield cursor
        finally:
            try:
                if connection:
                    connection.commit()
                if cursor:
                    cursor.close()
            except Exception as ex:
                logger.error(ex)
                if connection:
                    connection.rollback()
                if cursor:
                    cursor.close()

    # def __del__(self):
    #     try:
    #         self.connection.commit()
    #     except Exception as ex:
    #         logger.error(f"Error while committing DB transaction: {ex}")
    #     finally:
    #         self.connection.close()

    def path_exists(self, path: str) -> bool:
        path: PathModel = self.get_path(path=path)
        return path is not None

    def _find_paths(self, column: str, operator: str, value, offset: int = 0, limit: int = 20) -> List[PathModel]:
        sql_statement: str = f'SELECT id, path, extension, name, owner, "group", root, drive, size, ' \
                             f'hash, is_windows_path, hidden, archive, compressed, encrypted, ' \
                             f'offline, readonly, system, temporary, content_family, mime_type, path_type, ' \
                             f'path_stage, date_created, date_updated ' \
                             f'FROM path ' \
                             f"WHERE {column} {operator} %s " \
                             f'LIMIT %s OFFSET %s'
        if isinstance(value, str):
            value = value.replace("'", "\'")
        args = [value, limit, offset]
        path_list: List[PathModel] = []
        try:
            with self.cursor() as cur:
                logger.debug(sql_statement)
                logger.debug(args)
                cur.execute(sql_statement, args)
                rows = cur.fetchall()
                if not rows:
                    return path_list
                for row in rows:
                    path = row[1]
                    root = row[6]
                    path_type = PathType(row[21])
                    if path_type == PathType.FILE:
                        path_model = FileModel(path=path, root=root)
                    elif path_type == PathType.DIRECTORY:
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
                    path_model.size = row[8]
                    path_model.hash = row[9]
                    path_model.is_windows_path = row[10]
                    path_model.hidden = row[11]
                    path_model.archive = row[12]
                    path_model.compressed = row[13]
                    path_model.encrypted = row[14]
                    path_model.offline = row[15]
                    path_model.readonly = row[16]
                    path_model.system = row[17]
                    path_model.temporary = row[18]
                    path_model.content_family = ContentFamily(row[19]) if row[19] else None
                    path_model.mime_type = row[20]
                    path_model.path_stage = PathStage(row[22]) if row[22] else None
                    path_model.date_created = row[23]
                    path_model.date_updated = row[24]
                    path_list.append(path_model)
                    logging.debug(f"Fetched path '{path}'")
            logging.info(f"Fetched {len(path_list)} paths")
            return path_list
        except Exception as ex:
            logger.error(f"_find_paths - Unable to execute SQL command:\n{sql_statement}\nError: {ex}\nwhere_clause: '{column} {operator} {value}'")
            return path_list

    def _get_path_by(self, column: str, operator: str, value) -> PathModel:
        path_list: List[PathModel] = self._find_paths(column=column, operator=operator, value=value)
        if len(path_list) > 1:
            raise ValueError(f"_get_path_by - More than one path found for where clause '{column} {operator} {value}'")
        elif len(path_list) == 0:
            return None
        else:
            return path_list[0]

    def get_path(self, path: str) -> PathModel:
        return self._get_path_by(column='path', operator='=', value=path)

    def find_paths_by_hash(self, hash: str) -> List[PathModel]:
        return self._find_paths(column='hash', operator='=', value=hash)

    def find_paths_by_prefix_and_name(self, path_prefix: str, name: str, mime_type: str) -> List[PathModel]:
        path_prefix = path_prefix.replace("'", "\'")
        name = name.replace("'", "\'")
        sql_statement: str = f'SELECT id, path, extension, name, owner, "group", root, drive, size, ' \
                             f'hash, is_windows_path, hidden, archive, compressed, encrypted, ' \
                             f'offline, readonly, system, temporary, content_family, mime_type, path_type, ' \
                             f'path_stage, date_created, date_updated ' \
                             f'FROM path ' \
                             f"WHERE path like '{path_prefix}%' and name like '%{name}%' and mime_type like '{mime_type}/%'"
        path_list: List[PathModel] = []
        try:
            with self.cursor() as cur:
                logger.debug(sql_statement)
                cur.execute(sql_statement)
                rows = cur.fetchall()
                if not rows:
                    return path_list
                for row in rows:
                    path = row[1]
                    root = row[6]
                    path_type = PathType(row[21])
                    if path_type == PathType.FILE:
                        path_model = FileModel(path=path, root=root)
                    elif path_type == PathType.DIRECTORY:
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
                    path_model.size = row[8]
                    path_model.hash = row[9]
                    path_model.is_windows_path = row[10]
                    path_model.hidden = row[11]
                    path_model.archive = row[12]
                    path_model.compressed = row[13]
                    path_model.encrypted = row[14]
                    path_model.offline = row[15]
                    path_model.readonly = row[16]
                    path_model.system = row[17]
                    path_model.temporary = row[18]
                    path_model.content_family = ContentFamily(row[19]) if row[19] else None
                    path_model.mime_type = row[20]
                    path_model.path_stage = PathStage(row[22]) if row[22] else None
                    path_model.date_created = row[23]
                    path_model.date_updated = row[24]
                    path_list.append(path_model)
                    logging.debug(f"Fetched path '{path}'")
            logging.info(f"Fetched {len(path_list)} paths")
            return path_list
        except Exception as ex:
            logger.error(
                f"_find_paths - Unable to execute SQL command:\n{sql_statement}\nError: {ex}\nwhere_clause: '{column} {operator} {value}'")
            return path_list

    def find_duplicates(self) -> Dict[str, List]:
        sql_statement: str = ('Select p.size, p.hash, p.path '
                              'FROM path p '
                              'Inner Join path p1 on p.size = p1.size '
                              ' AND p.hash = p1.hash AND p.path <> p1.path '
                              'Where p.hash <> '' AND p.hash IS NOT NULL '
                              'Order By p.size DESC, p.hash, p.path')
        result: Dict[str, List] = {}
        try:
            with self.cursor() as cur:
                cur.execute(sql_statement)
                rows = cur.fetchall()
                if not rows:
                    return result
                for row in rows:
                    size = row[0]
                    hash = row[1]
                    path = row[2]
                    values = result.get(hash, [])
                    values.append((path, size))
        except Exception as ex:
            logger.error(f"find_duplicates - Unable to execute SQL command:\n{sql_statement}\nError: {ex}")
        return result

    def _save_path(self, cursor, full_path: str, extension: str | None, name: str, is_dir: bool,
                   files_in_dir: int | None, size: int | None, stage: PathStage, category: ContentCategory,
                   min_age: ContentClassificationPegi) -> None:
        sql_statement: str = f'INSERT INTO path (path, extension, name, path_type, files_in_dir, size, ' \
                             f'path_stage, content_category, content_min_age) ' \
                             f'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s) ' \
                             f'ON CONFLICT(path) DO UPDATE SET extension=EXCLUDED.extension, name=EXCLUDED.name, ' \
                             f'path_type=EXCLUDED.path_type, files_in_dir=EXCLUDED.files_in_dir, size=EXCLUDED.size, ' \
                             f'path_stage=EXCLUDED.path_stage, content_category=EXCLUDED.content_category, ' \
                             f'content_min_age=EXCLUDED.content_min_age, ' \
                             f'date_updated=now()'
        params = (full_path,
                  extension,
                  name,
                  PathType.DIRECTORY.value if is_dir else PathType.FILE.value,
                  files_in_dir,
                  size,
                  stage.value if stage else None,
                  category.value if category else None,
                  min_age.value if min_age else None)
        try:
            logging.debug(f"Saved path '{full_path}' into DB")
            start = time.time()
            cursor.execute(sql_statement, params)
            end = time.time()
            duration = end - start
            if duration > 0.5:
                logger.warning(f"SLOW: took {duration}s for inserting path '{full_path}'")
        except Exception as ex:
            logger.error(f"Unable to execute SQL command:\n{sql_statement}\nError: {ex}\nPath: '{full_path}'")


def save_path(self, path_model: PathModel) -> None:
        sql_statement: str = f'INSERT INTO path (path, extension, name, owner, "group", root, drive, size, ' \
                             f'hash, is_windows_path, hidden, archive, compressed, encrypted, offline, ' \
                             f'readonly, system, temporary, content_family, mime_type, path_type, files_in_dir, tags, ' \
                             f'content_rating, path_stage, content_category, content_min_age) ' \
                             f'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ' \
                             f'%s, %s, %s, %s, %s, %s, %s, %s) ' \
                             f'ON CONFLICT(path) DO UPDATE SET extension=EXCLUDED.extension, name=EXCLUDED.name, ' \
                             f'owner=EXCLUDED.owner, "group"=EXCLUDED."group", root=EXCLUDED.root, drive=EXCLUDED.drive, ' \
                             f'size=EXCLUDED.size, hash=EXCLUDED.hash, ' \
                             f'is_windows_path=EXCLUDED.is_windows_path, hidden=EXCLUDED.hidden, archive=EXCLUDED.archive, ' \
                             f'compressed=EXCLUDED.compressed, encrypted=EXCLUDED.encrypted, offline=EXCLUDED.offline, ' \
                             f'readonly=EXCLUDED.readonly, system=EXCLUDED.system, temporary=EXCLUDED.temporary, ' \
                             f'content_family=EXCLUDED.content_family, mime_type=EXCLUDED.mime_type, ' \
                             f'path_type=EXCLUDED.path_type, path_stage=EXCLUDED.path_stage, tags=EXCLUDED.tags, ' \
                             f'content_rating=EXCLUDED.content_rating, ' \
                             f'files_in_dir=EXCLUDED.files_in_dir, ' \
                             f'content_category=EXCLUDED.content_category, content_min_age=EXCLUDED.content_min_age, ' \
                             f'date_updated=now()'
        try:
            params = (path_model.full_path, path_model.extension, path_model.name, path_model.owner,
                      path_model.group, path_model.path_root, path_model.drive, path_model.size,
                      path_model.hash, path_model.is_windows_path,
                      path_model.hidden, path_model.archive, path_model.compressed,
                      path_model.encrypted, path_model.offline, path_model.readonly,
                      path_model.system, path_model.temporary,
                      path_model.content_family.value if path_model.content_family else None,
                      str(path_model.mime_type) if path_model.mime_type else None, path_model.path_type.value,
                      path_model.files_in_dir if hasattr(path_model, 'files_in_dir') else None,
                      path_model.keywords if path_model.keywords else None,
                      path_model.content_rating.value if path_model.content_rating else None,
                      # json.dumps(path_model.tags) if path_model.tags else None,
                      path_model.path_stage.value,
                      path_model.content_category.value if path_model.content_category else None,
                      path_model.content_min_age.value if path_model.content_min_age else None)
            with self.cursor() as cur:
                start = time.time()
                cur.execute(sql_statement, params)
                end = time.time()
                duration = end - start
                if duration > 0.5:
                    logger.warning(f"SLOW: took {duration}s for inserting path '{path_model.full_path}'")
            logging.debug(f"Saved path '{path_model.full_path}' into DB")
        except Exception as ex:
            logger.error(f"Unable to execute SQL command:\n{sql_statement}\nError: {ex}\nPath: '{path_model.relative_path if path_model else 'None'}'")


# if __name__ == '__main__':
#     pdm = PathDataManager()
#     # res = pdm._find_paths()
#     res = pdm.get_path(path='/media/s....jpg')
#     print(res)
