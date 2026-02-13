import { CalendarDays, Clock, FileText, Image as ImageIcon, Target, User } from "lucide-react";
import { Badge } from "../ui/badge";
import { Separator } from "../ui/separator";


const STATUS_CONFIG = {
    "Checked-in": {
        label: "تم الطلب",
        variant: "secondary",
    },
    Confirmed: {
        label: "تم التأكيد",
        variant: "default",
    },
    "Checked-out": {
        label: "تم الانتهاء",
        variant: "outline",
    },
    Cancelled: {
        label: "تم الالغاء",
        variant: "destructive",
    },
    Draft: {
        label: "مسودة",
        variant: "secondary",
    },
    "No-show": {
        label: "لم يرى",
        variant: "destructive",
    },
};

function StatusBadge({ status }) {
    const config = STATUS_CONFIG[status];

    return (
        <Badge variant={config?.variant ?? "secondary"}>
            {config?.label ?? status ?? "-"}
        </Badge>
    );
}


function BookingViewItem({ booking }) {
    return (
        <div className="rounded-2xl border bg-background p-4 shadow-sm">
            <div className="flex flex-col gap-4 xl:flex-row xl:items-start">
                {/* Image */}
                <div className="relative overflow-hidden rounded-xl border bg-muted">
                    {booking?.space?.image ? (
                        <img
                            src={booking?.space?.image}
                            alt={booking?.space?.name_ar || booking?.space?.name}
                            className="h-64 w-full object-cover xl:h-32 xl:w-48"
                            loading="lazy"
                        />
                    ) : (
                        <div className="flex h-44 w-full items-center justify-center xl:h-32 xl:w-48">
                            <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                <ImageIcon className="h-4 w-4" />
                                لا توجد صورة
                            </div>
                        </div>
                    )}
                </div>

                {/* Content */}
                <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-start justify-between gap-2">
                        <div className="min-w-0">
                            <div className="truncate text-lg font-semibold">{booking?.space?.name_ar || booking?.space?.name}</div>
                            <div className="mt-1 text-sm text-muted-foreground">{booking?.purpose || "-"}</div>
                        </div>
                        <StatusBadge status={booking?.status} />
                    </div>

                    <Separator className="my-4" />

                    {/* Meta */}
                    <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
                        <div className="flex items-start gap-3 rounded-xl border bg-muted/20 p-3">
                            <CalendarDays className="mt-0.5 h-4 w-4" />
                            <div className="min-w-0">
                                <div className="text-xs text-muted-foreground">اليوم المحدد</div>
                                <div className="truncate text-sm font-medium">{booking?.booking_date || "—"}</div>
                            </div>
                        </div>

                        <div className="flex items-start gap-3 rounded-xl border bg-muted/20 p-3">
                            <Clock className="mt-0.5 h-4 w-4" />
                            <div className="min-w-0">
                                <div className="text-xs text-muted-foreground">المدة</div>
                                <div className="truncate text-sm font-medium">
                                    {booking?.duration_hours ? booking?.duration_hours + " ساعة" : "-"}
                                </div>
                            </div>
                        </div>

                        <div className="flex items-start gap-3 rounded-xl border bg-muted/20 p-3">
                            <Target className="mt-0.5 h-4 w-4" />
                            <div className="min-w-0">
                                <div className="text-xs text-muted-foreground">الغرض</div>
                                <div className="truncate text-sm font-medium">{booking?.purpose || "—"}</div>
                            </div>
                        </div>
                        <div className="flex items-start gap-3 rounded-xl border bg-muted/20 p-3">
                            <User className="mt-0.5 h-4 w-4" />
                            <div className="min-w-0">
                                <div className="text-xs text-muted-foreground">عدد الحضور</div>
                                <div className="truncate text-sm font-medium">{booking?.attendees || "—"}</div>
                            </div>
                        </div>

                        <div className="flex items-start gap-3 rounded-xl border bg-muted/20 p-3">
                            <FileText className="mt-0.5 h-4 w-4" />
                            <div className="min-w-0">
                                <div className="text-xs text-muted-foreground">ملاحظات</div>
                                <div className="text-sm font-medium">{booking.notes || "—"}</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default BookingViewItem