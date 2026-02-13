import { useGSAP } from "@gsap/react";
import { gsap } from "gsap";
import { useRef } from "react";
import { FormatHtmlContent } from "..";
import BookingForm from "../booking/BookingForm";
import { Badge } from "../ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Separator } from "../ui/separator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../ui/tabs";

function OnePackageContent({ space, activeTab, setActiveTab }) {
    const rootRef = useRef(null);
    const contentWrapRef = useRef(null);

    useGSAP(() => {
        // Entrance animation
        const ctx = gsap.context(() => {
            const card = rootRef.current?.querySelector("[data-card]");
            const badge = rootRef.current?.querySelector("[data-status-badge]");
            const tabs = rootRef.current?.querySelector("[data-tabs]");

            // Initial states
            gsap.set(card, { opacity: 0, y: 16 });
            gsap.set(badge, { opacity: 0, scale: 0.9 });
            gsap.set(tabs, { opacity: 0, y: 8 });

            // Animate in
            const tl = gsap.timeline({ defaults: { ease: "power3.out" } });
            tl.to(card, { opacity: 1, y: 0, duration: 0.65 }, 0);
            tl.to(badge, { opacity: 1, scale: 1, duration: 0.35 }, 0.18);
            tl.to(tabs, { opacity: 1, y: 0, duration: 0.45 }, 0.22);

            // If details tab is the default, animate its rows
            const items = contentWrapRef.current?.querySelectorAll("[data-anim-item]");
            if (items && items.length) {
                gsap.fromTo(
                    items,
                    { opacity: 0, y: 8 },
                    {
                        opacity: 1,
                        y: 0,
                        duration: 0.35,
                        stagger: 0.08,
                        ease: "power2.out",
                        delay: 0.35,
                    }
                );
            }
        }, rootRef);

        return () => ctx.revert();
    }, []);

    useGSAP(() => {
        // Animate tab content on change
        if (!contentWrapRef.current) return;

        const ctx = gsap.context(() => {
            gsap.fromTo(
                contentWrapRef.current,
                { opacity: 0, y: 10 },
                { opacity: 1, y: 0, duration: 0.35, ease: "power2.out" }
            );

            // Stagger inner items (only if present)
            const items = contentWrapRef.current.querySelectorAll("[data-anim-item]");
            if (items && items.length) {
                gsap.fromTo(
                    items,
                    { opacity: 0, y: 8 },
                    {
                        opacity: 1,
                        y: 0,
                        duration: 0.3,
                        stagger: 0.06,
                        ease: "power2.out",
                        delay: 0.05,
                    }
                );
            }
        }, contentWrapRef);

        return () => ctx.revert();
    }, [activeTab]);

    return (
        <div ref={rootRef} className="md:col-span-6 lg:col-span-5">
            <Card data-card className="overflow-hidden rounded-2xl">
                <CardHeader data-header className="space-y-3">
                    <div className="flex items-start justify-between gap-3">
                        <div className="min-w-0">
                            <CardTitle className="truncate text-xl md:text-2xl">
                                {space?.space_name_ar || space?.space_name}
                            </CardTitle>
                        </div>
                    </div>

                    <Separator />
                </CardHeader>

                <CardContent>
                    <Tabs
                        data-tabs
                        value={activeTab}
                        onValueChange={setActiveTab}
                        className="w-full"
                    >
                        <TabsList className="grid w-full grid-cols-2">
                            <TabsTrigger value="details">التفاصيل</TabsTrigger>
                            <TabsTrigger value="book">احجز</TabsTrigger>
                        </TabsList>

                        {/* This wrapper is what we animate on tab change */}
                        <div ref={contentWrapRef} className="mt-4">
                            {/* Details */}
                            <TabsContent value="details" className="m-0" dir="rtl">
                                <div className="space-y-4">
                                    <div data-anim-item>
                                        <KeyValueRow label="الوصف" value={<FormatHtmlContent htmlFromServer={space?.description} />} />
                                    </div>

                                    <div data-anim-item>
                                        <KeyValueRow
                                            label="السعة"
                                            value={space?.capacity ? `${space.capacity} فرد` : "—"}
                                        />
                                    </div>

                                    <div data-anim-item>
                                        <KeyValueRow label="المكان" value={space?.location} />
                                    </div>

                                    {/* Extra meta */}
                                    <div data-anim-item>
                                        <KeyValueRow label="المساحة" value={space?.area_sqm || "—"} compact />
                                    </div>

                                    {/* Add-ons */}
                                    <div data-anim-item className="space-y-2">
                                        <div className="text-sm font-medium">الإضافات</div>
                                        <div className="flex flex-wrap gap-2">
                                            {(space?.amenities || []).length ? (
                                                space.amenities.map((a, idx) => (
                                                    <Badge key={idx} variant="secondary" className="rounded-full">
                                                        {a ? (
                                                            <span className="mr-1 text-muted-foreground">• {a}</span>
                                                        ) : null}
                                                    </Badge>
                                                ))
                                            ) : (
                                                <p className="text-sm text-muted-foreground">لا توجد إضافات.</p>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </TabsContent>

                            {/*  Booking */}
                            <BookingForm spaceID={space?.id} />
                        </div>
                    </Tabs>
                </CardContent>
            </Card>
        </div>
    );
}

export default OnePackageContent;


/** Simple key/value row for details */
function KeyValueRow({ label, value, compact }) {
    return (
        <div className={compact ? "space-y-1" : "space-y-1.5"}>
            <div className="text-sm font-medium">{label}</div>
            <div className="text-sm text-muted-foreground">{value ? value : "—"}</div>
        </div>
    );
}
