import { testimonialsItems } from "@/assets/data";
import testIMG from "@/assets/images/test/hero-test.jpg";
import { useGSAP } from "@gsap/react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { Quote } from "lucide-react";
import { useRef } from "react";
import CustomBadge from "../utils/CustomBadge";

gsap.registerPlugin(ScrollTrigger);

const TestimonialsSection = () => {
    const sectionRef = useRef(null);
    const contentRef = useRef(null);

    useGSAP(
        () => {
            const ctx = gsap.context(() => {
                // 1) section header animation
                const headerItems = gsap.utils.toArray("[data-anim='testimonials-text']");
                gsap.fromTo(
                    headerItems,
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
                );

                // 2) hero image animation
                const heroImg = sectionRef.current?.querySelector("[data-hero-img]");
                if (heroImg) {
                    gsap.fromTo(
                        heroImg,
                        { opacity: 0, scale: 1.04 },
                        {
                            opacity: 1,
                            scale: 1,
                            duration: 0.9,
                            ease: "power3.out",
                            scrollTrigger: {
                                trigger: heroImg,
                                start: "top 85%",
                                once: true,
                            },
                        }
                    );
                }

                // 3) testimonials cards animation
                const cols = gsap.utils.toArray("[data-testimonial-col]");
                gsap.set(cols, { opacity: 0, y: 26 });

                gsap.to(cols, {
                    opacity: 1,
                    y: 0,
                    duration: 0.9,
                    ease: "power3.out",
                    stagger: 0.12,
                    scrollTrigger: {
                        trigger: sectionRef.current,
                        start: "top 75%",
                        once: true,
                    },
                });

                // 4) inner cards animation
                cols.forEach((col) => {
                    const cards = col.querySelectorAll("[data-testimonial-card]");
                    if (!cards.length) return;

                    gsap.set(cards, { opacity: 0, y: 18, scale: 0.98 });

                    gsap.to(cards, {
                        opacity: 1,
                        y: 0,
                        scale: 1,
                        duration: 0.75,
                        ease: "power3.out",
                        stagger: 0.12,
                        scrollTrigger: {
                            trigger: col,
                            start: "top 82%",
                            once: true,
                        },
                    });
                });
            }, sectionRef);

            return () => ctx.revert();
        },
        { scope: sectionRef }
    );

    return (
        <section className="py-16 bg-gray-50" ref={sectionRef}>
            <div className="container">
                <div className="flex flex-col items-center gap-3" ref={contentRef}>
                    <CustomBadge title="آراء أعضائنا" />
                    <h6 data-anim="testimonials-text" className="text-xl sm:text-2xl text-gray-900">
                        قصص وتجارب أعضائنا معنا
                    </h6>
                </div>

                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-3 mt-5">
                    <div className="rounded-lg overflow-hidden" data-hero-img>
                        <img className="w-full h-full object-cover" src={testIMG} alt="testimonials image" />
                    </div>

                    {testimonialsItems.map((item, index) => (
                        <div
                            key={index}
                            data-testimonial-col
                            className={`flex ${index % 2 === 0 ? "flex-col" : "flex-col-reverse"} gap-3`}
                        >
                            <div data-testimonial-card className="bg-white p-6 rounded-lg flex gap-4 items-center shadow-lg">
                                <img className="w-10 h-10 rounded-full" src={testIMG} alt="testimonials image" />
                                <div>
                                    <h6 className="text-gray-900">{item.name}</h6>
                                    <p className="text-gray-500">{item.title}</p>
                                </div>
                            </div>

                            <div data-testimonial-card className="bg-white p-6 rounded-lg shadow-lg flex-1">
                                <div className="flex justify-between items-center pb-7">
                                    <Quote size={30} className="text-gray-200" />
                                    <span>⭐⭐⭐⭐⭐</span>
                                </div>
                                <p className="text-gray-600 leading-relaxed">{item.text}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
};

export default TestimonialsSection;
