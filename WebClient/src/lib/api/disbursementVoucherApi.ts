/**
 * Temporary API service for disbursement vouchers
 * This will be replaced by the auto-generated OpenAPI client once the backend is updated
 */

interface DisbursementVoucherEntry {
    receipt?: string;
    particulars: string;
    unit: string;
    quantity: number;
    unitPrice: number;
}

interface DisbursementVoucherAccountingEntry {
    uacs_code: string;
    accountTitle: string;
    debit: number;
    credit: number;
}

interface DisbursementVoucherCreateRequest {
    schoolId: number;
    date: string; // YYYY-MM-DD format
    modeOfPayment: string;
    payee: string;
    tinOrEmployeeNo?: string;
    responsibilityCenter?: string;
    orsbursNo?: string;
    address?: string;
    linkedLiquidationCategory?: string;

    // Section C: Certified
    certifiedCashAvailable?: boolean;
    certifiedSupportingDocsComplete?: boolean;
    certifiedSubjectToDebitAccount?: boolean;

    // Section D: Approved for Payment
    approvedBy?: string;

    // Section E: Receipt of Payment
    checkNo?: string;
    bankNameAndAccountNo?: string;
    adaNo?: string;
    jevNo?: string;

    entries: DisbursementVoucherEntry[];
    accountingEntries: DisbursementVoucherAccountingEntry[];
    certifiedBy: string[];
}

interface DisbursementVoucherResponse {
    parent: string; // Date string
    date: string; // Date string
    schoolId: number;
    modeOfPayment: string;
    payee: string;
    tinOrEmployeeNo?: string;
    responsibilityCenter?: string;
    orsbursNo?: string;
    address?: string;
    linkedLiquidationCategory?: string;
    reportStatus: string;

    // Section C: Certified
    certifiedCashAvailable: boolean;
    certifiedSupportingDocsComplete: boolean;
    certifiedSubjectToDebitAccount: boolean;

    // Section D: Approved for Payment
    approvedBy?: string;

    // Section E: Receipt of Payment
    checkNo?: string;
    bankNameAndAccountNo?: string;
    adaNo?: string;
    jevNo?: string;

    entries: DisbursementVoucherEntry[];
    accountingEntries: DisbursementVoucherAccountingEntry[];
    certifiedBy: string[];
}

// Temporary API functions - these will be replaced by the auto-generated client
export const disbursementVoucherApi = {
    async createOrUpdate(
        schoolId: number,
        year: number,
        month: number,
        date: number,
        data: DisbursementVoucherCreateRequest
    ): Promise<DisbursementVoucherResponse> {
        const response = await fetch(`/api/v1/reports/disbursement-voucher/${schoolId}/${year}/${month}/${date}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                // TODO: Add authentication header
            },
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return response.json();
    },

    async get(schoolId: number, year: number, month: number, date: number): Promise<DisbursementVoucherResponse> {
        const response = await fetch(`/api/v1/reports/disbursement-voucher/${schoolId}/${year}/${month}/${date}`, {
            method: "GET",
            headers: {
                // TODO: Add authentication header
            },
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return response.json();
    },

    async getForMonth(
        schoolId: number,
        year: number,
        month: number,
        linkedCategory?: string
    ): Promise<DisbursementVoucherResponse[]> {
        const url = new URL(
            `/api/v1/reports/disbursement-voucher/${schoolId}/${year}/${month}`,
            window.location.origin
        );

        if (linkedCategory) {
            url.searchParams.set("linked_category", linkedCategory);
        }

        const response = await fetch(url.toString(), {
            method: "GET",
            headers: {
                // TODO: Add authentication header
            },
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return response.json();
    },
};

export type {
    DisbursementVoucherEntry,
    DisbursementVoucherAccountingEntry,
    DisbursementVoucherCreateRequest,
    DisbursementVoucherResponse,
};
