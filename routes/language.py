from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import PlainTextResponse

from services.language_knowledge import (
    LANGUAGE_DIR,
    get_language_files,
)


router = APIRouter(
    prefix="/language"
)


ALLOWED_EXTENSIONS = {
    ".txt",
    ".md",
    ".json",
    ".csv",
}


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

    file_path = (
        LANGUAGE_DIR / safe_name
    )

    if not file_path.exists():

        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    if not file_path.is_file():

        raise HTTPException(
            status_code=400,
            detail="Not a file"
        )

    return PlainTextResponse(
        file_path.read_text(
            encoding="utf-8"
        )
    )


@router.post("/upload")
async def upload_file(
    request: Request
):

    filename = request.headers.get(
        "X-Filename"
    )


    if not filename:

        raise HTTPException(
            status_code=400,
            detail="Filename is required"
        )


    filename = Path(filename).name


    extension = Path(
        filename
    ).suffix.lower()


    if extension not in ALLOWED_EXTENSIONS:

        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Use .txt, .md, .json or .csv."
            )
        )


    LANGUAGE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    content = await request.body()


    if not content:

        raise HTTPException(
            status_code=400,
            detail="File is empty"
        )


    try:

        content.decode("utf-8")

    except UnicodeDecodeError:

        raise HTTPException(
            status_code=400,
            detail="Only UTF-8 text files are supported"
        )


    destination = (
        LANGUAGE_DIR / filename
    )


    destination.write_bytes(
        content
    )


    return {
        "success": True,
        "filename": filename
    }
