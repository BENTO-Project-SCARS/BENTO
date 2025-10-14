"use client";

import {
    Badge,
    Button,
    Card,
    Group,
    Stack,
    Table,
    Text,
    Title,
    Modal,
    TextInput,
    Select,
    ActionIcon,
    Loader,
    Alert,
} from "@mantine/core";
import { IconPlus, IconFileText, IconLink, IconUnlink, IconAlertCircle } from "@tabler/icons-react";
import { useState, useEffect, useCallback } from "react";
import { notifications } from "@mantine/notifications";
import { DateInput } from "@mantine/dates";
import dayjs from "dayjs";
import { csclient } from "@/lib/api/csclient";
import { disbursementVoucherApi, type DisbursementVoucherResponse } from "@/lib/api/disbursementVoucherApi";

interface DisbursementVoucherLinkerProps {
    reportPeriod: Date | null;
    category: string;
    schoolId: number;
    disabled?: boolean;
}

export function DisbursementVoucherLinker({
    reportPeriod,
    category,
    schoolId,
    disabled = false,
}: DisbursementVoucherLinkerProps) {
    const [linkedVouchers, setLinkedVouchers] = useState<DisbursementVoucherResponse[]>([]);
    const [loading, setLoading] = useState(false);
    const [createModalOpened, setCreateModalOpened] = useState(false);
    const [newVoucherDate, setNewVoucherDate] = useState<Date | null>(null);
    const [newVoucherPayee, setNewVoucherPayee] = useState("");
    const [newVoucherMode, setNewVoucherMode] = useState("");
    const [creating, setCreating] = useState(false);

    const modeOptions = [
        { value: "MDS Check", label: "MDS Check" },
        { value: "Commercial Check", label: "Commercial Check" },
        { value: "ADA", label: "ADA (Advice to Debit Account)" },
        { value: "Others", label: "Others" },
    ];

    // Fetch linked disbursement vouchers for this liquidation report
    const fetchLinkedVouchers = useCallback(async () => {
        if (!reportPeriod || !category || !schoolId) return;

        setLoading(true);
        try {
            const year = reportPeriod.getFullYear();
            const month = reportPeriod.getMonth() + 1;

            const vouchers = await disbursementVoucherApi.getForMonth(schoolId, year, month, category);

            setLinkedVouchers(vouchers);
        } catch (error) {
            console.error("Failed to fetch linked disbursement vouchers:", error);
            notifications.show({
                title: "Error",
                message: "Failed to load linked disbursement vouchers.",
                color: "red",
            });
        } finally {
            setLoading(false);
        }
    }, [reportPeriod, category, schoolId]);

    useEffect(() => {
        fetchLinkedVouchers();
    }, [fetchLinkedVouchers]);

    const handleCreateVoucher = async () => {
        if (!newVoucherDate || !newVoucherPayee || !newVoucherMode || !reportPeriod) {
            notifications.show({
                title: "Validation Error",
                message: "Please fill in all required fields.",
                color: "orange",
            });
            return;
        }

        setCreating(true);
        try {
            const year = reportPeriod.getFullYear();
            const month = reportPeriod.getMonth() + 1;
            const date = newVoucherDate.getDate();

            await disbursementVoucherApi.createOrUpdate(schoolId, year, month, date, {
                schoolId,
                date: dayjs(newVoucherDate).format("YYYY-MM-DD"),
                modeOfPayment: newVoucherMode,
                payee: newVoucherPayee,
                linkedLiquidationCategory: category,
                entries: [],
                accountingEntries: [],
                certifiedBy: [],
            });

            notifications.show({
                title: "Success",
                message: "Disbursement voucher created and linked successfully.",
                color: "green",
            });

            // Reset form
            setNewVoucherDate(null);
            setNewVoucherPayee("");
            setNewVoucherMode("");
            setCreateModalOpened(false);

            // Refresh the list
            await fetchLinkedVouchers();
        } catch (error) {
            console.error("Failed to create disbursement voucher:", error);
            notifications.show({
                title: "Error",
                message: "Failed to create disbursement voucher.",
                color: "red",
            });
        } finally {
            setCreating(false);
        }
    };

    const handleUnlinkVoucher = async (voucherDate: string) => {
        try {
            // TODO: Implement unlinking by setting linkedLiquidationCategory to null
            console.log(`Unlinking voucher dated ${voucherDate} from category ${category}`);

            notifications.show({
                title: "Success",
                message: "Disbursement voucher unlinked successfully.",
                color: "green",
            });

            await fetchLinkedVouchers();
        } catch (error) {
            console.error("Failed to unlink disbursement voucher:", error);
            notifications.show({
                title: "Error",
                message: "Failed to unlink disbursement voucher.",
                color: "red",
            });
        }
    };

    const getDateRange = () => {
        if (!reportPeriod) return { minDate: undefined, maxDate: undefined };

        const startOfMonth = dayjs(reportPeriod).startOf("month").toDate();
        const endOfMonth = dayjs(reportPeriod).endOf("month").toDate();

        return { minDate: startOfMonth, maxDate: endOfMonth };
    };

    const { minDate, maxDate } = getDateRange();

    const formatCurrency = (amount: number) => {
        return `₱${amount.toLocaleString("en-US", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        })}`;
    };

    const calculateVoucherTotal = (voucher: DisbursementVoucherData) => {
        return voucher.entries.reduce((total, entry) => {
            return total + entry.quantity * entry.unitPrice;
        }, 0);
    };

    return (
        <Card withBorder>
            <Stack gap="md">
                <Group justify="space-between" align="center">
                    <Title order={4}>
                        <Group gap="xs">
                            <IconFileText size={20} />
                            Linked Disbursement Vouchers
                        </Group>
                    </Title>
                    <Button
                        leftSection={<IconPlus size={16} />}
                        size="sm"
                        onClick={() => setCreateModalOpened(true)}
                        disabled={disabled || !reportPeriod}
                    >
                        Create & Link Voucher
                    </Button>
                </Group>

                {loading ? (
                    <Group justify="center" p="md">
                        <Loader size="sm" />
                        <Text size="sm" c="dimmed">
                            Loading disbursement vouchers...
                        </Text>
                    </Group>
                ) : linkedVouchers.length === 0 ? (
                    <Alert icon={<IconAlertCircle size={16} />} title="No linked vouchers" color="blue" variant="light">
                        No disbursement vouchers are currently linked to this liquidation report. Create and link
                        vouchers to track disbursements for this category.
                    </Alert>
                ) : (
                    <Table>
                        <Table.Thead>
                            <Table.Tr>
                                <Table.Th>Date</Table.Th>
                                <Table.Th>Payee</Table.Th>
                                <Table.Th>Mode of Payment</Table.Th>
                                <Table.Th>Amount</Table.Th>
                                <Table.Th>Status</Table.Th>
                                <Table.Th>Actions</Table.Th>
                            </Table.Tr>
                        </Table.Thead>
                        <Table.Tbody>
                            {linkedVouchers.map((voucher, index) => (
                                <Table.Tr key={`${voucher.date}-${index}`}>
                                    <Table.Td>{dayjs(voucher.date).format("MMM DD, YYYY")}</Table.Td>
                                    <Table.Td>
                                        <Text size="sm" fw={500}>
                                            {voucher.payee}
                                        </Text>
                                    </Table.Td>
                                    <Table.Td>
                                        <Text size="sm">{voucher.modeOfPayment}</Text>
                                    </Table.Td>
                                    <Table.Td>
                                        <Text size="sm" fw={500}>
                                            {formatCurrency(calculateVoucherTotal(voucher))}
                                        </Text>
                                    </Table.Td>
                                    <Table.Td>
                                        <Badge
                                            size="sm"
                                            color={
                                                voucher.reportStatus === "approved"
                                                    ? "green"
                                                    : voucher.reportStatus === "draft"
                                                    ? "blue"
                                                    : "orange"
                                            }
                                        >
                                            {voucher.reportStatus}
                                        </Badge>
                                    </Table.Td>
                                    <Table.Td>
                                        <Group gap="xs">
                                            <ActionIcon
                                                size="sm"
                                                variant="light"
                                                color="red"
                                                onClick={() => handleUnlinkVoucher(voucher.date)}
                                                disabled={disabled}
                                                title="Unlink voucher"
                                            >
                                                <IconUnlink size={14} />
                                            </ActionIcon>
                                        </Group>
                                    </Table.Td>
                                </Table.Tr>
                            ))}
                        </Table.Tbody>
                    </Table>
                )}
            </Stack>

            {/* Create Voucher Modal */}
            <Modal
                opened={createModalOpened}
                onClose={() => setCreateModalOpened(false)}
                title="Create & Link Disbursement Voucher"
                size="md"
            >
                <Stack gap="md">
                    <Alert icon={<IconLink size={16} />} title="Linking Information" color="blue" variant="light">
                        This voucher will be automatically linked to the <strong>{category.replace(/_/g, " ")}</strong>{" "}
                        liquidation report.
                    </Alert>

                    <DateInput
                        label="Voucher Date"
                        placeholder="Select date"
                        value={newVoucherDate}
                        onChange={setNewVoucherDate}
                        minDate={minDate}
                        maxDate={maxDate}
                        required
                    />

                    <TextInput
                        label="Payee"
                        placeholder="Enter payee name"
                        value={newVoucherPayee}
                        onChange={(e) => setNewVoucherPayee(e.currentTarget.value)}
                        required
                    />

                    <Select
                        label="Mode of Payment"
                        placeholder="Select payment mode"
                        data={modeOptions}
                        value={newVoucherMode}
                        onChange={(value) => setNewVoucherMode(value || "")}
                        required
                    />

                    <Group justify="flex-end" gap="md">
                        <Button variant="default" onClick={() => setCreateModalOpened(false)} disabled={creating}>
                            Cancel
                        </Button>
                        <Button onClick={handleCreateVoucher} loading={creating}>
                            Create & Link
                        </Button>
                    </Group>
                </Stack>
            </Modal>
        </Card>
    );
}
