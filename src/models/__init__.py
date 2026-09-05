from src.models.base import Base
from src.models.delivery import DeliveryORM
from src.models.reports import ReportsORM

all = [
    ReportsORM,
    DeliveryORM,
    Base
]