from app.ml.training.train_profit_model import (
    train_profit_models
)

from app.ml.training.train_conversion_model import (
    train_conversion_model
)

from app.ml.training.evaluate_model import (
    evaluate_all as evaluate_model
)


def train_models():

    print(
        "Training Profit Model..."
    )

    profit_result = train_profit_models()

    print(profit_result)

    print(
        "Training Conversion Model..."
    )

    conversion_result = (
        train_conversion_model()
    )

    print(conversion_result)

    print(
        "Evaluating Models..."
    )

    metrics = evaluate_model()

    print(metrics)

    print(
        "All ML models trained successfully"
    )


if __name__ == "__main__":
    train_models()