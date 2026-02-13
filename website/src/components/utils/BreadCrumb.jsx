import { formatBreadCrumb } from "@/lib/utils";
import { useGSAP } from "@gsap/react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useRef } from "react";
import { Link, useLocation } from "react-router-dom";

gsap.registerPlugin(ScrollTrigger);

const BreadCrumb = () => {
    const location = useLocation();
    const rootRef = useRef(null);

    const rawPathnames = location.pathname.split("/").filter(Boolean);

    const pathnames =
        rawPathnames.length === 3 && rawPathnames[0] === "packages"
            ? rawPathnames.slice(0, -1)
            : rawPathnames;

    const currentPage =
        pathnames.length > 0 ? formatBreadCrumb(pathnames[pathnames.length - 1]) : "الرئيسية";

    useGSAP(
        () => {
            const root = rootRef.current;
            if (!root) return;

            const ctx = gsap.context(() => {
                const title = root.querySelector("[data-bc-title]");
                const pill = root.querySelector("[data-bc-pill]");
                const crumbs = gsap.utils.toArray(root.querySelectorAll("[data-bc-crumb]"));
                const dots = gsap.utils.toArray(root.querySelectorAll("[data-bc-dot]"));

                // initial
                gsap.set(title, { opacity: 0, y: 18, filter: "blur(6px)" });
                gsap.set(pill, { opacity: 0, y: 14, scale: 0.98, filter: "blur(6px)" });
                gsap.set(crumbs, { opacity: 0, y: 10 });
                gsap.set(dots, { opacity: 0, scale: 0.7 });

                const tl = gsap.timeline({
                    scrollTrigger: {
                        trigger: root,
                        start: "top 85%",
                        once: true,
                    },
                });

                tl.to(title, {
                    opacity: 1,
                    y: 0,
                    filter: "blur(0px)",
                    duration: 0.9,
                    ease: "power3.out",
                })
                    .to(
                        pill,
                        {
                            opacity: 1,
                            y: 0,
                            scale: 1,
                            filter: "blur(0px)",
                            duration: 0.75,
                            ease: "power3.out",
                        },
                        0.18
                    )
                    .to(
                        crumbs,
                        {
                            opacity: 1,
                            y: 0,
                            duration: 0.55,
                            ease: "power3.out",
                            stagger: 0.06,
                        },
                        0.35
                    )
                    .to(
                        dots,
                        {
                            opacity: 1,
                            scale: 1,
                            duration: 0.6,
                            ease: "back.out(2)",
                            stagger: 0.08,
                        },
                        0.25
                    );
            }, rootRef);

            return () => ctx.revert();
        },
        { scope: rootRef, dependencies: [location.pathname] } // مهم لو بتتنقل بين الصفحات
    );

    return (
        <section
            ref={rootRef}
            className="relative bg-[#0a2e38] py-20 text-white overflow-hidden"
        >
            <div className="container flex flex-col items-center gap-6">
                {/* Page Title */}
                <h1 data-bc-title className="text-3xl sm:text-5xl font-semibold">
                    {currentPage}
                </h1>

                {/* Breadcrumb pill */}
                <div
                    data-bc-pill
                    className="flex items-center gap-2 rounded-full bg-white/10 px-6 py-2 text-sm"
                >
                    <Link to="/" data-bc-crumb className="text-white/80 hover:text-white transition">
                        الرئيسية
                    </Link>

                    {pathnames.map((segment, index) => {
                        const routeTo = "/" + pathnames.slice(0, index + 1).join("/");
                        const isLast = index === pathnames.length - 1;

                        return (
                            <div key={routeTo} className="flex items-center gap-2">
                                <span data-bc-crumb className="text-white/50">
                                    /
                                </span>

                                {isLast ? (
                                    <span data-bc-crumb className="font-medium text-white">
                                        {formatBreadCrumb(segment)}
                                    </span>
                                ) : (
                                    <Link
                                        to={routeTo}
                                        data-bc-crumb
                                        className="text-white/80 hover:text-white transition"
                                    >
                                        {formatBreadCrumb(segment)}
                                    </Link>
                                )}
                            </div>
                        );
                    })}
                </div>
            </div>
        </section>
    );
};

export default BreadCrumb;
