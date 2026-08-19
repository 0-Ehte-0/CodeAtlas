# services/analyzer/codeatlas_analyzer/worker.py
import json
import os
import time
from datetime import datetime, timezone
import redis
from sqlalchemy import select

from codeatlas_observability import get_logger
from codeatlas_contracts.enums import IndexStatus
from codeatlas_queue.constants import INDEXING_QUEUE_NAME
from codeatlas_queue.payloads import IndexJobPayload

from codeatlas_analyzer.db import SessionLocal
from codeatlas_analyzer.discovery.scanner import discover_source_files
from apps.api.models import IndexJob

logger = get_logger("codeatlas.analyzer")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

def update_job_status(job_id: str, status: IndexStatus, error_message: str = None):
    with SessionLocal() as db:
        job = db.scalar(select(IndexJob).where(IndexJob.job_id == job_id))
        if job:
            job.status = status
            job.error_message = error_message
            job.updated_at = datetime.now(timezone.utc)
            db.commit()

def process_job(payload: IndexJobPayload):
    logger.info(f"Starting job {payload.job_id} for repository {payload.repository_id}")
    update_job_status(payload.job_id, IndexStatus.PROCESSING)

    try:
        # Phase 6: Source Discovery
        # For local repositories or local cloned paths:
        target_path = payload.clone_url if os.path.exists(payload.clone_url) else os.getcwd()
        
        discovered_files = discover_source_files(target_path)
        logger.info(f"Discovered {len(discovered_files)} source files in {target_path}")

        # Update Job to COMPLETED
        update_job_status(payload.job_id, IndexStatus.COMPLETED)
        logger.info(f"Job {payload.job_id} completed successfully")

    except Exception as e:
        logger.exception(f"Job {payload.job_id} failed: {str(e)}")
        update_job_status(payload.job_id, IndexStatus.FAILED, error_message=str(e))

def start_worker():
    logger.info(f"Analyzer worker started. Listening on queue: {INDEXING_QUEUE_NAME}")
    while True:
        try:
            # BRPOP blocks until a job is available (timeout 5s to allow graceful signal checking)
            job_item = redis_client.brpop([INDEXING_QUEUE_NAME], timeout=5)
            if not job_item:
                continue

            qname, payload_raw = job_item
            payload_data = json.loads(payload_raw)
            payload = IndexJobPayload(**payload_data)
            
            process_job(payload)

        except redis.RedisError as e:
            logger.error(f"Redis connection error: {e}. Retrying in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            logger.exception(f"Unexpected worker loop error: {e}")

if __name__ == "__main__":
    start_worker()