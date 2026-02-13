import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export function PackagesContentSkeleton({ count = 3 }) {
    return (
        <>
            {Array.from({ length: count }).map((_, i) => (
                <Card
                    key={i}
                    data-anim="booking-panel"
                    className="overflow-hidden rounded-2xl border-0 bg-gray-300 text-white"
                >
                    <div className="p-3">
                        {/* IMAGE */}
                        <div className="overflow-hidden rounded-2xl bg-white/10 p-6">
                            <Skeleton className="h-[360px] w-full rounded-xl md:h-[420px]" />
                        </div>

                        {/* CONTENT */}
                        <div className="space-y-5">
                            {/* title */}
                            <Skeleton className="h-9 w-72 rounded-lg" />

                            {/* desc */}
                            <div className="space-y-2">
                                <Skeleton className="h-4 w-[520px] max-w-full rounded-md" />
                                <Skeleton className="h-4 w-[460px] max-w-full rounded-md" />
                            </div>

                            {/* button */}
                            <div className="pt-4">
                                <Skeleton className="h-14 w-44 rounded-xl sm:h-16" />
                            </div>
                        </div>
                    </div>
                </Card>
            ))}
        </>
    );
}
