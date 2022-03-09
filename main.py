from fastapi import FastAPI
import uvicorn

from src import views, models, session


models.Base.metadata.create_all(bind=session.engine)

app = FastAPI()
app.include_router(views.router)
