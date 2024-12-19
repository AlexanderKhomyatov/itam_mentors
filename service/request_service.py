from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict
import uuid
from persistent.db.request import Request, RequestStatus
from persistent.db.call import Call
from persistent.db.mentor import Mentor

async def reserv_call(
    session: AsyncSession,
    mentor_id: str,
    student_tg_id: str,
    description: str,
    call_id: str
) -> Dict:
    """
    Добавляет запрос на созвон (call_type = True).
    Если call_id не существует или не принадлежит данному ментору - ошибка.
    """
    mentor_uuid = uuid.UUID(mentor_id)
    call_uuid = uuid.UUID(call_id)

    # Проверим что есть такой ментор
    mentor_result = await session.execute(select(Mentor).where(Mentor.id == mentor_uuid))
    mentor_obj = mentor_result.scalar_one_or_none()
    if mentor_obj is None:
        return {"success": False, "message": "Mentor not found"}

    # Проверяем слот
    call_result = await session.execute(
        select(Call).where(Call.id == call_uuid, Call.mentor_id == mentor_uuid)
    )
    call_obj = call_result.scalar_one_or_none()
    if call_obj is None:
        return {"success": False, "message": "Call slot not found for this mentor"}

    new_request = Request(
        call_type=True,
        mentor_id=mentor_uuid,
        guest_tg_id=student_tg_id,
        description=description,
        call_id=call_uuid
    )
    session.add(new_request)
    await session.commit()
    await session.refresh(new_request)
    return {
        "success": True,
        "message": "Call request created",
        "request_id": str(new_request.id)
    }

async def reserv_question(
    session: AsyncSession,
    mentor_id: str,
    student_tg_id: str,
    description: str
) -> Dict:
    """
    Добавляет запрос на переписку (call_type = False).
    """
    mentor_uuid = uuid.UUID(mentor_id)

    # Проверим что есть такой ментор
    mentor_result = await session.execute(select(Mentor).where(Mentor.id == mentor_uuid))
    mentor_obj = mentor_result.scalar_one_or_none()
    if mentor_obj is None:
        return {"success": False, "message": "Mentor not found"}

    new_request = Request(
        call_type=False,
        mentor_id=mentor_uuid,
        guest_tg_id=student_tg_id,
        description=description
    )
    session.add(new_request)
    await session.commit()
    await session.refresh(new_request)
    return {
        "success": True,
        "message": "Question request created",
        "request_id": str(new_request.id)
    }

async def mentor_call_response(
    session: AsyncSession,
    mentor_id: str,
    student_tg_id: str,
    accept: bool
) -> Dict:
    """
    Ментор отвечает на запрос о созвоне для конкретного студента.
    Если accept=True, запрос становится accepted, слот занятый, остальные запросы
    на тот же слот — rejected.
    Если accept=False, запрос становится rejected.
    """
    mentor_uuid = uuid.UUID(mentor_id)

    result = await session.execute(
        select(Request)
        .where(
            Request.mentor_id == mentor_uuid,
            Request.guest_tg_id == student_tg_id,
            Request.call_type == True,
            Request.status == RequestStatus.pending
        )
        .options()
    )
    req = result.scalar_one_or_none()
    if req is None:
        return {
            "success": False,
            "message": "No pending call request for this mentor and student."
        }

    if accept:
        req.status = RequestStatus.accepted
        if req.call:
            req.call.is_reserved = True
            # Отклоняем остальные запросы на этот же слот
            await session.execute(
                update(Request)
                .where(
                    Request.call_id == req.call_id,
                    Request.id != req.id,
                    Request.status == RequestStatus.pending
                )
                .values(status=RequestStatus.rejected)
            )

        await session.commit()
        return {
            "success": True,
            "message": "Request accepted. Slot reserved. Others rejected.",
            "chosen_request_id": str(req.id)
        }
    else:
        req.status = RequestStatus.rejected
        await session.commit()
        return {
            "success": True,
            "message": "Request rejected.",
            "chosen_request_id": None
        }

async def mentor_question_response(
    session: AsyncSession,
    mentor_id: str,
    student_tg_id: str,
    accept: bool
) -> Dict:
    """
    Ментор отвечает на запрос переписки. Если accept=True -> accepted, иначе rejected.
    """
    mentor_uuid = uuid.UUID(mentor_id)

    result = await session.execute(
        select(Request)
        .where(
            Request.mentor_id == mentor_uuid,
            Request.guest_tg_id == student_tg_id,
            Request.call_type == False,
            Request.status == RequestStatus.pending
        )
    )
    req = result.scalar_one_or_none()
    if req is None:
        return {
            "success": False,
            "message": "No pending question request for this mentor and student."
        }

    req.status = RequestStatus.accepted if accept else RequestStatus.rejected
    await session.commit()
    return {
        "success": True,
        "message": "Request accepted." if accept else "Request rejected.",
        "chosen_request_id": str(req.id) if accept else None
    }
