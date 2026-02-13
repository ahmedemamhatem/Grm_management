import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { Skeleton } from "@/components/ui/skeleton"

const ProfileSkeleton = () => {
    return (
        <Card className="rounded-2xl shadow-sm">
            {/* Header */}
            <CardHeader className="flex flex-row items-center justify-between gap-4">
                <div className="flex items-center gap-4">

                    {/* Avatar */}
                    <Skeleton className="h-14 w-14 rounded-full" />

                    <div className="space-y-2">
                        <Skeleton className="h-6 w-40" />
                        <Skeleton className="h-4 w-28" />
                    </div>
                </div>

                {/* Edit Button */}
                <Skeleton className="h-9 w-24 rounded-md" />
            </CardHeader>

            <CardContent>
                {/* Fields Grid */}
                <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
                    {Array.from({ length: 6 }).map((_, i) => (
                        <div
                            key={i}
                            className="flex items-start gap-3 rounded-xl border bg-background p-4"
                        >
                            <Skeleton className="h-8 w-8 rounded-lg" />

                            <div className="flex-1 space-y-2">
                                <Skeleton className="h-4 w-24" />
                                <Skeleton className="h-5 w-full" />
                            </div>
                        </div>
                    ))}
                </div>

                <Separator className="my-6" />

                {/* Footer */}
                <div className="flex flex-wrap items-center justify-between gap-3">
                    <Skeleton className="h-4 w-72" />

                    <div className="flex gap-2">
                        <Skeleton className="h-9 w-20 rounded-md" />
                        <Skeleton className="h-9 w-20 rounded-md" />
                    </div>
                </div>
            </CardContent>
        </Card>

    )
}

export default ProfileSkeleton