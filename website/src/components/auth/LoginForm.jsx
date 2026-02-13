import { Button } from "@/components/ui/button"
import { Field, FieldGroup, FieldLabel } from "@/components/ui/field"
import { Input } from "@/components/ui/input"
import LoginHook from "@/logic/auth/LoginHook"
import { loginSchema } from "@/validation"
import { useGSAP } from "@gsap/react"
import { zodResolver } from "@hookform/resolvers/zod"
import { gsap } from "gsap"
import { useMemo, useRef } from "react"
import { useForm } from "react-hook-form"
import { Link } from "react-router-dom"
import { toast } from "sonner"


export function LoginForm() {
    const formRef = useRef(null);
    const { loginSubmit } = LoginHook();

    const {
        register,
        handleSubmit,
        formState: { errors, isSubmitting, isValid, submitCount },
        setFocus,
    } = useForm({
        resolver: zodResolver(loginSchema),
        mode: "onSubmit",
        defaultValues: { username: "", password: "" },
    })

    const itemSelectors = useMemo(() => ["[data-anim='title']", "[data-anim='username']", "[data-anim='password']", "[data-anim='btn']"], [])

    useGSAP(() => {
        if (!formRef.current) return

        const ctx = gsap.context(() => {
            gsap.fromTo(
                formRef.current,
                { opacity: 0, y: 14, filter: "blur(6px)" },
                { opacity: 1, y: 0, filter: "blur(0px)", duration: 0.6, ease: "power3.out" }
            )

            gsap.fromTo(
                itemSelectors.map((s) => formRef.current.querySelector(s)).filter(Boolean),
                { opacity: 0, y: 10 },
                { opacity: 1, y: 0, duration: 0.5, stagger: 0.08, ease: "power2.out", delay: 0.05 }
            )
        }, formRef)

        return () => ctx.revert()
    }, [itemSelectors])

    const shake = () => {
        if (!formRef.current) return
        gsap.fromTo(
            formRef.current,
            { x: 0 },
            { x: -8, duration: 0.06, yoyo: true, repeat: 5, ease: "power1.inOut" }
        )
    }

    const onSubmit = async ({ username, password }) => {
        await loginSubmit({ usr: username, pwd: password })
        toast.success("تم تسجيل الدخول بنجاح")
    }

    const onInvalid = () => {
        shake()
        if (errors.username) setFocus("username")
        else if (errors.password) setFocus("password")
    }

    return (
        <form
            ref={formRef}
            className="flex flex-col gap-6"
            onSubmit={handleSubmit(onSubmit, onInvalid)}
            noValidate
        >
            <FieldGroup>
                <div className="flex flex-col items-center gap-1 text-center" data-anim="title">
                    <h1 className="text-2xl font-bold">سجّل الدخول إلى حسابك</h1>
                    <p className="text-muted-foreground text-sm text-balance">
                        اكتب بريدك الإلكتروني بالأسفل لتسجيل الدخول إلى حسابك
                    </p>
                </div>

                <Field data-anim="username">
                    <FieldLabel htmlFor="username">اسم المستخدم</FieldLabel>
                    <Input
                        id="username"
                        type="text"
                        placeholder="اسم المستخدم"
                        autoComplete="username"
                        aria-invalid={!!errors.username}
                        className={errors.username ? "border-destructive focus-visible:ring-destructive" : ""}
                        {...register("username")}
                    />
                    {errors.username && (
                        <p className="text-sm text-destructive mt-1">{errors.username.message}</p>
                    )}
                </Field>

                <Field data-anim="password">
                    <FieldLabel htmlFor="password">كلمة المرور</FieldLabel>
                    <Input
                        id="password"
                        type="password"
                        autoComplete="current-password"
                        aria-invalid={!!errors.password}
                        className={errors.password ? "border-destructive focus-visible:ring-destructive" : ""}
                        {...register("password")}
                    />
                    {errors.password && (
                        <p className="text-sm text-destructive mt-1">{errors.password.message}</p>
                    )}
                    <div className="flex justify-between items-center">
                        {/* <Link
                            to="/forget-password"
                            className="text-sm underline-offset-4 transition-colors duration-300 hover:underline text-gray-400"
                        >
                            هل نسيت كلمة المرور؟
                        </Link> */}
                        <Link
                            to="/sign-up"
                            className="text-sm underline-offset-4 transition-colors duration-300 hover:underline text-gray-400"
                        >
                            هل لديك حساب؟ سجل حساب جديد
                        </Link>
                    </div>
                </Field>

                <Field data-anim="btn">
                    <Button type="submit" disabled={isSubmitting || (submitCount > 0 && !isValid)}>
                        {isSubmitting ? "جاري تسجيل الدخول..." : "تسجيل الدخول"}
                    </Button>
                </Field>
            </FieldGroup>
        </form>
    )
}
