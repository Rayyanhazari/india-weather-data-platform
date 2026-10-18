
import logging
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(
            LOG_DIR / "pipeline.log",
            encoding="utf-8",
        ),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger("weather_pipeline")


def run_stage(stage_name):
    logger.info("Starting stage: %s", stage_name)

    result = subprocess.run(
        [sys.executable, "-m", f"src.{stage_name}"],
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    if result.stdout:
        logger.info("%s output:\n%s", stage_name, result.stdout.strip())

    if result.stderr:
        logger.info("%s messages:\n%s", stage_name, result.stderr.strip())

    if result.returncode != 0:
        raise RuntimeError(
            f"Stage '{stage_name}' failed with exit code "
            f"{result.returncode}"
        )

    logger.info("Completed stage: %s", stage_name)


def main():
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    logger.info("Pipeline started | run_id=%s", run_id)

    try:
        run_stage("extract")
        run_stage("load")
        logger.info("Pipeline completed successfully | run_id=%s", run_id)

    except Exception:
        logger.exception("Pipeline failed | run_id=%s", run_id)
        sys.exit(1)


if __name__ == "__main__":
    main()
