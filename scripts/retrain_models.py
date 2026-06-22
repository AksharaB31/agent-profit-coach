import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.infra.mysql.database import SessionLocal
from app.ml.training.train_conversion_model import train_conversion_model 
from app.ml.training.train_profit_model import train_profit_models
from app.ml.training.evaluate_model import evaluate_all

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("retrain_models")


def main():
    logger.info("=== Starting model retraining ===")

    session = SessionLocal()
    try:
        logger.info("--- Training Conversion Model ---")
        conv_result = train_conversion_model(session)
        logger.info(f"Result: {conv_result}")

        logger.info("--- Training Profit Models ---")
        profit_result = train_profit_models(session)
        logger.info(f"Result: {profit_result}")

    finally:
        session.close()

    logger.info("--- Evaluation ---")
    metrics = evaluate_all()
    import json
    logger.info(f"Metrics:\n{json.dumps(metrics, indent=2)}")

    logger.info("=== Retraining complete ===")


if __name__ == "__main__":
    main()
