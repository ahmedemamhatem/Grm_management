import { useGSAP } from "@gsap/react";
import gsap from "gsap";
import { useRef } from "react";
import CustomBadge from "../utils/CustomBadge";
import { FaqsAccordions } from "./FaqsAccordions";
import FaqsForm from "./FaqsForm";


const FaqSection = () => {
    const sectionRef = useRef(null);
    const contentRef = useRef(null);

    useGSAP(
        () => {
            const ctx = gsap.context(() => {
                const headerItems = gsap.utils.toArray("[data-anim='faq-text']");
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
            }, sectionRef);

            return () => ctx.revert();
        },
        { scope: sectionRef }
    );


    return (
        <section className='py-16' ref={sectionRef}>
            <div className="container">
                <div className="flex flex-col items-center gap-3 mb-10" ref={contentRef}>
                    <CustomBadge title="الأسئلة الشائعة" />
                    <h6 data-anim="faq-text" className="text-xl sm:text-2xl text-gray-900">
                        أسئلة قد تهمك
                    </h6>
                </div>
                <div className="grid lg:grid-cols-2 gap-8 items-center">
                    <FaqsAccordions />
                    <FaqsForm />
                </div>
            </div>
        </section>
    )
}

export default FaqSection