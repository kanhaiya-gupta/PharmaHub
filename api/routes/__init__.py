from .stores import router as stores_router
from .medicines import router as medicines_router
from .customers import router as customers_router
from .operators import router as operators_router
from .purchases import router as purchases_router
from .sync import router as sync_router
from .reports import router as reports_router

__all__ = [
    'stores_router',
    'medicines_router',
    'customers_router',
    'operators_router',
    'purchases_router',
    'sync_router',
    'reports_router'
] 