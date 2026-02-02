import { featuresItems } from "@/assets/data";
import { useGSAP } from "@gsap/react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useRef } from "react";

gsap.registerPlugin(ScrollTrigger);


export default function FeaturesSection() {
    const root = useRef(null);

    useGSAP(
        () => {
            const cards = gsap.utils.toArray(".feature-card");

            // entrance: stagger by grid order
            gsap.set(cards, { opacity: 0, y: 26 });

            // prep arc draw (both paths)
            cards.forEach((card) => {
                const thin = card.querySelector(".arc-thin");
                const icon = card.querySelector(".icon-wrap");
                const title = card.querySelector(".title");

                const len = thin.getTotalLength();
                gsap.set(thin, { strokeDasharray: len, strokeDashoffset: len });

                gsap.set(icon, { scale: 0.85, opacity: 0 });
                gsap.set(title, { opacity: 0, y: 10 });

                const tl = gsap.timeline({
                    scrollTrigger: {
                        trigger: root.current,
                        start: "top 75%",
                        once: true,
                    },
                });
                return tl;
            });

            // global timeline with nice stagger
            const master = gsap.timeline({
                scrollTrigger: {
                    trigger: root.current,
                    start: "top 75%",
                    once: true,
                },
            });

            master.to(cards, {
                opacity: 1,
                y: 0,
                duration: 0.7,
                ease: "power3.out",
                stagger: { each: 0.12, from: "start" },
            });

            // arcs draw (slightly after cards appear)
            cards.forEach((card, i) => {
                const thin = card.querySelector(".arc-thin");
                const thick = card.querySelector(".arc-thick");
                const icon = card.querySelector(".icon-wrap");
                const title = card.querySelector(".title");

                master.to(
                    [thin, thick],
                    { strokeDashoffset: 0, duration: 1, ease: "power2.out" },
                    0.15 + i * 0.12
                );

                master.to(
                    icon,
                    { opacity: 1, scale: 1, duration: 0.55, ease: "back.out(2)" },
                    0.25 + i * 0.12
                );

                master.to(
                    title,
                    { opacity: 1, y: 0, duration: 0.45, ease: "power2.out" },
                    0.32 + i * 0.12
                );
            });
        },
        { scope: root }
    );


    return (
        <section ref={root} className="w-full bg-gray-50 py-16">
            <div className="container">
                <div className="grid grid-cols-1 gap-y-10 sm:grid-cols-2 lg:grid-cols-4 lg:gap-y-16">
                    {featuresItems.slice(0, 4).map((it) => (
                        <div key={it.no} className="flex justify-center">
                            <FeatureCard no={it.no} title={it.title} IconComp={it.Icon} />
                        </div>
                    ))}
                </div>

                <div className="mt-10 grid grid-cols-1 gap-y-10 sm:grid-cols-2 lg:grid-cols-3 lg:gap-y-16">
                    {featuresItems.slice(4).map((it) => (
                        <div key={it.no} className="flex justify-center">
                            <FeatureCard
                                no={it.no}
                                title={it.title}
                                IconComp={it.Icon}
                            />
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}



function FeatureCard({ no, title, IconComp }) {


    return (
        <div className="feature-card group relative flex w-[290px] flex-col items-center text-center">
            {/* Arc */}
            <svg
                className="arc absolute -top-2 left-1/2 -translate-x-1/2 w-[290px] h-[150px] pointer-events-none"
                viewBox="0 0 290 150"
                fill="none"
                aria-hidden="true"
            >
                <path
                    className="arc-thin"
                    d="M10 145C38 45 105 10 145 10C185 10 252 45 280 145"
                    stroke="#E7E7E7"
                    strokeWidth="3"
                    strokeLinecap="round"
                />
            </svg>

            <div className="mt-7 text-[22px] font-semibold text-[#0B1020]">
                {no}
            </div>

            <div className="icon-wrap mt-6 grid h-16 w-16 place-items-center rounded-full bg-[#DFF2A0] text-[#0B1020] shadow-sm transition-transform duration-300 group-hover:scale-[1.06]">
                <IconComp className="h-6 w-6" strokeWidth={1.6} />
            </div>

            <div className="title mt-5 whitespace-pre-line text-[22px] leading-tight font-semibold text-[#0B1020]">
                {title}
            </div>

            <div className="pointer-events-none absolute inset-0 rounded-2xl transition-transform duration-300 group-hover:-translate-y-1" />
        </div>
    );
}