import uvicorn
from fastapi import FastAPI, UploadFile, File, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from starlette.responses import FileResponse

from core.config import UVICORN_HOST, UVICORN_PORT
from file_manager import FileManager
from model import FileObjectModel
from mogodb_base import create_db_client, shutdown_db_client, get_database


app = FastAPI(title='DrWeb File Storage')
file_manager = FileManager()


@app.post("/upload_file/")
async def upload_file(file: UploadFile = File(...),
                      db: AsyncIOMotorClient = Depends(get_database)) -> FileObjectModel:
    """
    Load file in Store
    :param file: file object
    :param db: AsyncIOMotorClient
    :return: FileObjectModel
    """
    file_data = await file_manager.upload_file(file, db)
    return file_data


@app.get("/file/{file_id_hash}")
async def download_file(file_id_hash: str,
                        db: AsyncIOMotorClient = Depends(get_database)):
    """
    Download file by file_id_hash
    :param file_id_hash: hash string
    :param db: AsyncIOMotorClient
    :return: link for upload
    """
    file_description = await file_manager.download(file_id_hash, db)
    if file_description:
        file_desc = FileObjectModel(**file_description.dict())
        return FileResponse(media_type=file_desc.content_type,
                            path=file_desc.abs_path,
                            filename=f'{file_desc.hash_file}.{file_desc.file_extension}')
    return {"error": f"file with hash({file_id_hash}) not found"}


@app.delete("/file/{file_id_hash}")
async def delete_file(file_id_hash: str,
                      db: AsyncIOMotorClient = Depends(get_database)):
    """
    Delete file from Store and description file from db
    :param file_id_hash: hash string
    :param db: AsyncIOMotorClient
    :return:
    """
    desc = await file_manager.delete_file(file_id_hash, db)
    if desc:
        return {"response": f'file with hash({file_id_hash}) deleted'}
    return {"error": f"file with hash({file_id_hash}) not found"}


app.add_event_handler("startup", create_db_client)
app.add_event_handler("shutdown", shutdown_db_client)

if __name__ == "__main__":
    uvicorn.run(app=app, host=UVICORN_HOST, port=UVICORN_PORT)
