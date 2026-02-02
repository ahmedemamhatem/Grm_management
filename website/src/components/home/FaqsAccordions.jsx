import { faqsItems } from "@/assets/data";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

import { useGSAP } from "@gsap/react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useRef } from "react";

gsap.registerPlugin(ScrollTrigger);

export function FaqsAccordions() {
  const rootRef = useRef(null);

  useGSAP(
    () => {
      const root = rootRef.current;
      if (!root) return;

      const ctx = gsap.context(() => {
        const items = gsap.utils.toArray(root.querySelectorAll("[data-faq-item]"));

        gsap.set(items, { opacity: 0, y: 18 });

        gsap.to(items, {
          opacity: 1,
          y: 0,
          duration: 0.8,
          ease: "power3.out",
          stagger: 0.12,
          scrollTrigger: {
            trigger: root,
            start: "top 80%",
            once: true,
          },
        });
      }, rootRef);

      return () => ctx.revert();
    },
    { scope: rootRef }
  );

  return (
    <div ref={rootRef}>
      <Accordion type="single" collapsible className="max-w-full space-y-2">
        {faqsItems.map((item) => (
          <AccordionItem
            key={item.value}
            value={item.value}
            data-faq-item
            className="overflow-hidden rounded-lg border bg-white"
          >
            <AccordionTrigger className="px-4 text-right">
              {item.label}
            </AccordionTrigger>
            <AccordionContent className="px-4 text-right">
              {item.answer}
            </AccordionContent>
          </AccordionItem>
        ))}
      </Accordion>
    </div>
  );
}
