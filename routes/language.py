from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import PlainTextResponse

from services.language_knowledge import (
    LANGUAGE_DIR,
    get_language_files,
)


router = APIRouter()


# ============================================================
# LANGUAGE FILE LIST
# ============================================================

@router.get("/language/files")
async def list_language_files():

    return {
        "files": get_language_files()
    }


# ============================================================
# LANGUAGE FILE CONTENT
# ============================================================

@router.get(
    "/language/content/{filename}",
    response_class=PlainTextResponse
)
async def get_language_content(
    filename: str
):

    # Prevent directory traversal.
    safe_name = Path(filename).name

    if safe_name != filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename."
        )

    file_path = LANGUAGE_DIR / safe_name

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Language file not found."
        )

    if not file_path.is_file():
        raise HTTPException(
            status_code=400,
            detail="Invalid language file."
        )

    try:

        return file_path.read_text(
            encoding="utf-8"
        )

    except OSError:

        raise HTTPException(
            status_code=500,
            detail="Unable to read language file."
        )


# ============================================================
# LANGUAGE FILE UPLOAD
# ============================================================

@router.post("/language/upload")
async def upload_language_file(
    request: Request
):

    filename = request.headers.get(
        "X-Filename"
    )

    if not filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required."
        )

    safe_name = Path(filename).name

    if safe_name != filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename."
        )

    if not safe_name.endswith(".txt"):
        raise HTTPException(
            status_code=400,
            detail="Only .txt files are allowed."
        )

    LANGUAGE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    file_path = LANGUAGE_DIR / safe_name

    content = await request.body()

    try:

        file_path.write_bytes(
            content
        )

    except OSError:

        raise HTTPException(
            status_code=500,
            detail="Unable to save language file."
        )

    return {
        "success": True,
        "filename": safe_name
    }
