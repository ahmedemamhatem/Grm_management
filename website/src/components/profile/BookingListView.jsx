import GetProfileBookingsHook from "@/logic/profile/GetProfileBookingsHook";
import { useMemo, useState } from "react";
import { BookingItemSkeleton } from "..";
import { Button } from "../ui/button";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "../ui/card";
import BookingViewItem from "./BookingViewItem";

const STATUS_LABELS = {
    all: "الكل",
    "Checked-in": "تم الطلب",
    "Checked-out": "تم الانتهاء",
    Confirmed: "تم التأكيد",
    Cancelled: "تم الالغاء",
    Draft: "مسودة",
    "No-show": "لم يرى",
};

const STATUSES = ["all", "Checked-in", "Draft", "Checked-out", "Confirmed", "No-show", "Cancelled"];

const BookingListView = () => {
    const { bookings, isLoading, error } = GetProfileBookingsHook();
    const [filter, setFilter] = useState("all");

    const safeBookings = Array.isArray(bookings) ? bookings : [];

    const counts = useMemo(() => {
        const c = {
            all: safeBookings.length,
            "Checked-in": 0,
            "Checked-out": 0,
            Confirmed: 0,
            Cancelled: 0,
            Draft: 0,
            "No-show": 0,
        };

        for (const b of safeBookings) {
            const s = b?.status;
            if (!s) continue;
            c[s] = (c[s] || 0) + 1;
        }
        return c;
    }, [safeBookings]);

    const filteredBookings = useMemo(() => {
        if (filter === "all") return safeBookings;
        return safeBookings.filter((b) => b?.status === filter);
    }, [filter, safeBookings]);

    return (
        <Card className="rounded-2xl shadow-sm">
            <CardHeader className="space-y-3">
                <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                        <CardTitle>الحجوزات</CardTitle>
                        <CardDescription>اعرض حجوزاتك وفلترها حسب الحالة.</CardDescription>
                    </div>
                </div>

                <div className="flex flex-wrap gap-2">
                    {STATUSES.map((s) => (
                        <Button
                            key={s}
                            variant={filter === s ? "default" : "outline"}
                            onClick={() => setFilter(s)}
                        >
                            {STATUS_LABELS[s]} ({counts?.[s] ?? 0})
                        </Button>
                    ))}
                </div>
            </CardHeader>

            <CardContent>
                {isLoading ? (
                    Array.from({ length: 5 }).map((_, i) => (
                        <BookingItemSkeleton key={i} />
                    ))
                ) : error ? (
                    <div className="rounded-xl border bg-muted/30 p-6 text-sm text-destructive">
                        حصل خطأ أثناء تحميل الحجوزات.
                    </div>
                ) : filteredBookings.length === 0 ? (
                    <div className="rounded-xl border bg-muted/30 p-6 text-sm text-muted-foreground">
                        لا يوجد حجوزات لعرضها دلوقتي.
                    </div>
                ) : (
                    <div className="space-y-3">
                        {filteredBookings.map((booking) => (
                            <BookingViewItem
                                key={booking?.id ?? booking?.name ?? `${booking?.status}-${Math.random()}`}
                                booking={booking}
                            />
                        ))}
                    </div>
                )}
            </CardContent>
        </Card>
    );
};

export default BookingListView;
