"""
API endpoints for disbursement voucher reports.
"""

import datetime
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, select

from centralserver.internals.auth_handler import (
    get_user,
    verify_access_token,
    verify_user_permission,
)
from centralserver.internals.db_handler import get_db_session
from centralserver.internals.logger import LoggerFactory
from centralserver.internals.models.reports.disbursement_voucher import (
    DisbursementVoucher,
    DisbursementVoucherCertifiedBy,
    DisbursementVoucherEntry,
    DisbursementVoucherAccountingEntry,
)
from centralserver.internals.models.reports.report_status import ReportStatus

router = APIRouter(prefix="/disbursement-voucher")
logger = LoggerFactory().get_logger("disbursement_voucher")


class DisbursementVoucherEntryData(BaseModel):
    """Data model for disbursement voucher entries."""

    receipt: Optional[str] = None
    particulars: str
    unit: str
    quantity: float
    unitPrice: float


class DisbursementVoucherAccountingEntryData(BaseModel):
    """Data model for disbursement voucher accounting entries."""

    uacs_code: str
    accountTitle: str
    debit: float
    credit: float


class DisbursementVoucherCreateRequest(BaseModel):
    """Request model for creating/updating disbursement vouchers."""

    schoolId: int
    date: datetime.date
    modeOfPayment: str
    payee: str
    tinOrEmployeeNo: Optional[str] = None
    responsibilityCenter: Optional[str] = None
    orsbursNo: Optional[str] = None
    address: Optional[str] = None
    linkedLiquidationCategory: Optional[str] = None

    # Section C: Certified
    certifiedCashAvailable: bool = False
    certifiedSupportingDocsComplete: bool = False
    certifiedSubjectToDebitAccount: bool = False

    # Section D: Approved for Payment
    approvedBy: Optional[str] = None

    # Section E: Receipt of Payment
    checkNo: Optional[str] = None
    bankNameAndAccountNo: Optional[str] = None
    adaNo: Optional[str] = None
    jevNo: Optional[str] = None

    entries: List[DisbursementVoucherEntryData] = []
    accountingEntries: List[DisbursementVoucherAccountingEntryData] = []
    certifiedBy: List[str] = []


class DisbursementVoucherResponse(BaseModel):
    """Response model for disbursement voucher data."""

    parent: datetime.date
    date: datetime.date
    schoolId: int
    modeOfPayment: str
    payee: str
    tinOrEmployeeNo: Optional[str] = None
    responsibilityCenter: Optional[str] = None
    orsbursNo: Optional[str] = None
    address: Optional[str] = None
    linkedLiquidationCategory: Optional[str] = None
    reportStatus: ReportStatus

    # Section C: Certified
    certifiedCashAvailable: bool
    certifiedSupportingDocsComplete: bool
    certifiedSubjectToDebitAccount: bool

    # Section D: Approved for Payment
    approvedBy: Optional[str] = None

    # Section E: Receipt of Payment
    checkNo: Optional[str] = None
    bankNameAndAccountNo: Optional[str] = None
    adaNo: Optional[str] = None
    jevNo: Optional[str] = None

    entries: List[DisbursementVoucherEntryData] = []
    accountingEntries: List[DisbursementVoucherAccountingEntryData] = []
    certifiedBy: List[str] = []


