import { stepsTimelineItems } from '@/assets/data'
import testIMG from "@/assets/images/test/hero-test.jpg"
import { Card, CardContent } from "@/components/ui/card"
import { revealAnimation } from '@/lib/animations'
import { useGSAP } from "@gsap/react"
import { gsap } from "gsap"
import { ScrollTrigger } from "gsap/ScrollTrigger"
import { Check, MoveUpLeft } from 'lucide-react'
import React, { useMemo, useRef } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '../ui/button'
import CustomBadge from '../utils/CustomBadge'

gsap.registerPlugin(ScrollTrigger);

const WorkflowSection = () => {
    const rootRef = useRef(null);
    const sectionRef = useRef(null)
    const contentRef = useRef(null)
    const timelineColRef = useRef(null);
    const progressRef = useRef(null);

    const steps = useMemo(() => stepsTimelineItems, []);

    useGSAP(
        () => {
            const root = rootRef.current;
            const timelineCol = timelineColRef.current;
            const progressEl = progressRef.current;

            const stepEls = Array.from(root.querySelectorAll("[data-step]"));
            const titleEls = Array.from(root.querySelectorAll("[data-step-title]"));
            const bulletEls = Array.from(root.querySelectorAll("[data-bullet]"));

            // initial states
            gsap.set(progressEl, { height: 0 });
            gsap.set(stepEls, { opacity: 1 });
            gsap.set(titleEls, { opacity: 0, y: 10 });
            gsap.set(bulletEls, { opacity: 0, y: 10 });

            // 1) progress line grows as you scroll the whole section 
            ScrollTrigger.create({
                trigger: root,
                start: "top 70%",
                end: "bottom 70%",
                scrub: true,
                onUpdate: (self) => {
                    const colH = timelineCol.getBoundingClientRect().height;
                    const h = Math.max(0, Math.min(colH, colH * self.progress));
                    gsap.set(progressEl, { height: h });
                },
            });



            // 2) reveal each step as it enters
            stepEls.forEach((step, i) => {
                const localTitles = step.querySelectorAll("[data-step-title]");
                const localBullets = step.querySelectorAll("[data-bullet]");
                const dot = step.querySelector("[data-dot]");

                gsap.set(dot, { scale: 0.7, opacity: 0.6 });

                const tl = gsap.timeline({
                    scrollTrigger: {
                        trigger: step,
                        start: "top 78%",
                    },
                });

                tl.to(dot, { scale: 1, opacity: 1, duration: 0.35, ease: "back.out(2)" }, 0)
                    .to(localTitles, { opacity: 1, y: 0, duration: 0.45, ease: "power2.out" }, 0.05)
                    .to(
                        localBullets,
                        { opacity: 1, y: 0, duration: 0.45, ease: "power2.out", stagger: 0.08 },
                        0.12
                    );

                // subtle stagger offset
                tl.timeScale(1 + i * 0.03);
            });


            // 3) reveal the image
            const tl = revealAnimation(".workflow-reveal", {
                from: "right",
                duration: 1.1,
            })

            ScrollTrigger.create({
                trigger: ".workflow-reveal",
                start: "top 80%",
                once: true,
                animation: tl,
            })
        },
        { scope: rootRef }
    );


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
        <section className='py-16' ref={sectionRef}>
            <div className="container">
                <div className='flex justify-between items-center gap-3' ref={contentRef}>
                    <div className='space-y-4'>
                        <CustomBadge title="خطوات العمل" />
                        <h6 data-anim="contact-text" className="text-xl sm:text-2xl text-gray-900">تجربة عمل سلسة صُممت بعناية من أجلك</h6>
                        <p
                            data-anim="contact-text"
                            className="text-gray-600 leading-7 text-sm sm:text-base"
                        >
                            صممنا تجربتنا لتكون بسيطة وسلسة، وتدور بالكامل حول راحتك. <br />
                            من اختيار مساحة العمل وحتى لحظة دخولك، ستجد بيئة أنيقة ومجهزة بكل ما تحتاجه لتعمل براحة وتركيز.
                        </p>
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

                <div ref={rootRef} className="relative mx-auto max-w-6xl p-4">
                    <div className="grid grid-cols-1 gap-10 lg:grid-cols-[460px_1fr] lg:items-start">
                        <Card className="overflow-hidden rounded-3xl border-0 shadow-sm bg-transparent p-0 ">
                            <CardContent className="p-0">
                                <div className="workflow-reveal relative h-[420px] w-full sm:h-[520px] lg:h-[560px] max-h-full">
                                    <img
                                        src={testIMG}
                                        alt="Steps"
                                        className="hero-image object-cover h-full w-full"
                                    />
                                </div>
                            </CardContent>
                        </Card>

                        <div className="relative">
                            <div className="grid grid-cols-[120px_1fr] gap-x-8">
                                <div className="relative">
                                    <div
                                        ref={timelineColRef}
                                        className="relative mx-auto h-full w-[2px]"
                                        aria-hidden="true"
                                    >
                                        <div className="absolute inset-0 bg-[linear-gradient(to_bottom,#CFCFD5_0_6px,transparent_6px_12px)] bg-size-[2px_12px]" />
                                        <div
                                            ref={progressRef}
                                            className="absolute right-0 top-0 w-[2px] bg-[#0B1020]"
                                            style={{ height: 0 }}
                                        />
                                    </div>
                                </div>

                                {/* CONTENT COLUMN */}
                                <div className="space-y-14">
                                    {steps.map((s) => (
                                        <div key={s.id} data-step className="relative">
                                            <div className="relative">
                                                <div
                                                    className="absolute -right-[128px] top-0 grid h-10 w-10 place-items-center rounded-full bg-white"
                                                    aria-hidden="true"
                                                >
                                                    <div className="min-w-[90px] text-[13px] font-semibold tracking-[0.14em] bg-white py-5 text-[#0B1020]/60">
                                                        {s.stepLabel}
                                                    </div>
                                                </div>

                                                <div className="flex items-start gap-6">
                                                    <div className="flex-1">
                                                        <h3
                                                            data-step-title
                                                            className="text-[28px] font-semibold leading-tight text-[#0B1020]"
                                                        >
                                                            {s.title}
                                                        </h3>

                                                        <ul className="mt-5 space-y-4">
                                                            {s.bullets.map((b, idx) => (
                                                                <li key={idx} data-bullet className="flex items-start gap-3">
                                                                    <span className="mt-[2px] inline-flex h-6 w-6 shrink-0 items-center justify-center rounded-md bg-[#DFF2A0] text-[#0B1020]">
                                                                        <Check className="h-4 w-4" strokeWidth={2.2} />
                                                                    </span>
                                                                    <span className="text-[15px] leading-relaxed text-[#0B1020]/70">
                                                                        {b}
                                                                    </span>
                                                                </li>
                                                            ))}
                                                        </ul>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    )
}

export default WorkflowSection