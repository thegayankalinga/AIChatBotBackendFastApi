# app/ml/model_selector.py

from app.ml.predictor       import predict_intent as ml_predict
from app.transformer.predictor_transformer import predict_intent as tf_predict

def predict_intent(text: str, model_type: str = "transformer"):
    """
    model_type: "ml" for your old model.pth predictor,
                "transformer" for the new BERT-based one.
    """
    if model_type.lower() == "ml":
        return ml_predict(text)
    # default to transformer
    return tf_predict(text)