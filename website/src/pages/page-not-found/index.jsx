import gsap from "gsap";
import React, { useEffect, useRef } from "react";
import { Link } from "react-router-dom";

import { SetMetaTags } from "@/components";
import { Button } from "@/components/ui/button";

import bg from "@/assets/images/page_not_found.png";

function PageNotFound() {
    const rootRef = useRef(null);

    const codeRef = useRef(null);
    const titleRef = useRef(null);
    const descRef = useRef(null);
    const actionsRef = useRef(null);

    useEffect(() => {
        // Meta
        SetMetaTags({
            title: "٤٠٤ - الصفحة غير موجودة",
            description: "",
            keywords: "",
        });

        // GSAP
        const ctx = gsap.context(() => {
            const els = [codeRef.current, titleRef.current, descRef.current, actionsRef.current].filter(Boolean);

            gsap.set(els, { autoAlpha: 0, y: 16 });

            gsap
                .timeline({ defaults: { ease: "power3.out" } })
                .to(codeRef.current, { autoAlpha: 1, y: 0, duration: 0.55 }, 0.05)
                .to(titleRef.current, { autoAlpha: 1, y: 0, duration: 0.5 }, 0.15)
                .to(descRef.current, { autoAlpha: 1, y: 0, duration: 0.5 }, 0.22)
                .to(actionsRef.current, { autoAlpha: 1, y: 0, duration: 0.5 }, 0.3);
        }, rootRef);

        return () => ctx.revert();
    }, []);

    return (
        <section
            ref={rootRef}
            className="relative overflow-hidden bg-cover bg-center bg-no-repeat py-14"
            style={{
                backgroundImage: `url(${bg})`,

            }}
        >
            <div className="absolute inset-0 bg-white/70" />
            <div className="container">
                <div className="relative mx-auto flex max-w-6xl items-center px-6">
                    <div className="w-full">
                        <div className="mx-auto max-w-2xl text-center">
                            <h1
                                ref={codeRef}
                                className="mt-8 text-[84px] font-extrabold leading-none tracking-tight md:text-[120px]"
                            >
                                ٤٠٤
                            </h1>

                            <h2 ref={titleRef} className="mt-3 text-2xl font-semibold tracking-tight md:text-3xl">
                                الصفحة غير موجودة
                            </h2>

                            <p ref={descRef} className="mt-4 text-base leading-relaxed text-muted-foreground md:text-lg">
                                غالباً تم تغيير الرابط أو تم حذف الصفحة
                            </p>

                            <div
                                ref={actionsRef}
                                className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row"
                            >
                                <Link to="/">
                                    <Button size="lg" className="min-w-[180px]">
                                        الرجوع للرئيسية
                                    </Button>
                                </Link>

                                <Button
                                    size="lg"
                                    variant="outline"
                                    className="min-w-[180px]"
                                    onClick={() => window.history.back()}
                                >
                                    رجوع
                                </Button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );

}

export default PageNotFound;
