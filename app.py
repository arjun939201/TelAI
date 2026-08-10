import os

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from routes.language import router as language_router

from routes.chatbot import router as chatbot_router


app = FastAPI(
    title="TelAI",
    description="Simple AI Chatbot",
    version="1.0.0"
)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


templates = Jinja2Templates(
    directory=os.path.join(BASE_DIR, "templates")
)


app.mount(
    "/static",
    StaticFiles(
        directory=os.path.join(BASE_DIR, "static")
    ),
    name="static"
)


app.include_router(
    chatbot_router,
    prefix="/api",
    tags=["Chat"]
)

app.include_router(
    language_router,
    prefix="/api",
    tags=["Language"]
)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


@app.get("/health")
async def health():

    return {
        "status": "healthy",
        "service": "TelAI"
    }


if __name__ == "__main__":

    import uvicorn

    port = int(os.environ.get("PORT", 5000))

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port
    )
