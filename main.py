from fastapi import FastAPI
import uvicorn

from src import views, models, session


models.Base.metadata.create_all(bind=session.engine)

app = FastAPI()
app.include_router(views.router)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        log_level="info",
        reload=True,
        debug=True
    )