@router.post("/{school_id}/{year}/{month}/{date}")
async def create_or_update_disbursement_voucher(
    school_id: int,
    year: int,
    month: int,
    date: int,
    request: DisbursementVoucherCreateRequest,
    db: Annotated[Session, Depends(get_db_session)],
    token: Annotated[str, Depends(verify_access_token)],
) -> DisbursementVoucherResponse:
    """Create or update a disbursement voucher."""

    user = get_user(db, token)
    await verify_user_permission(db, user, "reports:local:write")

    logger.debug(
        f"user `{user.id}` attempting to create/update disbursement voucher for school {school_id}, {year}-{month}-{date}"
    )

    # Create the parent date (monthly report date)
    parent_date = datetime.date(year, month, 1)
    voucher_date = datetime.date(year, month, date)

    # Check if voucher already exists
    stmt = select(DisbursementVoucher).where(
        DisbursementVoucher.parent == parent_date,
        DisbursementVoucher.date == voucher_date,
        DisbursementVoucher.schoolId == school_id,
    )

    existing_voucher = db.exec(stmt).first()

    if existing_voucher:
        # Update existing voucher
        voucher = existing_voucher
        # Clear existing entries
        for entry in voucher.entries:
            db.delete(entry)
        for entry in voucher.accounting_entries:
            db.delete(entry)
        for cert in voucher.certified_by:
            db.delete(cert)
    else:
        # Create new voucher
        voucher = DisbursementVoucher(
            parent=parent_date,
            date=voucher_date,
            schoolId=school_id,
        )
        db.add(voucher)

    # Update voucher fields
    voucher.modeOfPayment = request.modeOfPayment
    voucher.payee = request.payee
    voucher.tinOrEmployeeNo = request.tinOrEmployeeNo
    voucher.responsibilityCenter = request.responsibilityCenter
    voucher.orsbursNo = request.orsbursNo
    voucher.address = request.address
    voucher.linkedLiquidationCategory = request.linkedLiquidationCategory
    voucher.certifiedCashAvailable = request.certifiedCashAvailable
    voucher.certifiedSupportingDocsComplete = request.certifiedSupportingDocsComplete
    voucher.certifiedSubjectToDebitAccount = request.certifiedSubjectToDebitAccount
    voucher.approvedBy = request.approvedBy
    voucher.checkNo = request.checkNo
    voucher.bankNameAndAccountNo = request.bankNameAndAccountNo
    voucher.adaNo = request.adaNo
    voucher.jevNo = request.jevNo

    # Add entries
    for entry_data in request.entries:
        entry = DisbursementVoucherEntry(
            parent=parent_date,
            date=datetime.datetime.combine(voucher_date, datetime.time()),
            schoolId=school_id,
            receipt=entry_data.receipt,
            particulars=entry_data.particulars,
            unit=entry_data.unit,
            quantity=entry_data.quantity,
            unitPrice=entry_data.unitPrice,
        )
        db.add(entry)

    # Add accounting entries
    for acc_entry_data in request.accountingEntries:
        acc_entry = DisbursementVoucherAccountingEntry(
            parent=parent_date,
            date=datetime.datetime.combine(voucher_date, datetime.time()),
            schoolId=school_id,
            uacs_code=acc_entry_data.uacs_code,
            accountTitle=acc_entry_data.accountTitle,
            debit=acc_entry_data.debit,
            credit=acc_entry_data.credit,
        )
        db.add(acc_entry)

    # Add certified by
    for certified_user in request.certifiedBy:
        cert = DisbursementVoucherCertifiedBy(
            parent=parent_date,
            date=voucher_date,
            schoolId=school_id,
            user=certified_user,
        )
        db.add(cert)

    db.commit()
    db.refresh(voucher)

    # Build response
    response = DisbursementVoucherResponse(
        parent=voucher.parent,
        date=voucher.date,
        schoolId=voucher.schoolId,
        modeOfPayment=voucher.modeOfPayment,
        payee=voucher.payee,
        tinOrEmployeeNo=voucher.tinOrEmployeeNo,
        responsibilityCenter=voucher.responsibilityCenter,
        orsbursNo=voucher.orsbursNo,
        address=voucher.address,
        linkedLiquidationCategory=voucher.linkedLiquidationCategory,
        reportStatus=voucher.reportStatus,
        certifiedCashAvailable=voucher.certifiedCashAvailable,
        certifiedSupportingDocsComplete=voucher.certifiedSupportingDocsComplete,
        certifiedSubjectToDebitAccount=voucher.certifiedSubjectToDebitAccount,
        approvedBy=voucher.approvedBy,
        checkNo=voucher.checkNo,
        bankNameAndAccountNo=voucher.bankNameAndAccountNo,
        adaNo=voucher.adaNo,
        jevNo=voucher.jevNo,
        entries=[
            DisbursementVoucherEntryData(
                receipt=entry.receipt,
                particulars=entry.particulars,
                unit=entry.unit,
                quantity=entry.quantity,
                unitPrice=entry.unitPrice,
            )
            for entry in voucher.entries
        ],
        accountingEntries=[
            DisbursementVoucherAccountingEntryData(
                uacs_code=entry.uacs_code,
                accountTitle=entry.accountTitle,
                debit=entry.debit,
                credit=entry.credit,
            )
            for entry in voucher.accounting_entries
        ],
        certifiedBy=[cert.user for cert in voucher.certified_by],
    )

    return response


