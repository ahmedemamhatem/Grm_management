import { Card, CardHeader } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { GetClientsHook } from "@/logic";
import { useGSAP } from "@gsap/react";
import gsap from "gsap";
import ScrollTrigger from "gsap/ScrollTrigger";
import { useMemo, useRef } from "react";
import ClientCard from "./ClientCard";

gsap.registerPlugin(ScrollTrigger);

function ClientsSection() {
    const { isLoading, clients } = GetClientsHook();
    const containerRef = useRef(null);
    const animateKey = useMemo(() => (isLoading ? 0 : (clients?.length ?? 0)), [isLoading, clients?.length]);

    console.log(clients);

    useGSAP(
        () => {
            ScrollTrigger.getAll().forEach((t) => {
                if (t?.vars?.id?.startsWith("client-card-")) t.kill();
                if (t?.vars?.id === "client-card-batch") t.kill();
            });

            const cards = gsap.utils.toArray(".client-card");
            gsap.set(cards, { y: 18, opacity: 0, scale: 0.985 });

            ScrollTrigger.batch(cards, {
                id: "client-card-batch",
                start: "top 85%",
                once: true,
                onEnter: (batch) => {
                    gsap.to(batch, {
                        y: 0,
                        opacity: 1,
                        scale: 1,
                        duration: 0.55,
                        ease: "power2.out",
                        stagger: 0.08,
                        overwrite: true,
                    });
                },
            });

            return () => {
                ScrollTrigger.getAll().forEach((t) => {
                    if (t?.vars?.id?.startsWith("client-card-") || t?.vars?.id === "client-card-batch") {
                        t.kill();
                    }
                });
            };
        },
        { scope: containerRef, dependencies: [animateKey] }
    );

    return (
        <section ref={containerRef} className="py-14">
            <div className="container">
                {isLoading ? (
                    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 sm:gap-4 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6">
                        {Array.from({ length: 3 }).map((_, i) => (
                            <Card key={i} className="bg-white/5 border-white/10 p-3">
                                <div className="flex items-start gap-3">
                                    <Skeleton className="h-12 w-12 rounded-lg" />
                                    <div className="flex-1 space-y-2">
                                        <Skeleton className="h-4 w-3/4" />
                                        <Skeleton className="h-3 w-full" />
                                        <Skeleton className="h-3 w-5/6" />
                                    </div>
                                </div>
                            </Card>
                        ))}
                    </div>
                ) : clients && clients?.length === 0 ? (
                    <Card className="bg-white/5 border-white/10">
                        <CardHeader className="pb-0">
                            <div className="text-base font-medium">لا توجد نتائج</div>
                        </CardHeader>
                    </Card>
                ) : (
                    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 sm:gap-4 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6">
                        {clients && clients?.length > 0 && clients?.map((client) => (
                            <ClientCard
                                key={client.name}
                                image={client.logo}
                                name={client.customer_name}
                                description={client.description_ar || client.description}
                            />
                        ))}
                    </div>
                )}
            </div>
        </section>
    );
}

export default ClientsSection;
