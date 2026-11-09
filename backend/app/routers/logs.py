from __future__ import annotations

from fastapi import APIRouter, Depends, Response

from backend.app.schemas.common import LogInput
from backend.app.schemas.orders import LogAck
from backend.app.services import logs as svc
from backend.app.services.scope import SupervisorScope, sup_scope

router = APIRouter(tags=["logs"])


@router.post("/logs", response_model=LogAck, status_code=201)
def post_log(body: LogInput, response: Response, scope: SupervisorScope = Depends(sup_scope)) -> LogAck:
    created, log_id = svc.submit_log(scope, body)
    if not created:
        response.status_code = 200  # same id again: idempotent, same body
    return LogAck(id=log_id, effective=True)
