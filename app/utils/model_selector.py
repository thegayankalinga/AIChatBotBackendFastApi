# app/ml/model_selector.py
from typing import Tuple

from app.ml.predictor       import predict_intent as ml_predict

# def predict_intent(text: str, model_type: str = "transformer"):
#     """
#     model_type: "ml" for your old model.pth predictor,
#                 "transformer" for the new BERT-based one.
#     """
#     if model_type.lower() == "ml":
#         return ml_predict(text)
#     # default to transformer
#     return tf_predict(text)



# app/utils/model_selector.p

# We do *not* import predictor_transformer at top‐level,
# so any errors happen inside the function, not at startup.

def predict_intent(
    text: str,
    model_type: str = "transformer"
) -> Tuple[str, float]:
    """
    Try Transformer-based intent prediction if requested;
    on any error (missing files, HF auth, etc.) fall back to ML.
    """
    if model_type.lower() == "transformer":
        try:
            # Lazy‐import the transformer predictor
            from app.transformer.predictor_transformer import predict_intent as tf_predict

            # And run it (inside a local_files_only context to avoid network calls)
            return tf_predict(text)
        except Exception as e:
            # any import/model‐loading/inference error gets caught here
            print(f"[model_selector] Transformer failed ({e!r}), falling back to ML.")
            return ml_predict(text)

    # Otherwise or if model_type == "ml"
    return ml_predict(text)