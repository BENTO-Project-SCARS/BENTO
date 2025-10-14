import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKeyConstraint
from sqlmodel import Field, Relationship, SQLModel

from centralserver.internals.models.reports.report_status import ReportStatus

if TYPE_CHECKING:
    from centralserver.internals.models.reports.monthly_report import MonthlyReport


class DisbursementVoucher(SQLModel, table=True):
    """A model representing the disbursement voucher reports.

    Document Name: Disbursement Voucher
    """

    __tablename__ = "disbursementVouchers"  # type: ignore
    __table_args__ = (
        # Composite foreign key to reference the composite primary key of monthlyReports
        ForeignKeyConstraint(
            ["parent", "schoolId"],
            ["monthlyReports.id", "monthlyReports.submittedBySchool"],
            name="fk_disbursement_voucher_monthly_report",
        ),
    )

    parent: datetime.date = Field(primary_key=True, index=True)
    date: datetime.date = Field(
        primary_key=True,
        description="The date of the disbursement voucher report.",
    )
    schoolId: int = Field(
        primary_key=True,
        foreign_key="schools.id",
        description="The ID of the school associated with the disbursement voucher report.",
    )

    modeOfPayment: str  # MDS Check, Commercial Check, ADA, Others

    # Link to liquidation report
    linkedLiquidationCategory: str | None = Field(
        default=None,
        description="The category of the liquidation report this voucher is linked to (e.g., 'operating_expenses', 'clinic_fund', etc.)",
    )

    payee: str
    tinOrEmployeeNo: str | None = None
    responsibilityCenter: str | None = None
    orsbursNo: str | None = None
    address: str | None = None

    # Section C: Certified
    certifiedCashAvailable: bool = False
    certifiedSupportingDocsComplete: bool = False
    certifiedSubjectToDebitAccount: bool = False

    # Section D: Approved for Payment
    approvedBy: str | None = Field(foreign_key="users.id", default=None)

    # Section E: Receipt of Payment
    checkNo: str | None = None
    bankNameAndAccountNo: str | None = None
    adaNo: str | None = None  # Advice to Debit Account Number
    jevNo: str | None = None  # Journal Entry Voucher Number
    reportStatus: ReportStatus = Field(
        default=ReportStatus.DRAFT,
        description="The status of the report.",
    )

    certified_by: list["DisbursementVoucherCertifiedBy"] = Relationship(
        back_populates="parent_report", cascade_delete=True
    )
    entries: list["DisbursementVoucherEntry"] = Relationship(
        back_populates="parent_report", cascade_delete=True
    )
    accounting_entries: list["DisbursementVoucherAccountingEntry"] = Relationship(
        back_populates="parent_report", cascade_delete=True
    )
    parent_report: "MonthlyReport" = Relationship(
        back_populates="disbursement_voucher_report"
    )


class DisbursementVoucherCertifiedBy(SQLModel, table=True):
    __tablename__ = "disbursementVoucherCertifiedBy"  # type: ignore
    __table_args__ = (
        # Composite foreign key to reference the composite primary key of disbursementVouchers
        ForeignKeyConstraint(
            ["parent", "date", "schoolId"],
            [
                "disbursementVouchers.parent",
                "disbursementVouchers.date",
                "disbursementVouchers.schoolId",
            ],
            name="fk_disbursement_voucher_certified_by",
        ),
    )

    parent: datetime.date = Field(primary_key=True, index=True)
    date: datetime.date = Field(primary_key=True)
    schoolId: int = Field(
        primary_key=True,
        foreign_key="schools.id",
        description="The ID of the school associated with the certification.",
    )
    user: str = Field(foreign_key="users.id")
    role: str | None = None  # e.g. Principal, Accountant, Cashier

    parent_report: DisbursementVoucher = Relationship(back_populates="certified_by")


class DisbursementVoucherEntry(SQLModel, table=True):
    __tablename__ = "disbursementVoucherEntries"  # type: ignore
    __table_args__ = (
        # Composite foreign key to reference the composite primary key of disbursementVouchers
        ForeignKeyConstraint(
            ["parent", "date", "schoolId"],
            [
                "disbursementVouchers.parent",
                "disbursementVouchers.date",
                "disbursementVouchers.schoolId",
            ],
            name="fk_disbursement_voucher_entry",
        ),
    )

    parent: datetime.date = Field(primary_key=True, index=True)
    # to be edited for specific inputs based on the report requirements
    date: datetime.datetime = Field(primary_key=True)
    schoolId: int = Field(
        primary_key=True,
        foreign_key="schools.id",
        description="The ID of the school associated with the entry.",
    )
    receipt: str | None
    particulars: str = Field(primary_key=True)
    unit: str
    quantity: float
    unitPrice: float

    parent_report: DisbursementVoucher = Relationship(back_populates="entries")


class DisbursementVoucherAccountingEntry(SQLModel, table=True):
    __tablename__ = "disbursementVoucherAccountingEntries"  # type: ignore
    __table_args__ = (
        # Composite foreign key to reference the composite primary key of disbursementVouchers
        ForeignKeyConstraint(
            ["parent", "date", "schoolId"],
            [
                "disbursementVouchers.parent",
                "disbursementVouchers.date",
                "disbursementVouchers.schoolId",
            ],
            name="fk_disbursement_voucher_accounting_entry",
        ),
    )

    parent: datetime.date = Field(primary_key=True, index=True)
    date: datetime.datetime = Field(primary_key=True)
    schoolId: int = Field(
        primary_key=True,
        foreign_key="schools.id",
        description="The ID of the school associated with the accounting entry.",
    )
    uacs_code: str
    accountTitle: str
    debit: float
    credit: float

    parent_report: DisbursementVoucher = Relationship(
        back_populates="accounting_entries"
    )
