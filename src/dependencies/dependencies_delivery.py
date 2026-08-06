from src.database.db import async_session_factory
from src.database.unit_of_work import UnitOfWork
from src.repositories.delivery_rep import DeliveryRepository
from src.services.delivery_service import DeliveryService


class DeliveryServiceFactory:
    def __init__(self, session_factory) -> None:
        self.session_factory = session_factory

    async def create(self) -> DeliveryService:
        session = self.session_factory()
        uow = UnitOfWork(session=session)
        delivery_repo = DeliveryRepository(session=session)

        service = DeliveryService(
            delivery_rep=delivery_repo,
            uow=uow,
        )

        return service

delivery_service_factory = DeliveryServiceFactory(async_session_factory)
