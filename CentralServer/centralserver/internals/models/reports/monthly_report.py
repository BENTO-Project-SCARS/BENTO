import datetime

from sqlalchemy import ForeignKeyConstraint
from sqlmodel import Field, Relationship, SQLModel

from centralserver.internals.models.reports.daily_financial_report import (
    DailyFinancialReport,
)
from centralserver.internals.models.reports.disbursement_voucher import (
    DisbursementVoucher,
)
from centralserver.internals.models.reports.lr_administrative_expenses import (
    LiquidationReportAdministrativeExpenses,
)
from centralserver.internals.models.reports.lr_clinic_fund import (
    LiquidationReportClinicFund,
)
from centralserver.internals.models.reports.lr_faculty_stud_dev_fund import (
    LiquidationReportFacultyAndStudentDevFund,
)
from centralserver.internals.models.reports.lr_he_fund import LiquidationReportHEFund
from centralserver.internals.models.reports.lr_operating_expenses import (
    LiquidationReportOperatingExpenses,
)
from centralserver.internals.models.reports.lr_revolving_fund import (
    LiquidationReportRevolvingFund,
)
from centralserver.internals.models.reports.lr_school_operation_fund import (
    LiquidationReportSchoolOperationFund,
)
from centralserver.internals.models.reports.lr_supplementary_feeding_fund import (
    LiquidationReportSupplementaryFeedingFund,
)
from centralserver.internals.models.reports.payroll_report import PayrollReport
from centralserver.internals.models.reports.report_status import ReportStatus


class MonthlyReport(SQLModel, table=True):
    """A model representing a monthly report in the system.

    Document Names:
        - Statement of Receipts, Disbursements, and Utilization of Income (School Canteen)
        - Monthly Summarized Canteen Report for SY [YEAR-YEAR]
    """

    __tablename__: str = "monthlyReports"  # type: ignore

    id: datetime.date = Field(
        primary_key=True,
        index=True,
        description="The month and year of the report.",
    )
    name: str | None = Field(
        default=None,
        description="The name of the report.",
    )
    submittedBySchool: int = Field(
        primary_key=True,
        index=True,
        foreign_key="schools.id",
        description="The school that submitted the report.",
    )
    reportStatus: ReportStatus = Field(
        default=ReportStatus.DRAFT,
        description="The status of the report.",
    )
    preparedBy: str | None = Field(
        foreign_key="users.id", description="The user who prepared the report."
    )
    notedBy: str | None = Field(
        default=None,
        foreign_key="users.id",
        description="The user who noted the report.",
    )
    dateCreated: datetime.datetime = Field(
        default_factory=datetime.datetime.now,
        description="The date and time when the report was created.",
    )
    dateApproved: datetime.datetime | None = Field(
        default=None,
        description="The date and time when the report was approved.",
    )
    dateReceived: datetime.datetime | None = Field(
        default=None,
        description="The date and time when the report was received.",
    )
    lastModified: datetime.datetime = Field(
        default_factory=datetime.datetime.now,
        description="The last time the report was modified.",
    )

    receivedByDailyFinancialReport: str | None = Field(
        default=None, foreign_key="users.id"
    )
    receivedByOperatingExpensesReport: str | None = Field(
        default=None, foreign_key="users.id"
    )
    receivedByAdministrativeExpensesReport: str | None = Field(
        default=None, foreign_key="users.id"
    )
    receivedByClinicFundReport: str | None = Field(default=None, foreign_key="users.id")
    receivedBySupplementaryFeedingFundReport: str | None = Field(
        default=None, foreign_key="users.id"
    )
    receivedByHEFundReport: str | None = Field(default=None, foreign_key="users.id")
    receivedByFacultyAndStudentDevFundReport: str | None = Field(
        default=None, foreign_key="users.id"
    )
    receivedBySchoolOperationFundReport: str | None = Field(
        default=None, foreign_key="users.id"
    )
    receivedByRevolvingFundReport: str | None = Field(
        default=None, foreign_key="users.id"
    )

    audited_by: list["MonthlyReportAuditedBy"] = Relationship(
        back_populates="parent_report", cascade_delete=True
    )

    daily_financial_report: DailyFinancialReport | None = Relationship(
        back_populates="parent_report", cascade_delete=True
    )
    operating_expenses_report: LiquidationReportOperatingExpenses | None = Relationship(
        back_populates="parent_report", cascade_delete=True
    )
    administrative_expenses_report: LiquidationReportAdministrativeExpenses | None = (
        Relationship(back_populates="parent_report", cascade_delete=True)
    )
    clinic_fund_report: LiquidationReportClinicFund | None = Relationship(
        back_populates="parent_report", cascade_delete=True
    )
    supplementary_feeding_fund_report: (
        LiquidationReportSupplementaryFeedingFund | None
    ) = Relationship(back_populates="parent_report", cascade_delete=True)
    he_fund_report: LiquidationReportHEFund | None = Relationship(
        back_populates="parent_report", cascade_delete=True
    )
    faculty_and_student_dev_fund_report: (
        LiquidationReportFacultyAndStudentDevFund | None
    ) = Relationship(back_populates="parent_report", cascade_delete=True)
    school_operation_fund_report: LiquidationReportSchoolOperationFund | None = (
        Relationship(back_populates="parent_report", cascade_delete=True)
    )
    revolving_fund_report: LiquidationReportRevolvingFund | None = Relationship(
        back_populates="parent_report", cascade_delete=True
    )
    disbursement_voucher_report: list[DisbursementVoucher] = Relationship(
        back_populates="parent_report", cascade_delete=True
    )
    payroll_report: PayrollReport | None = Relationship(
        back_populates="parent_report", cascade_delete=True
    )


class MonthlyReportAuditedBy(SQLModel, table=True):
    __tablename__: str = "monthlyReportAuditedBy"  # type: ignore
    __table_args__ = (
        # Composite foreign key to reference the composite primary key of monthlyReports
        ForeignKeyConstraint(
            ["parent", "schoolId"],
            ["monthlyReports.id", "monthlyReports.submittedBySchool"],
            name="fk_monthly_report_audited_by",
        ),
    )

    parent: datetime.date = Field(
        primary_key=True,
        index=True,
    )
    user: str = Field(foreign_key="users.id")
    schoolId: int = Field(
        primary_key=True,
        index=True,
        foreign_key="schools.id",
        description="The school that submitted the report.",
    )

    parent_report: MonthlyReport = Relationship(back_populates="audited_by")
