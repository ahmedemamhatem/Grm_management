import testIMG from "@/assets/images/test/hero-test.jpg"
import { useGSAP } from "@gsap/react"
import { gsap } from "gsap"
import { useRef } from "react"
import { LoginForm } from "./LoginForm"

export default function LoginSection() {
    const imageWrapperRef = useRef(null)
    const imageRef = useRef(null)

    useGSAP(() => {
        if (!imageWrapperRef.current || !imageRef.current) return

        const ctx = gsap.context(() => {
            gsap.fromTo(
                imageRef.current,
                {
                    opacity: 0,
                    scale: 1.08,
                    filter: "blur(8px)",
                },
                {
                    opacity: 1,
                    scale: 1,
                    filter: "blur(0px)",
                    duration: 1.2,
                    ease: "power3.out",
                    delay: 0.2,
                }
            )
        }, imageWrapperRef)

        return () => ctx.revert()
    }, [])

    return (
        <section className="grid min-h-svh lg:grid-cols-2">
            <div className="flex flex-col gap-4 p-6 md:p-10">
                <div className="flex flex-1 items-center justify-center">
                    <div className="w-full max-w-sm">
                        <LoginForm />
                    </div>
                </div>
            </div>

            <div
                ref={imageWrapperRef}
                className="bg-muted relative hidden overflow-hidden lg:block"
            >
                <img
                    ref={imageRef}
                    src={testIMG}
                    alt="login image"
                    className="absolute inset-0 h-full w-full object-cover dark:brightness-[0.2] dark:grayscale will-change-transform"
                />
            </div>
        </section>
    )
}
