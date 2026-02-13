import { MoveUpLeft } from "lucide-react";
import { Link } from "react-router-dom";
import { PackagesContentSkeleton } from "../Skeletons/PackagesContentSkeleton";
import { Button } from "../ui/button";
import { Card } from "../ui/card";
import { TabsContent } from "../ui/tabs";

const PackagesContent = ({ isLoading, packagesList, packages }) => {
    return (
        <>
            {
                packagesList.length > 0 && packagesList.map((sp) => (
                    <TabsContent key={sp} value={sp} className="mt-0 space-y-4 order-2 xl:order-1 grid grid-cols-1 md:grid-cols-2 2xl:grid-cols-3 gap-3">
                        {isLoading ?
                            <PackagesContentSkeleton /> : packages[sp]?.spaces && packages[sp]?.spaces?.length > 0 && packages[sp]?.spaces?.map(space => (
                                <Card
                                    key={space.id}
                                    data-anim="package-panel"
                                    className="overflow-hidden p-0 rounded-2xl border-0 bg-[#072c33] text-white m-0"
                                >
                                    <div className="p-3">
                                        {/* IMAGE */}
                                        <div className="overflow-hidden rounded-2xl bg-white/10 p-6 h-[360px] w-full">
                                            <img
                                                data-anim="panel-img"
                                                src={space.space_image}
                                                alt={space.space_name_ar || space.space_name}
                                                className="w-full h-full rounded-xl object-cover"
                                            />
                                        </div>

                                        {/* CONTENT */}
                                        <div className="space-y-5 mt-3">
                                            <h3 data-anim="panel-title" className="text-xl font-semibold">
                                                {space.space_name_ar || space.space_name}
                                            </h3>
                                            <Link to={`/packages/${space.space_name_ar || space.space_name}/${space.id}`}>
                                                <Button size="lg" className="py-6 sm:py-7 w-full" data-anim="panel-btn">
                                                    عرض المساحه
                                                    <span className="inline-flex h-8 w-8 items-center justify-center rounded-tr-md rounded-bl-md bg-white text-[#052125] group-hover:bg-lime-400 group-hover:text-white transition group-hover:-translate-x-0.5">
                                                        <MoveUpLeft className="h-5 w-5" />
                                                    </span>
                                                </Button>
                                            </Link>

                                        </div>
                                    </div>
                                </Card>
                            ))}
                    </TabsContent>
                ))
            }
        </>
    )
}

export default PackagesContent