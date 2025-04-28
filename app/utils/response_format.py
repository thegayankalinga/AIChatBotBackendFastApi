# app/utils/response_format.py

def success_response(message: str, data: dict = None):
    return {
        "status": "success",
        "message": message,
        "data": data
    }

def error_response(message: str):
    return {
        "status": "error",
        "message": message
    }