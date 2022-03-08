import datetime as dt
import random
import shutil
from typing import Any
from typing import Generator
import os

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
import requests
import sqlalchemy
from sqlalchemy.orm import sessionmaker, Session

from src import models, schemas, views
from src.session import get_db


DATABASE_URL = "postgresql://postgres:admin@127.0.0.1:5432/test"
engine = sqlalchemy.create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
models.Base.metadata.drop_all(bind=engine)
models.Base.metadata.create_all(bind=engine)


@pytest.fixture
def test_db() -> Generator[Session, Any, None]:
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(test_db: Session) -> Generator[TestClient, Any, None]:
    def override_get_db() -> Generator[Session, Any, None]:
        yield test_db

    app = FastAPI()
    app.include_router(views.router)
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]


@pytest.fixture
def request_code() -> int:
    """
    Return random integer
    """

    return random.randint(0, 100_000)


@pytest.fixture
def random_files() -> list[bytes]:
    """
    Create random sized list of random bytes
    """

    size = random.randint(1, 16)

    return [random.randbytes(8) for __ in range(size)]


@pytest.fixture
def test_folder() -> Generator[str, Any, None]:
    """
    Override data folder
    Return folder name to write output to
    Remove the folder after all operations
    """

    folder = "test_data"
    views.DATA_PATH = folder

    yield folder
    shutil.rmtree(folder)


@pytest.fixture
def upload_files(
    client: TestClient, request_code: int, random_files: list[bytes], test_folder: str
):
    """
    Prepare test space by uploading files
    """

    files = [("images", file) for file in random_files]
    resp = client.put(f"frame/?request_code={request_code}", files=files)

    return resp


@pytest.fixture
def date() -> str:
    """
    Return current date as string in YYYYMMDD format
    """
    return dt.datetime.strftime(dt.datetime.today(), "%Y%m%d")


def test_create_files_expect_status_code_is_201(
    upload_files: requests.models.Response,
) -> None:
    """
    Check if response status code of /frame/<request_code> is 201
    """

    assert upload_files.status_code == 201


def test_create_files_expect_output_folder_is_created(
    upload_files: requests.models.Response, test_folder, date
) -> None:
    """
    Check if output folder have been created
    """

    assert os.path.isdir(
        os.path.join(test_folder, date)
    ), "Output folder does not exist"


def test_create_files_expect_identical_filenames_in_folder_and_in_database(
    upload_files: requests.models.Response,
    test_db: Session,
    date: str,
    test_folder: str,
) -> None:
    """
    Check if filenames in folder and in database is identical
    """

    # Get img schemas from database
    entries = test_db.query(models.Inbox).all()
    imgs = [schemas.ImageFile.from_orm(entry) for entry in entries]

    filenames = os.listdir(os.path.join(test_folder, date))
    img_names = [img.filename for img in imgs]

    assert set(filenames) == set(
        img_names
    ), "Mismatching filenames in folder and in database"


def test_create_files_expect_written_content_is_identical_to_uploaded_data(
    upload_files: requests.models.Response,
    date: str,
    test_folder: str,
    random_files: list[bytes],
) -> None:
    """
    Check if written images' content is identical to uploaded one
    """

    filenames = os.listdir(os.path.join(test_folder, date))

    for filename in filenames:
        with open(os.path.join(test_folder, date, filename), "rb") as written_img:
            # Check for inclusion due to file disorder
            assert written_img.read() in random_files


def test_create_files_expect_request_code_and_date_in_database_are_identical_to_uploaded(
    upload_files: requests.models.Response,
    date: str,
    test_db: Session,
    request_code: int,
) -> None:
    """
    Check if request_code and date is identical to given
    """

    entries = test_db.query(models.Inbox).all()
    imgs = [schemas.ImageFile.from_orm(entry) for entry in entries]

    for img in imgs:
        assert img.request_code == request_code, "Wrong database request code writing"

        assert dt.datetime.strftime(img.registration_date_time, "%Y%m%d") == date


def test_get_files(
    test_db: Session,
    upload_files: requests.models.Response,
    request_code: int,
    client: TestClient,
) -> None:
    """
    Check /frame/<request_code> get method

    Checks:
        * Correctness of returned by get method files' representations

    Make put request to upload files, than get them and check similarity
    """

    entries = test_db.query(models.Inbox).all()
    imgs = [schemas.ShowImageFile.from_orm(entry) for entry in entries]

    resp = client.get(f"frame/{request_code}")
    db_imgs = [
        schemas.ShowImageFile(**show_image_file) for show_image_file in resp.json()
    ]

    assert sorted(imgs, key=lambda img: img.filename) == sorted(
        db_imgs, key=lambda img: img.filename
    ), "Wrong get result"


def test_delete_files_expect_output_folder_is_empty(
    request_code: int,
    upload_files: requests.models.Response,
    client: TestClient,
    test_folder: str,
) -> None:
    """
    Check if files in output folder have been deleted
    """

    client.delete(f"frame/{request_code}")

    cur_date = dt.datetime.strftime(dt.datetime.today(), "%Y%m%d")
    written_files = os.listdir(os.path.join(test_folder, cur_date))
    assert written_files == [], "Files in output folder haven't been deleted"


def test_delete_files_expect_database_inbox_table_is_empty(
    test_db: Session,
    request_code: int,
    upload_files: requests.models.Response,
    client: TestClient,
) -> None:
    """
    Check if database entires have been deleted
    """

    client.delete(f"frame/{request_code}")

    imgs = test_db.query(models.Inbox).all()
    assert imgs == [], "Database entries haven't been deleted"