@router.get("/{school_id}/{year}/{month}/{date}")
async def get_disbursement_voucher(
    school_id: int,
    year: int,
    month: int,
    date: int,
    db: Annotated[Session, Depends(get_db_session)],
    token: Annotated[str, Depends(verify_access_token)],
) -> DisbursementVoucherResponse:
    """Get a disbursement voucher."""

    user = get_user(db, token)
    await verify_user_permission(db, user, "reports:local:read")

    parent_date = datetime.date(year, month, 1)
    voucher_date = datetime.date(year, month, date)

    stmt = select(DisbursementVoucher).where(
        DisbursementVoucher.parent == parent_date,
        DisbursementVoucher.date == voucher_date,
        DisbursementVoucher.schoolId == school_id,
    )

    voucher = db.exec(stmt).first()

    if not voucher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disbursement voucher not found.",
        )

    # Build response
    response = DisbursementVoucherResponse(
        parent=voucher.parent,
        date=voucher.date,
        schoolId=voucher.schoolId,
        modeOfPayment=voucher.modeOfPayment,
        payee=voucher.payee,
        tinOrEmployeeNo=voucher.tinOrEmployeeNo,
        responsibilityCenter=voucher.responsibilityCenter,
        orsbursNo=voucher.orsbursNo,
        address=voucher.address,
        linkedLiquidationCategory=voucher.linkedLiquidationCategory,
        reportStatus=voucher.reportStatus,
        certifiedCashAvailable=voucher.certifiedCashAvailable,
        certifiedSupportingDocsComplete=voucher.certifiedSupportingDocsComplete,
        certifiedSubjectToDebitAccount=voucher.certifiedSubjectToDebitAccount,
        approvedBy=voucher.approvedBy,
        checkNo=voucher.checkNo,
        bankNameAndAccountNo=voucher.bankNameAndAccountNo,
        adaNo=voucher.adaNo,
        jevNo=voucher.jevNo,
        entries=[
            DisbursementVoucherEntryData(
                receipt=entry.receipt,
                particulars=entry.particulars,
                unit=entry.unit,
                quantity=entry.quantity,
                unitPrice=entry.unitPrice,
            )
            for entry in voucher.entries
        ],
        accountingEntries=[
            DisbursementVoucherAccountingEntryData(
                uacs_code=entry.uacs_code,
                accountTitle=entry.accountTitle,
                debit=entry.debit,
                credit=entry.credit,
            )
            for entry in voucher.accounting_entries
        ],
        certifiedBy=[cert.user for cert in voucher.certified_by],
    )

    return response


@router.get("/{school_id}/{year}/{month}")
async def get_disbursement_vouchers_for_month(
    school_id: int,
    year: int,
    month: int,
    db: Annotated[Session, Depends(get_db_session)],
    token: Annotated[str, Depends(verify_access_token)],
    linked_category: Optional[str] = None,
) -> List[DisbursementVoucherResponse]:
    """Get all disbursement vouchers for a specific month, optionally filtered by linked liquidation category."""

    user = get_user(db, token)
    await verify_user_permission(db, user, "reports:local:read")

    parent_date = datetime.date(year, month, 1)

    stmt = select(DisbursementVoucher).where(
        DisbursementVoucher.parent == parent_date,
        DisbursementVoucher.schoolId == school_id,
    )

    if linked_category:
        stmt = stmt.where(
            DisbursementVoucher.linkedLiquidationCategory == linked_category
        )

    vouchers = db.exec(stmt).all()

    # Build response list
    response_list = []
    for voucher in vouchers:
        response = DisbursementVoucherResponse(
            parent=voucher.parent,
            date=voucher.date,
            schoolId=voucher.schoolId,
            modeOfPayment=voucher.modeOfPayment,
            payee=voucher.payee,
            tinOrEmployeeNo=voucher.tinOrEmployeeNo,
            responsibilityCenter=voucher.responsibilityCenter,
            orsbursNo=voucher.orsbursNo,
            address=voucher.address,
            linkedLiquidationCategory=voucher.linkedLiquidationCategory,
            reportStatus=voucher.reportStatus,
            certifiedCashAvailable=voucher.certifiedCashAvailable,
            certifiedSupportingDocsComplete=voucher.certifiedSupportingDocsComplete,
            certifiedSubjectToDebitAccount=voucher.certifiedSubjectToDebitAccount,
            approvedBy=voucher.approvedBy,
            checkNo=voucher.checkNo,
            bankNameAndAccountNo=voucher.bankNameAndAccountNo,
            adaNo=voucher.adaNo,
            jevNo=voucher.jevNo,
            entries=[
                DisbursementVoucherEntryData(
                    receipt=entry.receipt,
                    particulars=entry.particulars,
                    unit=entry.unit,
                    quantity=entry.quantity,
                    unitPrice=entry.unitPrice,
                )
                for entry in voucher.entries
            ],
            accountingEntries=[
                DisbursementVoucherAccountingEntryData(
                    uacs_code=entry.uacs_code,
                    accountTitle=entry.accountTitle,
                    debit=entry.debit,
                    credit=entry.credit,
                )
                for entry in voucher.accounting_entries
            ],
            certifiedBy=[cert.user for cert in voucher.certified_by],
        )
        response_list.append(response)

    return response_list
