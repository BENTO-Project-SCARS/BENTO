from typing import Annotated

from fastapi import APIRouter, Depends

from centralserver.internals.auth_handler import verify_access_token
from centralserver.internals.logger import LoggerFactory
from centralserver.internals.models.token import DecodedJWTToken
from centralserver.routers.reports_routes.attachments import (
    router as attachments_router,
)
from centralserver.routers.reports_routes.daily import router as daily_router
from centralserver.routers.reports_routes.disbursement_voucher import (
    router as disbursement_voucher_router,
)
from centralserver.routers.reports_routes.liquidation import (
    router as liquidation_router,
)
from centralserver.routers.reports_routes.monthly import router as monthly_router
from centralserver.routers.reports_routes.payroll import router as payroll_router

logger = LoggerFactory().get_logger(__name__)
router = APIRouter(
    prefix="/v1/reports",
    tags=["reports"],
    dependencies=[Depends(verify_access_token)],
)
logged_in_dep = Annotated[DecodedJWTToken, Depends(verify_access_token)]

router.include_router(monthly_router, tags=["Monthly Reports"])
router.include_router(daily_router, tags=["Daily Reports"])
router.include_router(payroll_router, tags=["Payroll Reports"])
router.include_router(liquidation_router, tags=["Liquidation Reports"])
router.include_router(
    disbursement_voucher_router, tags=["Disbursement Voucher Reports"]
)
router.include_router(attachments_router, tags=["Report Attachments"])
