import { Skeleton } from "../ui/skeleton"

export function PackagesListSkeleton({ count = 4 }) {
    return (
        <div className="space-y-3">
            {Array.from({ length: count }).map((_, idx) => (
                <div key={idx} className=" relative py-10 w-full text-start justify-end rounded-full px-6 bg-gray-300">
                    <Skeleton className="absolute start-6 top-1/2 -translate-y-1/2 h-11 w-12 rounded-md bg-white/20" />
                    <Skeleton className="ms-20 h-5 w-[60%] rounded-md bg-white/20" />
                </div>
            ))}
        </div>
    )
}

export default PackagesListSkeleton