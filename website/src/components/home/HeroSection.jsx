import heroBG from "@/assets/images/hero-section_bg.png"
import arrowDown from "@/assets/images/icons/h1__banner-arrow.png"
import testImage from "@/assets/images/test/hero-test.jpg"
import { useGSAP } from "@gsap/react"
import gsap from "gsap"
import { MoveUpLeft } from "lucide-react"
import { useRef } from "react"
import { Link } from "react-router-dom"
import { Button } from "../ui/button"
import { revealAnimation } from "@/lib/animations"

const HeroSection = () => {
    const scope = useRef(null)

    useGSAP(
        () => {
            const tl = gsap.timeline({ defaults: { ease: "power3.out" } })

            // ===== TEXT SETUP =====
            gsap.set([".hero-badge", ".hero-title", ".hero-brand", ".hero-desc", ".hero-cta"], {
                opacity: 0,
                y: 20,
                filter: "blur(8px)",
            })


            // ===== HERO CONTAINER =====
            tl.from(".hero_section", {
                y: 80,
                opacity: 0,
                duration: 0.8,
            })

            // ===== TEXT ANIMATION =====
            tl.to(".hero-badge", { opacity: 1, y: 0, filter: "blur(0px)", duration: 0.4 })
                .to(".hero-title", { opacity: 1, y: 0, filter: "blur(0px)", duration: 0.6 }, "<0.05")
                .to(".hero-brand", { opacity: 1, y: 0, filter: "blur(0px)", duration: 0.4 }, "<0.05")
                .to(".hero-desc", { opacity: 1, y: 0, filter: "blur(0px)", duration: 0.5 }, "<0.05")
                .to(".hero-cta", { opacity: 1, y: 0, filter: "blur(0px)", duration: 0.4 }, "<0.05")

            tl.add(
                revealAnimation(".hero-image_reveal", {
                    from: "right",
                    duration: 1.2,
                }),
                "-=0.6"
            )

        },
        { scope }
    )

    return (
        <section className="p-4" ref={scope}>
            <div className="hero_section relative overflow-hidden rounded-2xl bg-[linear-gradient(180deg,#06323D_0%,#052125_57%)] px-6 py-10 md:p-14 lg:h-[calc(100vh-89px)]">

                {/* Decorative Background */}
                <div
                    className="pointer-events-none absolute inset-0 bg-no-repeat bg-top-start opacity-30"
                    style={{ backgroundImage: `url(${heroBG})` }}
                />

                {/* Content */}
                <div className="relative grid h-full items-center gap-10 lg:grid-cols-2">
                    {/* Text */}
                    <div className="max-w-2xl hero-text">
                        <div className="hero-badge inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-white/80 backdrop-blur">
                            <span>⭐</span>
                            <span className="font-medium text-white">4.5</span>
                            <span className="text-white/60">تقييم العملاء</span>
                        </div>

                        <h1 className="hero-title mt-6 text-3xl font-semibold leading-tight text-white md:text-5xl">
                            مساحة عمل حديثة <br />
                            تناسب المحترفين في
                        </h1>

                        <div className="hero-brand mt-2 text-4xl font-bold text-lime-400 md:text-5xl">
                            قرم
                        </div>

                        <p className="hero-desc mt-6 max-w-xl text-sm leading-7 text-white/70">
                            في قرم نوفر لك بيئة عمل مرنة تجمع بين الراحة والإنتاجية،
                            لتساعدك على التركيز وتحقيق أفضل النتائج في عملك.
                        </p>

                        <Link to="/about" className="hero-cta mt-10 flex items-center gap-4">
                            <Button size="lg" className="py-7 text-sm font-semibold shadow-lg group transition duration-150">
                                اكتشف المزيد
                                <span className="inline-flex h-8 w-8 items-center justify-center rounded-tr-md rounded-bl-md bg-white text-[#052125] group-hover:bg-lime-400 group-hover:text-white transition group-hover:-translate-x-0.5">
                                    <MoveUpLeft className="h-5 w-5" />
                                </span>
                            </Button>

                            <img src={arrowDown} alt="arrow down" className="rotate-180 skew-x-12" />
                        </Link>
                    </div>

                    {/* Image */}
                    <div>
                        <div className="overflow-hidden rounded-3xl bg-white/5 p-2">
                            <div className="hero-image_reveal overflow-hidden rounded-3xl">
                                <img
                                    src={testImage}
                                    alt="مساحة عمل قرم"
                                    className="hero-image h-full max-h-[70vh] w-full rounded-3xl object-cover"
                                />
                            </div>
                        </div>
                    </div>

                </div>
            </div>
        </section>
    )
}

export default HeroSection
