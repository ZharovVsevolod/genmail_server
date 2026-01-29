# POSTGRES_URI=postgresql://postgres:postgres@localhost/tale REDIS_URI=redis://localhost:6379/ uv run -m celery --app=data_info_handler.document_handler.services.reader_tasks.celery_app worker  --concurrency=1 --pool=solo --loglevel=INFO

from celery.app import Celery
from os import environ
from uuid import UUID
from celery.utils.log import get_logger
from celery import Task
from celery.signals import after_task_publish, task_prerun, task_failure
from data_info_handler.document_handler.models import dbutils
from gm_services.schemas.document_handler import TranscriptionStatusEnum
from data_info_handler.document_handler.services.reader import Reader

logger = get_logger(__name__)

REDIS_URI = environ["REDIS_URI"]
celery_app = Celery(__name__, broker=REDIS_URI, backend=REDIS_URI)


@after_task_publish.connect
def task_sent_handler(sender=None, headers=None, body=None, **kwargs):
    info = headers if "task" in headers else body
    task_id = info["id"]
    logger.info("Published task %s", task_id)
    dbutils.set_transcription_task_status(
        UUID(task_id), TranscriptionStatusEnum.IN_QUEUE.value
    )


@task_prerun.connect
def task_prerun_handler(task_id=None, task=None, *args, **kwargs):
    logger.info("Prerun for task %s", task_id)
    dbutils.set_transcription_task_status(
        UUID(task_id), TranscriptionStatusEnum.PROCESSING.value
    )


@celery_app.task(bind=True)
def reader_task(self: Task, file_id: UUID, md5sum: bytes) -> None:
    logger_extras = {
        "task_id": self.request.id,
        "file_id": str(file_id),
        "md5sum": md5sum.hex(),
    }
    logger.info("Started", extra=logger_extras)

    logger.info("Getting data by md5sum", extra=logger_extras)
    data = dbutils.get_data_by_md5sum(md5sum)
    if data is None:
        logger.error(
            "Found md5sum (%s) for tasj %s, but can't find data",
            md5sum.hex(),
            file_id,
            extra=logger_extras,
        )
        raise Exception(f"Can't find data for file {str(file_id)}")

    logger.info("Getting content_type by md5sum", extra=logger_extras)
    content_type = dbutils.get_transcription_content_type_by_md5sum(md5sum)
    if content_type is None:
        logger.error(
            "Found md5sum (%s) for file %s, but can't find file_type",
            md5sum.hex(),
            file_id,
            extra=logger_extras,
        )
        raise Exception(f"Can't find file_type for file {str(file_id)}")
    logger_extras["content_type"] = content_type

    method = Reader.detect_method(content_type)
    logger.info("Chose method %s", extra=logger_extras)
    logger_extras["method"] = method

    logger.info("Converting to Page", extra=logger_extras)
    page = Reader.read(data, method)
    if page is None:
        logger.error("Reader result is None for file %s", file_id, extra=logger_extras)
        raise Exception(f"Can't read file {file_id}")

    logger.info("Dumping page to dict", extra=logger_extras)
    page_dict = page.model_dump()

    logger.info("Setting result in DB", extra=logger_extras)
    set_result = dbutils.set_transcription_task_content(
        UUID(self.request.id), page_dict
    )
    if not set_result:
        logger.error(
            "Can't set result for task %s", self.request.id, extra=logger_extras
        )
        raise Exception(f"Can't set results for task {self.request.id}")

    dbutils.set_transcription_task_status(
        UUID(self.request.id), TranscriptionStatusEnum.SUCCESS.value
    )
    logger.info("Task %s completed successfully", self.request.id, extra=logger_extras)


@task_failure.connect
def task_failure_handler(
    task_id=None,
    exception=None,
    traceback=None,
    einfo=None,
    *args,
    **kwargs,
):
    logger.exception("Task %s failed with exception %s", task_id, exception)
    dbutils.set_transcription_task_status(
        UUID(task_id), TranscriptionStatusEnum.ERROR.value
    )
