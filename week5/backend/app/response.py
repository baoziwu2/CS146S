from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def api_ok(data, status_code: int = 200) -> JSONResponse:
    """Wrap a successful response in the standard envelope."""
    return JSONResponse(
        status_code=status_code,
        content={"ok": True, "data": jsonable_encoder(data)},
    )
