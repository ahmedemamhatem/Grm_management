import experience_img from "@/assets/images/icons/about_experience.png"
import testImg from "@/assets/images/test/hero-test.jpg"
import { MoveUpLeft } from "lucide-react"
import { useRef } from "react"
import { Link } from "react-router-dom"
import { Button } from "../ui/button"
import CustomBadge from "../utils/CustomBadge"

import { revealAnimation } from "@/lib/animations"
import { useGSAP } from "@gsap/react"
import gsap from "gsap"
import { ScrollTrigger } from "gsap/ScrollTrigger"

gsap.registerPlugin(ScrollTrigger)

const AboutSection = () => {
    const sectionRef = useRef(null)
    const contentRef = useRef(null)

    useGSAP(
        () => {
            const ctx = gsap.context(() => {
                const items = gsap.utils.toArray("[data-anim='about-text']")

                gsap.fromTo(
                    items,
                    { opacity: 0, y: 22 },
                    {
                        opacity: 1,
                        y: 0,
                        duration: 0.8,
                        ease: "power3.out",
                        stagger: 0.12,
                        scrollTrigger: {
                            trigger: contentRef.current,
                            start: "top 80%",
                            once: true,
                        },
                    }
                )
            }, sectionRef)

            const tl = revealAnimation(".about-reveal", {
                from: "right",
                duration: 1.1,
            })

            ScrollTrigger.create({
                trigger: ".about-reveal",
                start: "top 80%",
                once: true,
                animation: tl,
            })

            return () => ctx.revert()
        },
        { scope: sectionRef }
    )

    return (
        <section ref={sectionRef} className="py-12 sm:py-16">
            <div className="container">
                <div className="grid lg:grid-cols-2 gap-10 lg:gap-12 items-start">
                    <div className="flex flex-col sm:flex-row gap-4">
                        <div className="relative overflow-hidden rounded-xl about-reveal flex-1">
                            <img
                                className="hero-image h-[220px] sm:h-[320px] lg:h-[360px] w-full object-cover"
                                src={testImg}
                                alt="about image"
                            />
                        </div>
                        <div className="relative w-full sm:w-fit h-fit text-center flex justify-center sm:block">
                            <div className="relative">
                                <img
                                    className="w-[140px] h-[140px] sm:w-[150px] sm:h-[150px]"
                                    src={experience_img}
                                    alt="experience image"
                                />
                                <div className="absolute inset-0 flex flex-col items-center justify-center">
                                    <h2 className="text-3xl sm:text-4xl font-bold">١٠+</h2>
                                    <p className="text-lg sm:text-xl font-semibold">سنين خبره</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div ref={contentRef} className="space-y-5">
                        <div data-anim="about-text">
                            <CustomBadge title="عن قرم" />
                        </div>

                        <h6
                            data-anim="about-text"
                            className="text-xl sm:text-2xl text-gray-900"
                        >
                            مساحات عمل عصرية تناسب طموحك
                        </h6>

                        <hr data-anim="about-text" />

                        <p
                            data-anim="about-text"
                            className="text-gray-600 leading-7 text-sm sm:text-base"
                        >
                            نؤمن أن البيئة الصحيحة هي الأساس لكل إنجاز ناجح. <br />
                            لذلك حرصنا على تصميم مساحتنا بعناية فائقة، حيث النظافة، الترتيب،
                            والهدوء يجتمعون ليخلقوا بيئة عمل ملهمة تساعدك على تقديم أفضل ما لديك.
                        </p>

                        <div data-anim="about-text" className="pt-1">
                            <Link to="/about">
                                <Button
                                    size="lg"
                                    className="py-6 sm:py-7"
                                >
                                    اعرف المزيد عنا
                                    <span className="inline-flex h-8 w-8 items-center justify-center rounded-tr-md rounded-bl-md bg-white text-[#052125] group-hover:bg-lime-400 group-hover:text-white transition group-hover:-translate-x-0.5">
                                        <MoveUpLeft className="h-5 w-5" />
                                    </span>
                                </Button>
                            </Link>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    )
}

export default AboutSection
