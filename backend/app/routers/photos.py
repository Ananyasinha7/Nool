from __future__ import annotations

import io

from fastapi import APIRouter, Depends, File, Form, Response, UploadFile
from PIL import Image, UnidentifiedImageError
from sqlalchemy.orm import Session

from backend.app.auth.tokens import Principal
from backend.app.config import get_config
from backend.app.db import get_db
from backend.app.deps import current_principal
from backend.app.errors import AppError
from backend.app.models import DailyLog, Order, Photo, PhotoBlob
from backend.app.schemas.misc import PhotoAck, PhotoPatch
from backend.app.services.scope import BuyerScope, MerchScope, SupervisorScope, merch_scope, sup_scope

router = APIRouter(tags=["photos"])
ALLOWED = {"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp"}


def _validate_image(data: bytes) -> str:
    """Trust the bytes, not the declared type (Doc3 section 12)."""
    try:
        img = Image.open(io.BytesIO(data))
        fmt = img.format or ""
        img.verify()
    except (UnidentifiedImageError, OSError, SyntaxError) as e:
        raise AppError(422, "That file is not a valid image.", {"file": "Not a valid image."}) from e
    if fmt not in ALLOWED:
        raise AppError(422, "Use a JPEG, PNG or WebP image.", {"file": "Unsupported image type."})
    return ALLOWED[fmt]


@router.post("/logs/{log_id}/photo", response_model=PhotoAck, status_code=201)
def upload_photo(
    log_id: str, response: Response,
    photo_id: str = Form(..., alias="photoId", pattern=r"^[0-9a-fA-F-]{36}$"),
    file: UploadFile = File(...), scope: SupervisorScope = Depends(sup_scope),
) -> PhotoAck:
    log = scope.session.get(DailyLog, log_id)
    if log is None or log.entered_by_id != scope.principal.user_id:
        raise AppError(403, "You do not have access to this entry.")
    scope.get_order(log.order_id)
    existing = scope.session.get(Photo, photo_id)
    if existing is not None:
        if existing.log_id != log_id:
            raise AppError(409, "This id was used for a different photo.")
        response.status_code = 200  # idempotent
        return PhotoAck(id=photo_id)
    cap = get_config().photo_max_bytes
    data = file.file.read(cap + 1)
    if len(data) > cap:
        raise AppError(413, "Photo is too large.", {"file": "Photo is too large."})
    mime = _validate_image(data)
    scope.session.add(Photo(id=photo_id, log_id=log_id, mime=mime, size_bytes=len(data)))
    scope.session.flush()
    scope.session.add(PhotoBlob(photo_id=photo_id, bytes=data))
    scope.session.commit()
    return PhotoAck(id=photo_id)


def _may_view(session: Session, p: Principal, photo: Photo, order: Order) -> bool:
    if p.role == "MERCHANDISER":
        return True
    if p.role == "SUPERVISOR":
        try:
            SupervisorScope(session, p).get_order(order.id)
            return True
        except AppError:
            return False
    if p.role != "BUYER" or not photo.share_with_buyer or order.buyer_id != p.buyer_id:  # shared only
        return False
    from backend.app.services.buyer_links import assert_active

    assert_active(session, p)
    return True


@router.get("/photos/{photo_id}")
def get_photo(photo_id: str, p: Principal = Depends(current_principal), db: Session = Depends(get_db)) -> Response:
    photo = db.get(Photo, photo_id)
    log = db.get(DailyLog, photo.log_id) if photo else None
    order = db.get(Order, log.order_id) if log else None
    if photo is None or order is None or not _may_view(db, p, photo, order):
        raise AppError(404, "Photo not found.")  # same answer whether it exists or not
    blob = db.get(PhotoBlob, photo_id)
    return Response(content=blob.bytes, media_type=photo.mime, headers={"Cache-Control": "private, max-age=300"})


@router.patch("/photos/{photo_id}", response_model=PhotoAck)
def patch_photo(photo_id: str, body: PhotoPatch, scope: MerchScope = Depends(merch_scope)) -> PhotoAck:
    photo = scope.session.get(Photo, photo_id)
    if photo is None:
        raise AppError(404, "Photo not found.")
    photo.share_with_buyer = body.share_with_buyer
    scope.session.commit()
    return PhotoAck(id=photo_id)


__all__ = ["router", "BuyerScope"]
