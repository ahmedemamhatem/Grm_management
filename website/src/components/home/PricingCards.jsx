import { pricingItems } from "@/assets/data";
import currancy_logo from "@/assets/images/icons/currancy.png";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useGSAP } from "@gsap/react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { Check } from "lucide-react";
import { useMemo, useRef } from "react";

gsap.registerPlugin(ScrollTrigger);

const PricingCards = () => {
    const pricingRef = useRef(null);

    const plans = useMemo(
        () => pricingItems,
        []
    );

    useGSAP(
        () => {
            const root = pricingRef.current;
            if (!root) return;

            const cards = gsap.utils.toArray(root.querySelectorAll("[data-price-card]"));
            const ribbons = gsap.utils.toArray(root.querySelectorAll("[data-ribbon]"));
            const checks = gsap.utils.toArray(root.querySelectorAll("[data-check]"));

            gsap.set(cards, { opacity: 0, y: 28, scale: 0.98 });
            gsap.set(ribbons, { opacity: 0, y: -12, rotate: -45 });
            gsap.set(checks, { opacity: 0, scale: 0.8 });

            const tl = gsap.timeline({
                scrollTrigger: {
                    trigger: root,
                    start: "top 80%",
                    once: true,
                },
            });

            tl.to(cards, {
                opacity: 1,
                y: 0,
                scale: 1,
                duration: 0.9,
                ease: "power3.out",
                stagger: 0.12,
            })
                .to(
                    ribbons,
                    {
                        opacity: 1,
                        y: 0,
                        duration: 0.55,
                        ease: "power3.out",
                        stagger: 0.12,
                    },
                    0.15
                )
                .to(
                    checks,
                    {
                        opacity: 1,
                        scale: 1,
                        duration: 0.45,
                        ease: "back.out(2)",
                        stagger: 0.03,
                    },
                    0.25
                );
        },
        { scope: pricingRef }
    );

    return (
        <div ref={pricingRef} className="mx-auto max-w-6xl">
            <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
                {plans.map((p) => (
                    <Card
                        key={p.id}
                        data-price-card
                        className="relative overflow-hidden rounded-xl border border-[#E6E6E6] bg-white shadow-none"
                    >
                        {/* recommended ribbon */}
                        {p.featured && (
                            <div data-ribbon className="pointer-events-none absolute -right-8 top-5">
                                <div className="rotate-90 bg-[#B7F10A] px-10 py-2 text-[11px] font-semibold tracking-[0.14em] text-[#0B1020]">
                                    موصى به
                                </div>
                            </div>
                        )}


                        {/* top */}
                        <div className="p-10 pb-8">
                            <h3 className="text-[20px] font-semibold text-gray-900">{p.title}</h3>

                            <div className="mt-3 flex items-end gap-2">
                                <div className="text-[46px] font-semibold leading-none tracking-tight text-gray-900 ">
                                    {p.price}

                                </div>
                                <div className="pb-[6px] text-[14px] text-gray-500 flex items-center gap-2">
                                    <img width={15} height={15} src={currancy_logo} alt="rial logo" />
                                    <span>
                                        {p.period}
                                    </span>
                                </div>
                            </div>

                            <p className="mt-5 text-[14px] text-gray-500">{p.subtitle}</p>

                            <div className="mt-8">
                                <Button variant={p.featured ? "default" : "outline"} className="w-full py-7">
                                    احجز الان
                                </Button>
                            </div>
                        </div>

                        {/* divider */}
                        <div className="h-px w-full bg-[#E6E6E6]" />

                        {/* features */}
                        <div className="p-10 pt-8">
                            <div className="text-[12px] font-semibold tracking-[0.18em] text-[#0B1020]">
                                مميزات
                            </div>
                            <div className="mt-2 text-[14px] text-[#0B1020]/60">
                                يشمل جميع مزايا الباقة المجانية
                            </div>

                            <ul className="mt-6 space-y-4">
                                {p.features.map((f, idx) => (
                                    <li key={idx} className="flex items-center gap-3 text-[14px] text-[#0B1020]/70">
                                        <span
                                            data-check
                                            className="inline-flex h-5 w-5 items-center justify-center rounded-[4px] bg-[#DFF2A0] text-[#0B1020]"
                                        >
                                            <Check className="h-4 w-4" strokeWidth={2.2} />
                                        </span>
                                        <span>{f}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </Card>
                ))}
            </div>
        </div>
    );
};

export default PricingCards;
