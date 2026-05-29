# from src.exceptions.exceptions import ObjectNotFoundException, UserNotFoundException, TaskNotFoundException, \
#     TooManyObjectsException
# from src.utils.circuit_breaker import CircuitBreaker
# from src.external_clients.http_client import TaskServiceClient
# from src.utils.db_manager import DBManager
#
#
# class BaseService:
#     db: DBManager | None
#     _shared_circuit_breaker: CircuitBreaker | None = None
#
#     def __init__(
#             self,
#             db: DBManager | None = None,
#             http_client: TaskServiceClient | None = None) -> None:
#         self.db = db
#         self.http_client = http_client
#
#         # Circuit Breaker для внешнего сервиса
#         if BaseService._shared_circuit_breaker is None:
#             BaseService._shared_circuit_breaker = CircuitBreaker(
#                 name="task_service_external",
#                 failure_threshold=2,
#                 recovery_timeout=30,
#             )
#             print(f"🔌 Circuit Breaker initialized: {BaseService._shared_circuit_breaker.get_stats()}")
#         self._circuit_breaker = BaseService._shared_circuit_breaker
#
#     async def check_user_exists(self, user_id: int) -> bool:
#         try:
#             await self.db.tasks.get_one(user_id=user_id)
#         except ObjectNotFoundException:
#             raise UserNotFoundException
#         except TooManyObjectsException:
#             return True
#
#     async def check_task_exists(self, task_id: int) -> bool:
#         try:
#             await self.db.tasks.get_one(id=task_id)
#         except ObjectNotFoundException:
#             raise TaskNotFoundException
#
#     async def check_user_or_task_exists(
#         self, user_id: int = None, task_id: int = None
#     ) -> bool:
#         if user_id and task_id:
#             await self.check_user_exists(user_id)
#             await self.check_task_exists(task_id)
#             return True
#         elif user_id:
#             await self.check_user_exists(user_id)
#             return True
#         elif task_id:
#             await self.check_task_exists(task_id)
#             return True
#         else:
#             return False