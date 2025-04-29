from typing import Any, Dict, Optional

def success_response(message: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Wrap a successful response.
    """
    return {
        "status": "success",
        "message": message,
        "data": data
    }

def error_response(message: str) -> Dict[str, Any]:
    """
    Wrap an error response.
    """
    return {
        "status": "error",
        "message": message
    }

def format_prediction(tag: str, confidence: float, model_used: str) -> Dict[str, Any]:
    """
    Format the raw intent prediction.
    """
    return {
        "model_used": model_used,
        "intent": tag,
        "confidence": confidence
    }

def success_prediction(tag: str, confidence: float, model_used: str) -> Dict[str, Any]:
    """
    Wrap a prediction in a success response.
    """
    payload = format_prediction(tag, confidence, model_used)
    return success_response("Intent predicted", payload)