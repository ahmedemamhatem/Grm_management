import { convertEnToAr } from "@/lib/utils"
import { PackagesListSkeleton } from ".."
import { TabsList, TabsTrigger } from "../ui/tabs"

const PackagesList = ({ packagesList, isLoading }) => {
    return (
        <>
            <div data-anim="booking-list" className="space-y-2.5 xl:space-y-5 order-1 xl:order-2">
                <TabsList className="
                                h-auto xl:w-full p-0  
                                bg-transparent flex flex-wrap xl:flex-nowrap xl:flex-col gap-5
                                items-stretch justify-start
                            ">
                    {isLoading ?
                        <PackagesListSkeleton count={packagesList.length || 5} /> :
                        packagesList.length > 0 && packagesList.map((it, idx) => (
                            <TabsTrigger
                                key={it}
                                value={it}
                                data-anim="booking-trigger"
                                className="
                                            relative py-5 xl:py-10 xl:w-full max-w-full
                                            shrink-0
                                            text-start justify-end rounded-full border-0 px-3 xl:px-6
                                            bg-[#072c33] text-white
                                            data-[state=active]:bg-emerald-600 data-[state=active]:text-white
                                            transition-all duration-300 cursor-pointer
                                            hover:bg-emerald-600 hover:text-white
                                        "
                            >
                                <span
                                    className="
                                                absolute start-6 top-1/2 -translate-y-1/2
                                                text-[44px] font-semibold leading-none
                                                text-transparent
                                                [-webkit-text-stroke:1px_rgba(255,255,255,0.16)]
                                                data-[state=active]:[-webkit-text-stroke:1px_rgba(11,16,32,0.22)]
                                            "
                                >
                                    {convertEnToAr(idx + 1)}
                                </span>

                                <span className="ms-20 text-[20px] font-semibold">
                                    {it}
                                </span>
                            </TabsTrigger>
                        ))}
                </TabsList>
            </div>
        </>
    )
}

export default PackagesList