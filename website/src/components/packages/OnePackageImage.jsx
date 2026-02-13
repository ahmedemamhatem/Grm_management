import { useGSAP } from "@gsap/react";
import { gsap } from "gsap";
import { useRef } from "react";
import { Badge } from "../ui/badge";
import { Card } from "../ui/card";

const OnePackageImage = ({ image, name, capacity, location }) => {
    const wrapRef = useRef(null);
    const imgRef = useRef(null);
    const stripRef = useRef(null);

    useGSAP(() => {
        // Run GSAP scoped to this component only
        const ctx = gsap.context(() => {
            // Initial states
            gsap.set(wrapRef.current, { opacity: 0, y: 18 });
            gsap.set(imgRef.current, { scale: 1.06 });
            gsap.set(stripRef.current, { opacity: 0, y: 10 });

            // Entrance timeline
            const tl = gsap.timeline({ defaults: { ease: "power3.out" } });

            // Card container fade/slide in
            tl.to(wrapRef.current, { opacity: 1, y: 0, duration: 0.65 }, 0);

            // Image subtle zoom-out
            tl.to(imgRef.current, { scale: 1, duration: 0.9 }, 0.05);

            // Bottom strip pop in
            tl.to(stripRef.current, { opacity: 1, y: 0, duration: 0.45 }, 0.25);

            // Badges stagger
            const badges = stripRef.current?.querySelectorAll("[data-badge]");
            if (badges && badges.length) {
                gsap.fromTo(
                    badges,
                    { opacity: 0, y: 6 },
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
        }, wrapRef);

        return () => ctx.revert();
    }, []);

    return (
        <div ref={wrapRef} className="md:col-span-6 lg:col-span-7">
            <Card className="overflow-hidden rounded-2xl p-0">
                <div className="relative aspect-4/3 w-full md:aspect-16/11">
                    <img
                        ref={imgRef}
                        src={image}
                        alt={name || "Space"}
                        className="h-full w-full object-cover will-change-transform"
                        loading="lazy"
                    />

                    <div className="pointer-events-none absolute inset-0 bg-linear-to-t from-background/55 via-transparent to-transparent" />

                    {/* Bottom info strip */}
                    <div className="absolute bottom-3 right-3 left-3">
                        <div
                            ref={stripRef}
                            className="flex flex-wrap items-center gap-2 rounded-2xl border bg-background/75 p-3 backdrop-blur"
                        >
                            <Badge data-badge className="rounded-full">
                                {capacity || "—"} فرد
                            </Badge>

                            <Badge data-badge variant="secondary" className="rounded-full">
                                {location || "—"}
                            </Badge>
                        </div>
                    </div>
                </div>
            </Card>
        </div>
    );
};

export default OnePackageImage;
