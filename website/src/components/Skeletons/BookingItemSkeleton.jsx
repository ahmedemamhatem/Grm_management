import { Skeleton } from '../ui/skeleton'

const BookingItemSkeleton = () => {
  return (
      <div className="rounded-2xl border bg-background p-4 shadow-sm">
          <div className="flex flex-col gap-4 xl:flex-row xl:items-start">

              {/* Image Skeleton */}
              <div className="relative overflow-hidden rounded-xl border bg-muted">
                  <Skeleton className="h-64 w-full xl:h-32 xl:w-48" />
              </div>

              {/* Content */}
              <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-start justify-between gap-2">
                      <div className="min-w-0 space-y-2">
                          <Skeleton className="h-5 w-48" />
                          <Skeleton className="h-4 w-32" />
                      </div>
                      <Skeleton className="h-6 w-20 rounded-full" />
                  </div>

                  <div className="my-4">
                      <Skeleton className="h-px w-full" />
                  </div>

                  {/* Meta Grid */}
                  <div className="grid grid-cols-1 gap-3 md:grid-cols-2">

                      {/* Booking Date */}
                      <div className="flex items-start gap-3 rounded-xl border bg-muted/20 p-3">
                          <Skeleton className="h-4 w-4 rounded-sm" />
                          <div className="space-y-2 w-full">
                              <Skeleton className="h-3 w-20" />
                              <Skeleton className="h-4 w-32" />
                          </div>
                      </div>

                      {/* Duration */}
                      <div className="flex items-start gap-3 rounded-xl border bg-muted/20 p-3">
                          <Skeleton className="h-4 w-4 rounded-sm" />
                          <div className="space-y-2 w-full">
                              <Skeleton className="h-3 w-16" />
                              <Skeleton className="h-4 w-24" />
                          </div>
                      </div>

                      {/* Purpose */}
                      <div className="flex items-start gap-3 rounded-xl border bg-muted/20 p-3">
                          <Skeleton className="h-4 w-4 rounded-sm" />
                          <div className="space-y-2 w-full">
                              <Skeleton className="h-3 w-16" />
                              <Skeleton className="h-4 w-28" />
                          </div>
                      </div>

                      {/* Attendees */}
                      <div className="flex items-start gap-3 rounded-xl border bg-muted/20 p-3">
                          <Skeleton className="h-4 w-4 rounded-sm" />
                          <div className="space-y-2 w-full">
                              <Skeleton className="h-3 w-20" />
                              <Skeleton className="h-4 w-16" />
                          </div>
                      </div>

                      {/* Notes */}
                      <div className="flex items-start gap-3 rounded-xl border bg-muted/20 p-3 md:col-span-2">
                          <Skeleton className="h-4 w-4 rounded-sm" />
                          <div className="space-y-2 w-full">
                              <Skeleton className="h-3 w-20" />
                              <Skeleton className="h-4 w-full" />
                          </div>
                      </div>

                  </div>
              </div>
          </div>
      </div>

  )
}

export default BookingItemSkeleton