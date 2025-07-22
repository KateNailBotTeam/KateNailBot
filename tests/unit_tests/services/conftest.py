import pytest

from src.services.schedule import ScheduleService


@pytest.fixture()
def schedule_service():
    return ScheduleService()
