import hashlib
import os

from fastapi import UploadFile
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient

from model import FileObjectModel


class FileManager(object):
    def __init__(self, store_dir: str = 'dr_web_store'):
        self.store_path = store_dir
        self.prefix_len_for_directory_file = 2
        self.collection_mongo = 'file_description'
        self.db_name = 'file_storage'
        if not os.path.exists(self.store_path):
            os.makedirs(self.store_path)

    async def upload_file(self, file_obj: UploadFile,
                          conn: AsyncIOMotorClient) -> FileObjectModel:
        """
        Upload file from http and convert name for hash file,
        and save file description in database.

        :param file_obj: UploadFile
        :param conn: AsyncIOMotorClient
        :return FileObjectModel (save in db)
        """

        file = FileObjectModel(start_file_name=file_obj.filename,
                               content_type=file_obj.content_type,
                               file_extension=file_obj.filename.split(".")[-1])
        file_data = file_obj.file.read()
        hash_file = hashlib.md5(file_data).hexdigest()
        directory_file = hash_file[0:self.prefix_len_for_directory_file]
        current_directory = os.path.join(self.store_path, directory_file)

        if not os.path.exists(current_directory):
            os.makedirs(os.path.join(current_directory))
            logger.info(f"create directory new directory {os.path.join(current_directory)}")
        with open(os.path.join(self.store_path, directory_file, hash_file), 'w') as f:

            # work for file with extension .txt
            try:
                f.write(file_data.decode('utf-8'))
            except BaseException as e:
                # if byte 0xff in position 0 use 'utf-16'
                f.write(file_data.decode('utf-16'))
                logger.info(e)

        logger.info(f'file saved in {os.path.join(self.store_path, directory_file, hash_file)}')
        file.abs_path_directory = current_directory
        file.abs_path = os.path.join(self.store_path, directory_file, hash_file)
        file.hash_file = hash_file

        # save file description in db
        await conn[self.db_name][self.collection_mongo].insert_one(file.dict())
        return file

    async def download(self, hash_file_id: str,
                       conn: AsyncIOMotorClient) -> FileObjectModel or None:
        """
        Download file by hash_file_id in db -> return file description (FileObjectModel)
        else return None if file not found in db.

        :param hash_file_id: hash string
        :param conn: AsyncIOMotorClient
        :return FileObjectModel or None
        """
        description_file = await conn[self.db_name][self.collection_mongo].find_one(
            {'hash_file': hash_file_id})
        if description_file:
            file_desc = FileObjectModel(**description_file)

            if os.path.exists(file_desc.abs_path):
                logger.info(f"load file from {file_desc.abs_path}")
                return file_desc
        return None

    async def delete_file(self, hash_file_id: str,
                          conn: AsyncIOMotorClient) -> bool:
        """
        Delete file by hash_file_id and remove directory file
        :param hash_file_id: hash string
        :param conn: AsyncIOMotorClient
        :return: True or False
        """
        description_file = await conn[self.db_name][self.collection_mongo].find_one(
            {'hash_file': hash_file_id})
        if description_file:
            file_desc = FileObjectModel(**description_file)
            if os.path.exists(file_desc.abs_path):
                try:
                    os.remove(file_desc.abs_path)
                    logger.info(f"delete file with abs_path {file_desc.abs_path}")
                except BaseException as e:
                    logger.info(e)

                try:
                    os.rmdir(file_desc.abs_path_directory)
                    logger.info(f"delete directory {file_desc.abs_path_directory}")
                except BaseException as e:
                    logger.info(e)
                    logger.info(f"this directory {file_desc.abs_path_directory} is not empty")

                await conn[self.db_name][self.collection_mongo].delete_many(
                    {'hash_file': hash_file_id})
                return True
        logger.info(f"file with hash_file_id {hash_file_id} not in data")
        return False
