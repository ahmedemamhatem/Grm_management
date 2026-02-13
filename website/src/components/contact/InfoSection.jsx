import { useGSAP } from "@gsap/react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useRef } from "react";
import CustomBadge from "../utils/CustomBadge";
import {
    FacebookIcon,
    InstagramIcon,
    LinkedinIcon,
    MailOpen,
    MapPin,
    PhoneCall,
} from "lucide-react";
import ContactForm from "./ContactForm";
import ContactLocation from "./ContactLocation";

gsap.registerPlugin(ScrollTrigger);

const InfoSection = () => {
    const sectionRef = useRef(null);
    const contentRef = useRef(null);

    useGSAP(
        () => {
            const root = sectionRef.current;
            if (!root) return;

            const ctx = gsap.context(() => {
                const headerItems = gsap.utils.toArray(
                    root.querySelectorAll("[data-anim='contact-text']")
                );

                const blocks = gsap.utils.toArray(root.querySelectorAll("[data-info-block]"));
                const icons = gsap.utils.toArray(root.querySelectorAll("[data-info-icon]"));
                const socials = gsap.utils.toArray(root.querySelectorAll("[data-social]"));

                // initial
                gsap.set(headerItems, { opacity: 0, y: 18 });
                gsap.set(socials, { opacity: 0, y: 10, scale: 0.9 });

                gsap.set(blocks, { opacity: 0, y: 22, scale: 0.985 });
                gsap.set(icons, { opacity: 0, scale: 0.85 });

                const tl = gsap.timeline({
                    scrollTrigger: {
                        trigger: contentRef.current,
                        start: "top 80%",
                        once: true,
                    },
                });

                // header
                tl.to(headerItems, {
                    opacity: 1,
                    y: 0,
                    duration: 0.8,
                    ease: "power3.out",
                    stagger: 0.12,
                })
                    // socials
                    .to(
                        socials,
                        {
                            opacity: 1,
                            y: 0,
                            scale: 1,
                            duration: 0.55,
                            ease: "back.out(1.8)",
                            stagger: 0.06,
                        },
                        0.25
                    )
                    // blocks appear
                    .to(
                        blocks,
                        {
                            opacity: 1,
                            y: 0,
                            scale: 1,
                            duration: 0.75,
                            ease: "power3.out",
                            stagger: 0.12,
                        },
                        0.1
                    )
                    // icons pop
                    .to(
                        icons,
                        {
                            opacity: 1,
                            scale: 1,
                            duration: 0.5,
                            ease: "back.out(2)",
                            stagger: 0.08,
                        },
                        0.28
                    );
            }, sectionRef);

            return () => ctx.revert();
        },
        { scope: sectionRef }
    );

    return (
        <section className="py-16" ref={sectionRef}>
            <div className="container">
                <div className="grid grid-cols-1 gap-2 xl:gap-8 md:grid-cols-2 lg:grid-cols-3">
                    {/* COL 1 */}
                    <div className="space-y-4 md:col-span-2 lg:col-span-1" ref={contentRef}>
                        <CustomBadge title="يسعدنا تواصلك" />
                        <h6 data-anim="contact-text" className="text-xl sm:text-2xl text-gray-900">
                            هل تحتاج إلى مساعدة؟
                        </h6>

                        <div className="flex items-center gap-2">
                            <a
                                data-social
                                href="#"
                                target="_blank"
                                className="w-10 h-10 bg-emerald-600/70 rounded-full flex items-center justify-center"
                            >
                                <FacebookIcon size={20} color="white" />
                            </a>
                            <a
                                data-social
                                href="#"
                                target="_blank"
                                className="w-10 h-10 bg-emerald-600/70 rounded-full flex items-center justify-center"
                            >
                                <LinkedinIcon size={20} color="white" />
                            </a>
                            <a
                                data-social
                                href="#"
                                target="_blank"
                                className="w-10 h-10 bg-emerald-600/70 rounded-full flex items-center justify-center"
                            >
                                <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    viewBox="0 0 1200 1227"
                                    width="20"
                                    height="20"
                                    fill="white"
                                    aria-label="X"
                                >
                                    <path d="M714.163 519.284L1160.89 0H1055.03L667.137 450.887L357.328 0H0L468.492 681.821L0 1226.37H105.866L515.491 750.218L842.672 1226.37H1200L714.137 519.284H714.163ZM569.165 687.828L521.463 619.934L141.961 79.6944H304.017L610.172 515.685L657.874 583.579L1055.08 1147.88H893.022L569.165 687.854V687.828Z" />
                                </svg>
                            </a>
                            <a
                                data-social
                                href="#"
                                target="_blank"
                                className="w-10 h-10 bg-emerald-600/70 rounded-full flex items-center justify-center"
                            >
                                <InstagramIcon size={20} color="white" />
                            </a>
                        </div>
                    </div>

                    {/* COL 2 */}
                    <div className="space-y-4">
                        <div data-info-block className="bg-gray-100 rounded-xl p-6 flex items-center gap-4">
                            <div data-info-icon className="bg-emerald-600/50 rounded-lg p-2">
                                <MapPin size={40} color="white" />
                            </div>
                            <div className="space-y-2">
                                <h6 className="text-lg font-semibold text-gray-900">عنوان فرع الرياض</h6>
                                <p className="text-sm text-gray-500">
                                    الرياض – حي العليا، شارع التحلية، مبنى الأعمال، الدور الثالث
                                </p>
                            </div>
                        </div>

                        <div data-info-block className="bg-gray-100 rounded-xl p-6 flex items-center gap-4">
                            <div data-info-icon className="bg-emerald-600/50 rounded-lg p-2">
                                <MailOpen size={40} color="white" />
                            </div>
                            <div className="space-y-2">
                                <h6 className="text-lg font-semibold text-gray-900">البريد الإلكتروني</h6>
                                <p className="text-sm text-gray-500">example@grm.com</p>
                            </div>
                        </div>
                    </div>

                    {/* COL 3 */}
                    <div className="space-y-4">
                        <div data-info-block className="bg-gray-100 rounded-xl p-6 flex items-center gap-4">
                            <div data-info-icon className="bg-emerald-600/50 rounded-lg p-2">
                                <MapPin size={40} color="white" />
                            </div>
                            <div className="space-y-2">
                                <h6 className="text-lg font-semibold text-gray-900">عنوان فرع جدة</h6>
                                <p className="text-sm text-gray-500">
                                    جدة – حي الشاطئ، طريق الكورنيش، برج الأعمال، الدور الخامس
                                </p>
                            </div>
                        </div>

                        <div data-info-block className="bg-gray-100 rounded-xl p-6 flex items-center gap-4">
                            <div data-info-icon className="bg-emerald-600/50 rounded-lg p-2">
                                <PhoneCall size={40} color="white" />
                            </div>
                            <div className="space-y-2">
                                <h6 className="text-lg font-semibold text-gray-900">الهاتف</h6>
                                <p className="text-sm text-gray-500">+5 55 000 0000</p>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="grid grid-cols-1 gap-3 lg:gap-10 lg:grid-cols-2 mt-10">
                    <ContactForm />
                    <ContactLocation />
                </div>
            </div>
        </section>
    );
};

export default InfoSection;
