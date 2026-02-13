import { Tabs } from "@/components/ui/tabs";
import { GetAllPackagesHook } from "@/logic";
import { useGSAP } from "@gsap/react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useEffect, useRef, useState } from "react";
import PackagesContent from "./PackagesContent";
import PackagesList from "./PackagesList";

gsap.registerPlugin(ScrollTrigger);

export default function PackagesContainer() {
    const rootRef = useRef(null);
    const { isLoading, packages } = GetAllPackagesHook();
    const [activeTab, setActiveTab] = useState("");
    const [packagesList, setPackagesList] = useState([]);

    useEffect(() => {
        if (packages && Object.keys(packages).length > 0) {
            setPackagesList(Object.keys(packages));
            setActiveTab(Object.keys(packages)[0]);
        }
    }, [packages]);

    // animate the section (left pills + right panel)
    useGSAP(
        () => {
            if (isLoading) return;

            const raf = requestAnimationFrame(() => {
                const root = rootRef.current;
                if (!root) return;

                const activePanel = root.querySelector(
                    '[role="tabpanel"][data-state="active"]'
                );
                if (!activePanel) return;

                const imgs = activePanel.querySelectorAll("[data-anim='panel-img']");
                const titles = activePanel.querySelectorAll("[data-anim='panel-title']");
                const btns = activePanel.querySelectorAll("[data-anim='panel-btn']");

                const targets = [...imgs, ...titles, ...btns].filter(Boolean);
                if (!targets.length) return;

                gsap.killTweensOf(targets);

                if (imgs) gsap.set(imgs, { opacity: 0, scale: 0.985 });
                if (titles) gsap.set(titles, { opacity: 0, y: 10 });
                if (btns) gsap.set(btns, { opacity: 0, y: 10 });

                const tl = gsap.timeline({ defaults: { ease: "power2.out" } });

                if (imgs) tl.to(imgs, { opacity: 1, scale: 1, duration: 0.5 }, 0);
                if (titles) tl.to(titles, { opacity: 1, y: 0, duration: 0.4 }, 0.08);
                if (btns) tl.to(btns, { opacity: 1, y: 0, duration: 0.4 }, 0.24);
            });

            return () => cancelAnimationFrame(raf);
        },
        {
            scope: rootRef,
            dependencies: [activeTab, isLoading],
        }
    );

    return (
        <section ref={rootRef} className="py-16">
            <div className="container">
                <Tabs value={activeTab} onValueChange={setActiveTab} >
                    <div className="grid gap-8 xl:grid-cols-[1fr_420px] lg:items-start">
                        
                        <PackagesContent packagesList={packagesList} isLoading={isLoading} packages={packages} />
                        <PackagesList packagesList={packagesList} isLoading={isLoading} />
                    </div>
                </Tabs>
            </div>
        </section>
    );
}
