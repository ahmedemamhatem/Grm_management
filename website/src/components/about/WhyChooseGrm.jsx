import { useMemo, useRef } from "react";
import { useGSAP } from "@gsap/react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

import { Check, Play } from "lucide-react";

import testIMG from "@/assets/images/test/hero-test.jpg";
import { whyChooseGrmItems } from "@/assets/data";
import CustomBadge from "../utils/CustomBadge";

gsap.registerPlugin(ScrollTrigger);

export default function WhyChooseGrmSection() {
    const rootRef = useRef(null);
    const plans = useMemo(() => whyChooseGrmItems, []);

    const animatePanel = () => {
        const root = rootRef.current;
        if (!root) return;

        const activePanel = root.querySelector('[data-state="active"][role="tabpanel"]');
        if (!activePanel) return;

        const panelCard = activePanel.querySelector("[data-anim='wcu-panel']");
        const items = gsap.utils.toArray(activePanel.querySelectorAll("[data-anim='wcu-item']"));
        const img = activePanel.querySelector("[data-anim='wcu-img']");
        const video = activePanel.querySelector("[data-anim='wcu-video']");

        gsap.killTweensOf([panelCard, ...items, img, video]);

        // initial
        if (panelCard) gsap.set(panelCard, { opacity: 0, y: 10 });
        gsap.set(items, { opacity: 0, y: 10 });
        if (img) gsap.set(img, { opacity: 0, scale: 0.985 });
        if (video) gsap.set(video, { opacity: 0, y: 10 });

        const tl = gsap.timeline();
        tl.to(panelCard, { opacity: 1, y: 0, duration: 0.35, ease: "power2.out" }, 0)
            .to(img, { opacity: 1, scale: 1, duration: 0.5, ease: "power2.out" }, 0.05)
            .to(video, { opacity: 1, y: 0, duration: 0.45, ease: "power2.out" }, 0.08)
            .to(items, { opacity: 1, y: 0, duration: 0.5, ease: "power2.out", stagger: 0.06 }, 0.12);
    };

    // animate the section (tabs + cards)
    useGSAP(
        () => {
            const root = rootRef.current;
            if (!root) return;

            const ctx = gsap.context(() => {
                const heads = gsap.utils.toArray(root.querySelectorAll("[data-anim='wcu-head']"));
                const tabsWrap = root.querySelector("[data-anim='wcu-tabs']");
                const triggers = gsap.utils.toArray(root.querySelectorAll("[data-anim='wcu-tab']"));
                const rightCard = root.querySelector("[data-anim='wcu-right-card']");
                const rightImg = root.querySelector("[data-anim='wcu-right-img']");
                const rightBadge = root.querySelector("[data-anim='wcu-right-badge']");
                const rightText = root.querySelector("[data-anim='wcu-right-text']");

                // initial
                gsap.set(heads, { opacity: 0, y: 18 });
                gsap.set(tabsWrap, { opacity: 0, y: 18 });
                gsap.set(triggers, { opacity: 0, y: 10 });
                gsap.set(rightCard, { opacity: 0, y: 18, scale: 0.99 });
                gsap.set(rightImg, { opacity: 0, scale: 0.99 });
                gsap.set(rightBadge, { opacity: 0, y: 10 });
                gsap.set(rightText, { opacity: 0, y: 10 });

                const tl = gsap.timeline({
                    scrollTrigger: {
                        trigger: root,
                        start: "top 80%",
                        once: true,
                    },
                    onComplete: () => {
                        // بعد دخول السكشن لأول مرة شغّل أنيميشن الـ panel النشط
                        animatePanel();
                    },
                });

                tl.to(heads, {
                    opacity: 1,
                    y: 0,
                    duration: 0.85,
                    ease: "power3.out",
                    stagger: 0.12,
                })
                    .to(
                        tabsWrap,
                        {
                            opacity: 1,
                            y: 0,
                            duration: 0.75,
                            ease: "power3.out",
                        },
                        0.12
                    )
                    .to(
                        triggers,
                        {
                            opacity: 1,
                            y: 0,
                            duration: 0.5,
                            ease: "power2.out",
                            stagger: 0.06,
                        },
                        0.22
                    )
                    .to(
                        rightCard,
                        {
                            opacity: 1,
                            y: 0,
                            scale: 1,
                            duration: 0.75,
                            ease: "power3.out",
                        },
                        0.18
                    )
                    .to(
                        rightImg,
                        {
                            opacity: 1,
                            scale: 1,
                            duration: 0.75,
                            ease: "power3.out",
                        },
                        0.25
                    )
                    .to(
                        rightBadge,
                        { opacity: 1, y: 0, duration: 0.55, ease: "back.out(1.7)" },
                        0.45
                    )
                    .to(
                        rightText,
                        { opacity: 1, y: 0, duration: 0.55, ease: "power2.out" },
                        0.52
                    );
            }, rootRef);

            return () => ctx.revert();
        },
        { scope: rootRef }
    );

    return (
        <section className="py-16" ref={rootRef}>
            <div className="container">
                {/* Header */}
                <div className="flex justify-between items-center gap-3 mb-10">
                    <div className="space-y-4">
                        <CustomBadge title="لماذا تختارنا" />
                        <h6 data-anim="wcu-head" className="text-xl sm:text-2xl text-gray-900">
                            حلول مساحات عمل تناسب كل فريق
                        </h6>
                        <p
                            data-anim="wcu-head"
                            className="max-w-3xl text-sm sm:text-base leading-7 text-gray-900/80"
                        >
                            نوفر بيئة عمل احترافية تجمع بين الراحة والمرونة والإنتاجية — من المكتب المشترك وحتى الحلول المخصصة للشركات.
                        </p>
                    </div>
                </div>

                <div className="grid gap-10 lg:grid-cols-[1fr_460px] lg:items-start">
                    {/* LEFT */}
                    <div data-anim="wcu-tabs">
                        <Tabs defaultValue={plans[0]?.key} onValueChange={animatePanel}>
                            <TabsList className="w-full flex-wrap sm:flex-nowrap justify-start gap-2 bg-transparent p-0">
                                {plans.map((p) => (
                                    <TabsTrigger
                                        key={p.key}
                                        value={p.key}
                                        data-anim="wcu-tab"
                                        className="
                                                            transition-colors duration-300 rounded-full border border-emerald-600/50 bg-white px-4 py-2 text-sm
                                                            data-[state=active]:border-emerald-600/20 data-[state=active]:bg-emerald-600 data-[state=active]:text-white cursor-pointer hover:bg-emerald-600/10 hover:text-emerald-600
                                                        "
                                    >
                                        {p.label}
                                    </TabsTrigger>
                                ))}
                            </TabsList>

                            {plans.map((p) => (
                                <TabsContent key={p.key} value={p.key} className="mt-3">
                                    <Card
                                        data-anim="wcu-panel"
                                        className="relative overflow-hidden rounded-2xl border border-gray-200 bg-white p-6 sm:p-8"
                                    >
                                        <div>
                                            <div data-anim="wcu-item" className="text-sm font-semibold text-gray-500">
                                                تقييمات 5 نجوم
                                            </div>

                                            <h2 data-anim="wcu-item" className="mt-2 text-2xl sm:text-3xl font-semibold text-gray-900">
                                                {p.title}
                                            </h2>

                                            <p data-anim="wcu-item" className="mt-3 text-sm sm:text-base leading-7 text-gray-500">
                                                {p.subtitle === "تواصل معنا"
                                                    ? "نجهّز لك خطة تناسب حجم فريقك وميزانيتك ومتطلباتك التشغيلية."
                                                    : "اختر الخطة المناسبة وابدأ العمل في بيئة مجهزة بكل ما تحتاجه — بدون تعقيد."}
                                            </p>

                                            <ul className="mt-6 space-y-3">
                                                {p.bullets.map((b, i) => (
                                                    <li
                                                        key={i}
                                                        data-anim="wcu-item"
                                                        className="flex items-start gap-3 text-sm text-gray-500"
                                                    >
                                                        <span className="mt-0.5 inline-flex h-6 w-6 shrink-0 items-center justify-center rounded-md bg-[#DFF2A0] text-[#0B1020]">
                                                            <Check className="h-4 w-4" strokeWidth={2.2} />
                                                        </span>
                                                        <span className="leading-7">{b}</span>
                                                    </li>
                                                ))}
                                            </ul>

                                            <div data-anim="wcu-item" className="mt-7 flex items-center gap-3">
                                                <Button className="md:h-12 rounded-full bg-[#0B1020] px-7 text-white hover:bg-[#0B1020]/90">
                                                    {p.priceText}
                                                </Button>
                                                <Button variant="outline" className="md:h-12 rounded-full border-gray-200 px-7 text-gray-900">
                                                    اعرف المزيد
                                                </Button>
                                            </div>
                                        </div>
                                        {/* right small media card 
                                        <div className="grid gap-8 lg:grid-cols-[1fr_220px] lg:items-start">

                                            <div className="space-y-3">
                                                <div
                                                    data-anim="wcu-video"
                                                    className="relative overflow-hidden rounded-2xl border border-gray-200 bg-gray-100"
                                                >
                                                    <img src={testIMG} alt="video" className="h-[140px] w-full object-cover" />
                                                    <button
                                                        type="button"
                                                        className="absolute inset-0 grid place-items-center"
                                                        aria-label="تشغيل الفيديو"
                                                    >
                                                        <span className="inline-flex h-12 w-12 items-center justify-center rounded-full bg-white/90 text-[#0B1020] shadow-sm">
                                                            <Play className="h-5 w-5" />
                                                        </span>
                                                    </button>
                                                </div>

                                                <div data-anim="wcu-item" className="rounded-2xl border border-gray-200 bg-white p-4">
                                                    <div className="text-xs font-semibold tracking-[0.16em] text-[#0B1020]/60">
                                                        ملخص سريع
                                                    </div>
                                                    <div className="mt-2 text-sm text-[#0B1020]/70 leading-7">
                                                        جلسات مرنة، تجهيزات عصرية، تجربة سلسة — وكل شيء جاهز لتبدأ فورًا.
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        */}
                                    </Card>
                                </TabsContent>
                            ))}
                        </Tabs>
                    </div>

                    {/* RIGHT */}
                    <div className="lg:sticky lg:top-24">
                        <Card data-anim="wcu-right-card" className="overflow-hidden rounded-3xl border border-gray-200 bg-white p-0">
                            <div className="relative">
                                <img
                                    data-anim="wcu-right-img"
                                    src={testIMG}
                                    alt="workspace"
                                    className="h-[380px] w-full object-cover sm:h-[460px]"
                                />

                                <div data-anim="wcu-right-badge" className="absolute bottom-5 end-5">
                                    <div className="rounded-full bg-white/90 px-4 py-2 text-sm font-semibold text-[#0B1020] shadow-sm">
                                        موثوق به لدى +100 محترف
                                    </div>
                                </div>
                            </div>

                            <div className="pb-6 px-6">
                                <div data-anim="wcu-right-text" className="text-sm text-gray-500 leading-7">
                                    تجربة عمل منظمة تساعدك على الإنجاز — من لحظة دخولك وحتى نهاية يومك.
                                </div>
                            </div>
                        </Card>
                    </div>
                </div>
            </div>
        </section>
    );
}
