import logo from "@/assets/images/logo.png";
import { Facebook, Instagram, Linkedin, Mail, MapPin, Phone, Twitter } from "lucide-react";
import { Link } from "react-router-dom";

import { useGSAP } from "@gsap/react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useRef } from "react";

gsap.registerPlugin(ScrollTrigger);

const Footer = () => {
    const footerRef = useRef(null);

    useGSAP(
        () => {
            const root = footerRef.current;
            if (!root) return;

            const ctx = gsap.context(() => {
                const cols = gsap.utils.toArray(root.querySelectorAll("[data-footer-col]"));
                const socials = gsap.utils.toArray(root.querySelectorAll("[data-footer-social]"));
                const divider = root.querySelector("[data-footer-divider]");
                const copy = root.querySelector("[data-footer-copy]");
                const logoEl = root.querySelector("[data-footer-logo]");

                // initial
                gsap.set(cols, { opacity: 0, y: 24 });
                gsap.set(socials, { opacity: 0, y: 10, scale: 0.95 });
                if (divider) gsap.set(divider, { scaleX: 0, transformOrigin: "center" });
                if (copy) gsap.set(copy, { opacity: 0, y: 10 });
                if (logoEl) gsap.set(logoEl, { opacity: 0, y: 10 });

                const tl = gsap.timeline({
                    scrollTrigger: {
                        trigger: root,
                        start: "top 85%",
                        once: true,
                    },
                });

                tl.to(logoEl, {
                    opacity: 1,
                    y: 0,
                    duration: 0.6,
                    ease: "power3.out",
                })
                    .to(
                        cols,
                        {
                            opacity: 1,
                            y: 0,
                            duration: 0.85,
                            ease: "power3.out",
                            stagger: 0.12,
                        },
                        0.05
                    )
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
                        0.35
                    )
                    .to(
                        divider,
                        {
                            scaleX: 1,
                            duration: 0.7,
                            ease: "power2.out",
                        },
                        0.55
                    )
                    .to(
                        copy,
                        {
                            opacity: 1,
                            y: 0,
                            duration: 0.6,
                            ease: "power3.out",
                        },
                        0.75
                    );
            }, footerRef);

            return () => ctx.revert();
        },
        { scope: footerRef }
    );

    return (
        <footer ref={footerRef} className="bg-gray-50 pt-16">
            <div className="container">
                <div className="grid gap-10 md:grid-cols-2 lg:grid-cols-4">
                    <div data-footer-col className="space-y-4">
                        <img data-footer-logo width={50} src={logo} alt="شعار قرم" />

                        <p className="text-sm leading-7 text-gray-600">
                            نوفر مساحات عمل عصرية ومتكاملة تساعدك على التركيز، الإنتاج،
                            وبناء أعمالك في بيئة مريحة ومحفزة.
                        </p>

                        <div className="flex items-center gap-3">
                            <a data-footer-social className="text-emerald-400 hover:text-[#0B1020]" href="#">
                                <Facebook size={18} />
                            </a>
                            <a data-footer-social className="text-emerald-400 hover:text-[#0B1020]" href="#">
                                <Twitter size={18} />
                            </a>
                            <a data-footer-social className="text-emerald-400 hover:text-[#0B1020]" href="#">
                                <Instagram size={18} />
                            </a>
                            <a data-footer-social className="text-emerald-400 hover:text-[#0B1020]" href="#">
                                <Linkedin size={18} />
                            </a>
                        </div>
                    </div>

                    <div data-footer-col className="space-y-4">
                        <h4 className="text-lg font-semibold text-gray-900">روابط سريعة</h4>
                        <ul className="space-y-2 text-sm">
                            <li><Link className="text-gray-500 transition-all duration-150 hover:translate-x-1 hover:text-emerald-400" to="/">الرئيسية</Link></li>
                            <li><Link className="text-gray-500 transition-colors duration-150 hover:translate-x-1 hover:text-emerald-400" to="/about">من نحن</Link></li>
                            <li><Link className="text-gray-500 transition-colors duration-150 hover:translate-x-1 hover:text-emerald-400" to="/">الأسعار</Link></li>
                            <li><Link className="text-gray-500 transition-colors duration-150 hover:translate-x-1 hover:text-emerald-400" to="/contact">تواصل معنا</Link></li>
                        </ul>
                    </div>

                    <div data-footer-col className="space-y-4">
                        <h4 className="text-lg font-semibold text-gray-900">خدماتنا</h4>
                        <ul className="space-y-2 text-sm text-gray-600">
                            <li>مساحات عمل مشتركة</li>
                            <li>مكاتب خاصة</li>
                            <li>غرف اجتماعات</li>
                        </ul>
                    </div>

                    <div data-footer-col className="space-y-4">
                        <h4 className="text-lg font-semibold text-gray-900">تواصل معنا</h4>
                        <ul className="space-y-3 text-sm text-gray-600">
                            <li className="flex items-start gap-2">
                                <MapPin size={16} className="mt-1" />
                                <span>الرياض، المملكة العربية السعودية</span>
                            </li>
                            <li className="flex items-center gap-2">
                                <Phone size={16} />
                                <span>+966 55 000 0000</span>
                            </li>
                            <li className="flex items-center gap-2">
                                <Mail size={16} />
                                <span>info@company.com</span>
                            </li>
                        </ul>
                    </div>
                </div>

                <div data-footer-divider className="mt-12 border-t border-gray-200" />

                <p data-footer-copy className="text-center text-sm text-gray-500 py-5">
                    © {new Date().getFullYear()} جميع الحقوق محفوظة قرم
                </p>
            </div>
        </footer>
    );
};

export default Footer;
