from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from persistent.db.call import Call
from typing import Optional
import uuid

async def reserve_call(session: AsyncSession, call_id: str) -> bool:
    """
    Помечает слот звонка как занятый.
    Возвращает True, если успешно.
    """
    call_uuid = uuid.UUID(call_id)
    result = await session.execute(select(Call).where(Call.id == call_uuid))
    call_obj = result.scalar_one_or_none()
    if not call_obj:
        return False

    if call_obj.is_reserved:
        return False

    call_obj.is_reserved = True
    await session.commit()
    return True
