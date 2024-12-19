from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from persistent.db.mentor import Mentor
from typing import Dict

async def get_mentors_list(session: AsyncSession) -> Dict[str, str]:
    """
    Возвращает словарь {mentor_name: mentor_id} для всех менторов,
    у которых есть name.
    """
    result = await session.execute(select(Mentor).where(Mentor.name.isnot(None)))
    mentors = result.scalars().all()
    return {mentor.name: str(mentor.id) for mentor in mentors if mentor.name}