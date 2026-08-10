from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import PlainTextResponse

from services.language_knowledge import (
    LANGUAGE_DIR,
    get_language_files,
    read_language_knowledge
)


router = APIRouter(
    prefix="/language"
)


@router.get("/files")
async def list_files():

    return {
        "files": get_language_files()
    }


@router.get("/content/{filename}")
async def get_file_content(
    filename: str
):

    safe_name = Path(filename).name

    file = LANGUAGE_DIR / safe_name

    if not file.exists():
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    if not file.is_file():
        raise HTTPException(
            status_code=400,
            detail="Not a file"
        )

    return PlainTextResponse(
        file.read_text(
            encoding="utf-8"
        )
    )


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...)
):

    extension = Path(
        file.filename
    ).suffix.lower()

    if extension not in {
        ".txt",
        ".md",
        ".json",
        ".csv"
    }:

        raise HTTPException(
            status_code=400,
            detail="Unsupported file type"
        )


    LANGUAGE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    filename = Path(
        file.filename
    ).name


    destination = (
        LANGUAGE_DIR / filename
    )


    content = await file.read()


    destination.write_bytes(content)


    return {
        "success": True,
        "filename": filename
    }
