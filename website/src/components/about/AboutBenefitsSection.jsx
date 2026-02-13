import CustomBadge from "../utils/CustomBadge"
import { Link } from "react-router-dom"
import { Button } from "../ui/button"
import { MoveUpLeft } from "lucide-react"
import { useMemo, useRef, useState } from "react";
import { Card } from "@/components/ui/card";
import { useGSAP } from "@gsap/react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

import testImg from "@/assets/images/test/hero-test.jpg";
import { benefitsItems } from "@/assets/data";

gsap.registerPlugin(ScrollTrigger);

export default function AboutBenefitsSection() {
    const sectionRef = useRef(null)
    const contentRef = useRef(null)
    const rootRef = useRef(null);
    const [activeIndex, setActiveIndex] = useState(0);

    const items = useMemo(() => benefitsItems, []);

    // 1) animate the section (left image + cards)
    useGSAP(
        () => {
            const root = rootRef.current;
            if (!root) return;

            const cards = gsap.utils.toArray(root.querySelectorAll("[data-feature-card]"));
            const leftImg = root.querySelector("[data-left-image]");

            gsap.set(leftImg, { opacity: 0, y: 18, scale: 0.985 });
            gsap.set(cards, { opacity: 0, y: 22 });

            gsap
                .timeline({
                    scrollTrigger: {
                        trigger: root,
                        start: "top 80%",
                        once: true,
                    },
                })
                .to(leftImg, { opacity: 1, y: 0, scale: 1, duration: 0.9, ease: "power3.out" })
                .to(
                    cards,
                    { opacity: 1, y: 0, duration: 0.85, ease: "power3.out", stagger: 0.12 },
                    0.1
                );
        },
        { scope: rootRef }
    );

    // 2) activate/deactivate the active card (number + small image)
    useGSAP(
        () => {
            const root = rootRef.current;
            if (!root) return;

            // initial state 
            const nums = root.querySelectorAll("[data-num]");
            const thumbs = root.querySelectorAll("[data-thumb]");
            gsap.set(nums, { autoAlpha: 0 });
            gsap.set(thumbs, { autoAlpha: 0, scale: 0.98 });

            const cards = gsap.utils.toArray(root.querySelectorAll("[data-feature-card]"));

            cards.forEach((card, idx) => {
                const num = card.querySelector("[data-num]");
                const thumbWrap = card.querySelector("[data-thumb]");
                const content = card.querySelector("[data-content]");

                const isActive = idx === activeIndex;

                if (isActive) {
                    gsap.fromTo(
                        num,
                        { autoAlpha: 0, x: -8 },
                        { autoAlpha: 1, x: 0, duration: 0.35, ease: "power2.out" }
                    );

                    gsap.to(thumbWrap, { autoAlpha: 1, scale: 1, duration: 0.35, ease: "power2.out" });

                    // move the content away from the number (smooth)
                    gsap.to(content, { x: 16, duration: 0.35, ease: "power2.out" });

                    gsap.to(card, {
                        boxShadow: "0 10px 30px rgba(0,0,0,0.06)",
                        duration: 0.35,
                        ease: "power2.out",
                    });
                } else {
                    gsap.to(num, { autoAlpha: 0, duration: 0.25, ease: "power2.out" });
                    gsap.to(thumbWrap, { autoAlpha: 0, scale: 0.98, duration: 0.25, ease: "power2.out" });

                    // return the content to its natural position
                    gsap.to(content, { x: 0, duration: 0.25, ease: "power2.out" });

                    gsap.to(card, {
                        boxShadow: "0 0 0 rgba(0,0,0,0)",
                        duration: 0.25,
                        ease: "power2.out",
                    });
                }

            });
        },
        { scope: rootRef, dependencies: [activeIndex] }
    );



    // 3) animate the contact text
    useGSAP(
        () => {
            const ctx = gsap.context(() => {
                const items = gsap.utils.toArray("[data-anim='contact-text']")

                gsap.fromTo(
                    items,
                    { opacity: 0, y: 22 },
                    {
                        opacity: 1,
                        y: 0,
                        duration: 0.8,
                        ease: "power3.out",
                        stagger: 0.12,
                        scrollTrigger: {
                            trigger: contentRef.current,
                            start: "top 80%",
                            once: true,
                        },
                    }
                )
            }, sectionRef)

            return () => ctx.revert()
        },
        { scope: sectionRef }
    )

    return (
        <section ref={rootRef} className='py-16'>
            <div className="container space-y-10">
                <div className='flex justify-between items-center gap-3' ref={contentRef}>
                    <div className='space-y-4'>
                        <CustomBadge title="بعض من مميزات المساحات" />
                        <h6 data-anim="contact-text" className="text-xl sm:text-2xl text-gray-900">خدمات صُممت لتمنحك الراحة</h6>
                    </div>

                    <div data-anim="contact-text" className="pt-1">
                        <Link to="/contact">
                            <Button
                                size="lg"
                                className="py-6 sm:py-7"
                            >
                                تواصل معنا
                                <span className="inline-flex h-8 w-8 items-center justify-center rounded-tr-md rounded-bl-md bg-white text-[#052125] group-hover:bg-lime-400 group-hover:text-white transition group-hover:-translate-x-0.5">
                                    <MoveUpLeft className="h-5 w-5" />
                                </span>
                            </Button>
                        </Link>
                    </div>
                </div>
                <div className="grid grid-cols-1 gap-8 lg:grid-cols-[430px_1fr] lg:items-start">
                    {/* LEFT IMAGE */}
                    <div
                        data-left-image
                        className="overflow-hidden rounded-[28px] bg-gray-100 h-full"
                    >
                        <img
                            src={testImg}
                            alt="feature"
                            className="h-full w-full object-cover"
                        />
                    </div>

                    {/* RIGHT LIST */}
                    <div className="space-y-6">
                        {items.map((it, idx) => (
                            <Card
                                key={it.no}
                                data-feature-card
                                onMouseEnter={() => setActiveIndex(idx)}
                                className={[
                                    "relative overflow-hidden rounded-2xl border border-[#E6E6E6] bg-white",
                                    "px-6 py-6 sm:px-8 sm:py-7",
                                ].join(" ")}
                            >
                                {/* BIG OUTLINED NUMBER */}
                                <div
                                    data-num
                                    className="
                                        pointer-events-none absolute start-6 top-0 z-10 select-none
                                        text-[72px] font-semibold leading-none
                                        text-transparent
                                        [-webkit-text-stroke:1px_rgba(11,16,32,0.22)]
                                    "
                                >
                                    {it.no}
                                </div>

                                <div
                                    data-content
                                    className="flex items-start justify-between flex-col md:flex-row gap-6"
                                >
                                    {/* text */}
                                    <div className="min-w-0">
                                        <h3 className="text-[22px] font-semibold text-[#0B1020]">
                                            {it.title}
                                        </h3>
                                        <p className="mt-2 max-w-[520px] text-[15px] leading-7 text-[#0B1020]/65">
                                            {it.desc}
                                        </p>
                                    </div>

                                    <div
                                        data-thumb
                                        className="shrink-0 overflow-hidden rounded-xl border border-[#E6E6E6] bg-gray-100"
                                    >
                                        <img
                                            src={it.thumb}
                                            alt="thumb"
                                            className=" object-cover sm:h-[86px] sm:w-[132px]"
                                        />
                                    </div>
                                </div>
                            </Card>
                        ))}
                    </div>
                </div>
            </div>
        </section>
    );
}
