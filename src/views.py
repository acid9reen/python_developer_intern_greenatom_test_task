import datetime as dt
import os
import shutil
import uuid

import fastapi
from fastapi import UploadFile, Depends
from sqlalchemy.orm import Session

from src import models, session, schemas


DATA_PATH = r"data/"

router = fastapi.APIRouter()


def save_files(
    files: list[UploadFile], img_names: list[str], time: dt.datetime
) -> None:
    """
    Save files as DATA_PATH/<date(YYYYMMDD)>/filename
    """

    cur_date = time.strftime("%Y%m%d")
    img_dir = os.path.join(DATA_PATH, cur_date)

    if not os.path.isdir(img_dir):
        os.makedirs(img_dir)

    for file, name in zip(files, img_names):
        with open(os.path.join(img_dir, name), "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)


def write_to_db(
    request_code: int, img_names: list[str], time: dt.datetime, db: Session
) -> None:
    """
    Construct Inbox models from input and write them to database.
    """

    entries = [
        models.Inbox(
            request_code=request_code, filename=img_name, registration_date_time=time
        )
        for img_name in img_names
    ]

    db.add_all(entries)
    db.commit()


@router.put("/frame/", status_code=201)
async def create_upload_files(
    request_code: int, images: list[UploadFile], db: Session = Depends(session.get_db)
) -> int:
    """
    Save the input files to a folder
    /data/<date in YYYYMMDD format>/ with names <GUID>.jpg
    and commit to the database in the inbox table
    with structure
    <request code> | <name of saved file> | <date/time of registration>.

    Return status code 201.
    """

    time = dt.datetime.today()
    img_names = [str(uuid.uuid4()) + ".jpg" for __ in images]

    save_files(images, img_names, time)
    write_to_db(request_code, img_names, time, db=db)

    return 201


@router.get("/frame/{request_code}", response_model=list[schemas.ShowImageFile])
async def get_files(request_code: int, db: Session = Depends(session.get_db)):
    """
    Return a list of images in JSON format (including
    date and time of registration and file names),
    matching request code.
    """

    imgs = (
        db.query(models.Inbox)
        .filter(models.Inbox.request_code == request_code)
        .all()
    )

    return imgs


@router.delete("/frame/{request_code}", response_model=list[schemas.ShowImageFile])
async def delete_files(request_code: int, db: Session = Depends(session.get_db)):
    """
    Delete data from the database and corresponding image from data/ folder,
    matching request code.
    """

    imgs = (
        db.query(models.Inbox)
        .filter(models.Inbox.request_code == request_code)
        .all()
    )

    files_to_delete = [
        os.path.join(
            DATA_PATH,
            img.registration_date_time.strftime("%Y%m%d"),
            img.filename
        ) for img in imgs
    ]

    for file in files_to_delete:
        os.remove(file)

    (db.query(models.Inbox)
       .filter(models.Inbox.request_code == request_code)
       .delete())

    db.commit()

    return imgs
