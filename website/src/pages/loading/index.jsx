import gsap from "gsap";
import React, { useLayoutEffect, useRef } from "react";

export default function LoadingPage() {
  const rootRef = useRef(null);
  const arcRef = useRef(null);
  const lettersRef = useRef([]);

  useLayoutEffect(() => {
    const green = "#B7F400";
    const gray = "#BDBDBD";

    const ctx = gsap.context(() => {
      // spinner rotate
      gsap.to(arcRef.current, {
        rotate: 360,
        duration: 1.05,
        ease: "none",
        repeat: -1,
        transformOrigin: "50% 50%",
      });

      // loading letters animation
      const letters = lettersRef.current.filter(Boolean);
      gsap.set(letters, { color: gray });

      gsap
        .timeline({ repeat: -1 })
        .to(letters, {
          color: green,
          duration: 0.22,
          stagger: 0.085,
          ease: "power1.out",
        })
        .to(
          letters,
          {
            color: gray,
            duration: 0.22,
            stagger: 0.085,
            ease: "power1.in",
          },
          "+=0.12"
        )
        .to({}, { duration: 0.18 });

      // fade in
      gsap.fromTo(
        rootRef.current,
        { opacity: 0 },
        { opacity: 1, duration: 0.4, ease: "power2.out" }
      );
    }, rootRef);

    return () => ctx.revert();
  }, []);

  return (
    <div
      ref={rootRef}
      className="fixed inset-0 z-99999 grid place-items-center bg-white text-start"
      dir="ltr"
    >
      <div className="-translate-y-3 flex flex-col items-center gap-10">
        <svg
          width="160"
          height="160"
          viewBox="0 0 86 86"
          className="block"
        >
          <circle
            cx="43"
            cy="43"
            r="22"
            fill="none"
            stroke="#DFE8F0"
            strokeWidth="2.2"
            strokeLinecap="round"
            opacity="0.9"
          />
          <circle
            ref={arcRef}
            cx="43"
            cy="43"
            r="22"
            fill="none"
            stroke="#B7F400"
            strokeWidth="2.2"
            strokeLinecap="round"
            strokeDasharray="34 140"
          />
        </svg>


        <div className="select-none font-semibold leading-none text-[36px] md:text-[64px] tracking-[0.65em] pl-[0.65em] text-[#BDBDBD]">
          {"LOADING".split("").map((ch, i) => (
            <span
              key={i}
              ref={(el) => (lettersRef.current[i] = el)}
              className="inline-block"
            >
              {ch}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
