import gsap from "gsap"

export const revealAnimation = (target, options) => {
    const {
        from = "right",
        duration = 1.2,
        ease = "power4.out",
        imageSelector = ".hero-image",
        imageScaleFrom = 1.08,
        imageScaleTo = 1,
    } = options

    const closed =
        from === "right"
            ? "inset(0 100% 0 0)"
            : "inset(0 0 0 100%)"

    const open = "inset(0 0% 0 0)"

    gsap.set(target, {
        clipPath: closed,
        willChange: "clip-path",
    })

    gsap.set(imageSelector, {
        scale: imageScaleFrom,
        willChange: "transform",
    })

    const tl = gsap.timeline()

    tl.to(target, {
        clipPath: open,
        duration,
        ease,
    })

    tl.to(
        imageSelector,
        {
            scale: imageScaleTo,
            duration: duration + 0.2,
            ease: "power3.out",
        },
        "<0.05"
    )

    return tl
}
