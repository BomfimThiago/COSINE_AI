from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi

app = FastAPI()

@app.get("/api/docs", tags=["Documentation"])
async def get_api_docs():
    return JSONResponse(content={
        "endpoints": [
            {
                "path": "/api/submit",
                "method": "POST",
                "description": "Submit data for classification.",
                "request_format": "application/json",
                "request_body": {
                    "data": "string",
                    "metadata": "object"
                },
                "response_format": "application/json",
                "response_body": {
                    "status": "string",
                    "message": "string",
                    "classification_result": "object"
                },
                "authentication": "Bearer token required",
                "example_request": {
                    "data": "sample data",
                    "metadata": {"source": "user input"}
                },
                "example_response": {
                    "status": "success",
                    "message": "Data submitted successfully.",
                    "classification_result": {"label": "positive", "confidence": 0.95}
                }
            },
            {
                "path": "/api/results/{task_id}",
                "method": "GET",
                "description": "Retrieve classification results by task ID.",
                "request_format": "application/json",
                "response_format": "application/json",
                "response_body": {
                    "status": "string",
                    "result": "object"
                },
                "authentication": "Bearer token required",
                "example_response": {
                    "status": "success",
                    "result": {"task_id": "12345", "label": "negative", "confidence": 0.88}
                }
            }
        ]
    })

# Custom OpenAPI schema to include authentication info
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Data Submission and Classification API",
        version="1.0.0",
        description="API for submitting data and retrieving classification results.",
        routes=app.routes,
    )
    openapi_schema["components"] = {
        "securitySchemes": {
            "Bearer": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        }
    }
    openapi_schema["security"] = [{"Bearer": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
