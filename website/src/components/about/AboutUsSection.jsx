import testIMG from "@/assets/images/test/hero-test.jpg";
import { useGSAP } from "@gsap/react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { Check, Gem } from "lucide-react";
import { useRef } from "react";
import CustomBadge from "../utils/CustomBadge";

gsap.registerPlugin(ScrollTrigger);

const AboutUsSection = () => {
    const sectionRef = useRef(null);
    const contentRef = useRef(null);

    useGSAP(
        () => {
            const root = sectionRef.current;
            if (!root) return;

            const ctx = gsap.context(() => {
                // اختار كل العناصر النصية اللي هنحركها
                const headerItems = gsap.utils.toArray(root.querySelectorAll("[data-anim='about-text']"));
                const featureCards = gsap.utils.toArray(root.querySelectorAll("[data-anim='about-feature']"));
                const checkItems = gsap.utils.toArray(root.querySelectorAll("[data-anim='about-check']"));

                // initial states
                gsap.set(headerItems, { opacity: 0, y: 18 });
                gsap.set(featureCards, { opacity: 0, y: 18 });
                gsap.set(checkItems, { opacity: 0, y: 14 });

                // timeline واحد للسكشن كله
                const tl = gsap.timeline({
                    scrollTrigger: {
                        trigger: contentRef.current, // أول جزء نصي
                        start: "top 80%",
                        once: true,
                    },
                });

                tl.to(headerItems, {
                    opacity: 1,
                    y: 0,
                    duration: 0.8,
                    ease: "power3.out",
                    stagger: 0.12,
                })
                    .to(
                        featureCards,
                        {
                            opacity: 1,
                            y: 0,
                            duration: 0.7,
                            ease: "power3.out",
                            stagger: 0.12,
                        },
                        0.25
                    )
                    .to(
                        checkItems,
                        {
                            opacity: 1,
                            y: 0,
                            duration: 0.65,
                            ease: "power3.out",
                            stagger: 0.1,
                        },
                        0.35
                    );
            }, sectionRef);

            return () => ctx.revert();
        },
        { scope: sectionRef }
    );

    return (
        <section className="py-16" ref={sectionRef}>
            <div className="container max-w-7xl">
                <div className="grid lg:grid-cols-3 gap-4">
                    {/* الصورة (بدون أنيميشن) */}
                    <div className="relative overflow-hidden rounded-xl about-reveal">
                        <img
                            className="hero-image masked-img object-cover w-full"
                            src={testIMG}
                            alt="about image"
                        />
                    </div>

                    <div className="lg:col-span-2">
                        <div className="flex flex-col gap-3" ref={contentRef}>
                            <CustomBadge title="عن قرم" />
                            <h6 data-anim="about-text" className="text-xl sm:text-4xl text-gray-900">
                                مساحات عمل صُممت بعناية للمحترفين
                            </h6>

                            <p
                                data-anim="about-text"
                                className="text-gray-600 leading-7 text-sm sm:text-base"
                            >
                                أنشأنا مساحة العمل المشتركة هذه لنمنح المحترفين مكانًا يشعر فيه الإنجاز
                                بالسلاسة، وتكون الراحة جزءًا أساسيًا من التجربة.
                            </p>
                        </div>

                        {/* كروت المميزات */}
                        <div className="grid grid-cols-2 gap-3 mt-5">
                            <div data-anim="about-feature" className="flex items-center gap-2">
                                <div className="bg-[#E1F5A3] w-14 h-14 flex justify-center items-center rounded-lg">
                                    <Gem className="text-gray-500 font-extralight" size={24} />
                                </div>
                                <p className="text-gray-500 md:text-xl font-bold">
                                    مساحات عمل <br />
                                    عصرية واحترافية
                                </p>
                            </div>

                            <div data-anim="about-feature" className="flex items-center gap-2">
                                <div className="bg-[#E1F5A3] w-14 h-14 flex justify-center items-center rounded-lg">
                                    <Gem className="text-gray-500 font-extralight" size={24} />
                                </div>
                                <p className="text-gray-500 md:text-xl font-bold">
                                    مصممة لدعم <br />
                                    كل محترف
                                </p>
                            </div>
                        </div>

                        {/* checklist */}
                        <ul className="mt-6 space-y-4">
                            <li
                                data-anim="about-check"
                                className="flex items-center gap-3 text-[14px] text-gray-500"
                            >
                                <span className="inline-flex h-5 w-5 items-center justify-center rounded-[4px] bg-[#DFF2A0] text-[#0B1020]">
                                    <Check className="h-4 w-4" strokeWidth={2.2} />
                                </span>
                                <span>نتبنى نهجًا استباقيًا يهدف إلى تطوير أنظمة عمل متقدمة</span>
                            </li>

                            <li
                                data-anim="about-check"
                                className="flex items-center gap-3 text-[14px] text-gray-500"
                            >
                                <span className="inline-flex h-5 w-5 items-center justify-center rounded-[4px] bg-[#DFF2A0] text-[#0B1020]">
                                    <Check className="h-4 w-4" strokeWidth={2.2} />
                                </span>
                                <span>
                                    نتعاون معك عن قرب لضمان أن تكون كل خطة مصممة بما يناسب احتياجاتك وأهدافك.
                                </span>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
        </section>
    );
};

export default AboutUsSection;
