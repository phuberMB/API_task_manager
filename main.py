import logging
import logging.config
import time
from fastapi import FastAPI, Request, Response
from fastapi.routing import APIRouter
from routes.user import router as user_router
from routes.todo_list import router as todo_list_router
from routes.task import router as task_router
from routes.task_status import router as status_router
from routes.auth import router as auth_router


try:
    logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
except Exception:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(user_router)
app.include_router(todo_list_router)
app.include_router(task_router)
app.include_router(status_router)
app.include_router(auth_router)

router = APIRouter(prefix="/api/auth", tags=["auth"])

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info(f"Request: {request.method} {request.url.path}")
    try:
        response: Response = await call_next(request)
    except Exception as e:
        logger.exception(f"Exception during request: {request.method} {request.url.path} - {str(e)}")
        raise
    process_time = (time.time() - start_time) * 1000
    logger.info(
        f"Response: {request.method} {request.url.path} "
        f"Status: {response.status_code} "
        f"Time: {process_time:.2f}ms"
    )
    return response

@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to the Task Manager API!"}