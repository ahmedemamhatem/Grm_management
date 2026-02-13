import gsap from "gsap";
import { useEffect, useRef, useState } from "react";
import BookingListView from "./BookingListView";
import ProfileContent from "./ProfileContent";
import ProfileSidebar from "./ProfileSidebar";

export default function ProfileSection() {
    const rootRef = useRef(null);
    const sidebarRef = useRef(null);
    const headerRef = useRef(null);
    const cardRef = useRef(null);
    const fieldsRef = useRef(null);

    const [active, setActive] = useState("profile");

    useEffect(() => {
        const ctx = gsap.context(() => {
            gsap.set([sidebarRef.current, headerRef.current, cardRef.current], { opacity: 0, y: 14 });
            gsap.set(fieldsRef.current?.children || [], { opacity: 0, y: 10 });

            const tl = gsap.timeline({ defaults: { duration: 0.7, ease: "power3.out" } });

            tl.to(sidebarRef.current, { opacity: 1, y: 0 })
                .to(headerRef.current, { opacity: 1, y: 0 }, "-=0.45")
                .to(cardRef.current, { opacity: 1, y: 0 }, "-=0.45")
                .to(fieldsRef.current?.children || [], { opacity: 1, y: 0, stagger: 0.08 }, "-=0.4");
        }, rootRef);

        return () => ctx.revert();
    }, [active]);

    return (
        <section ref={rootRef} className="bg-muted/30">
            <div className="container">
                <div className="grid grid-cols-1 gap-6 p-4 lg:grid-cols-[280px_1fr] lg:p-8">
                    <ProfileSidebar active={active} setActive={setActive} sidebarRef={sidebarRef} />
                    {/* content */}
                    <main className="space-y-6">
                        {/* Header */}
                        <div ref={headerRef} className="flex items-start justify-between gap-3">
                            <div>
                                <div className="text-2xl font-bold tracking-tight">
                                    {active === "profile" ? "الصفحة الشخصية" : "الحجوزات"}
                                </div>
                                <div className="text-sm text-muted-foreground">
                                    {active === "profile"
                                        ? "راجع بيانات حسابك وتأكد إنها صحيحة."
                                        : "قائمة الحجوزات الخاصة بك."}
                                </div>
                            </div>
                        </div>

                        {active === "profile" ? (
                            <ProfileContent cardRef={cardRef} fieldsRef={fieldsRef} />
                        ) : (
                            <BookingListView />
                        )}
                    </main>
                </div>
            </div>
        </section>
    );
}
