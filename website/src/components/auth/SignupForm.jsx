import { Button } from "@/components/ui/button";
import { Field, FieldGroup, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import SignUpHook from "@/logic/auth/SignUpHook";
import { signupSchema } from "@/validation";
import { useGSAP } from "@gsap/react";
import { zodResolver } from "@hookform/resolvers/zod";
import { gsap } from "gsap";
import { Eye, EyeOff } from "lucide-react";
import { useMemo, useRef, useState } from "react";
import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "sonner";

export function SignupForm() {
    const formRef = useRef(null);
    const navigate = useNavigate();
    const { signUpSubmit } = SignUpHook();
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);

    const {
        register,
        handleSubmit,
        formState: { errors, isSubmitting, isValid, submitCount },
        setFocus,
        watch,
        setValue,
    } = useForm({
        resolver: zodResolver(signupSchema),
        mode: "onSubmit",
        defaultValues: {
            first_name: "",
            last_name: "",
            email: "",
            password: "",
            phone: "",
            confirm_password: "",
            tenant_type: "Individual",
            company_name: "",
            commercial_registration: "",
            tax_id: "",
        },
    });

    const tenantType = watch("tenant_type");

    const itemSelectors = useMemo(
        () => [
            "[data-anim='title']",
            "[data-anim='tenant_type']",
            "[data-anim='first_name']",
            "[data-anim='last_name']",
            "[data-anim='email']",
            "[data-anim='phone']",
            "[data-anim='password']",
            "[data-anim='confirm_password']",
            "[data-anim='company_fields']",
            "[data-anim='btn']",
        ],
        []
    );

    useGSAP(() => {
        if (!formRef.current) return;

        const ctx = gsap.context(() => {
            gsap.fromTo(
                formRef.current,
                { opacity: 0, y: 14, filter: "blur(6px)" },
                { opacity: 1, y: 0, filter: "blur(0px)", duration: 0.6, ease: "power3.out" }
            );

            gsap.fromTo(
                itemSelectors
                    .map((s) => formRef.current.querySelector(s))
                    .filter(Boolean),
                { opacity: 0, y: 10 },
                { opacity: 1, y: 0, duration: 0.5, stagger: 0.08, ease: "power2.out", delay: 0.05 }
            );
        }, formRef);

        return () => ctx.revert();
    }, [itemSelectors]);

    const shake = () => {
        if (!formRef.current) return;
        gsap.fromTo(formRef.current, { x: 0 }, { x: -8, duration: 0.06, yoyo: true, repeat: 5, ease: "power1.inOut" });
    };

    const submitForm = async (values) => {
        try {
            const payload =
                values.tenant_type === "Company"
                    ? {
                        first_name: values.first_name,
                        last_name: values.last_name,
                        email: values.email,
                        password: values.password,
                        phone: values.phone,
                        tenant_type: "Company",
                        company_name: values.company_name,
                        commercial_registration: values.commercial_registration,
                        tax_id: values.tax_id,
                    }
                    : {
                        first_name: values.first_name,
                        last_name: values.last_name,
                        email: values.email,
                        password: values.password,
                        phone: values.phone,
                        tenant_type: "Individual",
                    };

            await signUpSubmit(payload);

            toast.success("تم تسجيل الحساب بنجاح");
            setTimeout(() => navigate("/login"), 1000);
        } catch (e) {
            console.log(e)
        }
    };

    const onInvalid = () => {
        shake();
        if (errors.tenant_type) setFocus("tenant_type");
        else if (errors.first_name) setFocus("first_name");
        else if (errors.last_name) setFocus("last_name");
        else if (errors.email) setFocus("email");
        else if (errors.phone) setFocus("phone");
        else if (errors.password) setFocus("password");
        else if (errors.confirm_password) setFocus("confirm_password");
        else if (tenantType === "Company") {
            if (errors.company_name) setFocus("company_name");
            else if (errors.commercial_registration) setFocus("commercial_registration");
            else if (errors.tax_id) setFocus("tax_id");
        }
    };

    return (
        <form
            ref={formRef}
            className="flex flex-col gap-6"
            onSubmit={handleSubmit(submitForm, onInvalid)}
            noValidate
        >
            <FieldGroup>
                <div className="flex flex-col items-center gap-1 text-center" data-anim="title">
                    <h1 className="text-2xl font-bold">سجّل حساب جديد</h1>
                    <p className="text-muted-foreground text-sm text-balance">
                        اكتب بياناتك بالأسفل لإنشاء حساب جديد والبدء في استخدام المنصة
                    </p>
                </div>

                {/* tenant_type */}
                <Field data-anim="tenant_type">
                    <FieldLabel>نوع الحساب</FieldLabel>
                    <Select
                        value={tenantType}
                        onValueChange={(v) => {
                            setValue("tenant_type", v, { shouldValidate: true });
                            if (v === "Individual") {
                                setValue("company_name", "");
                                setValue("commercial_registration", "");
                                setValue("tax_id", "");
                            }
                        }}
                    >
                        <SelectTrigger aria-invalid={!!errors.tenant_type}>
                            <SelectValue placeholder="اختر نوع الحساب" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="Individual">فرد</SelectItem>
                            <SelectItem value="Company">شركة</SelectItem>
                        </SelectContent>
                    </Select>
                    {errors.tenant_type && <p className="text-sm text-destructive mt-1">{String(errors.tenant_type.message)}</p>}
                </Field>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-1">
                    <Field data-anim="first_name">
                        <FieldLabel htmlFor="first_name">الاسم الأول</FieldLabel>
                        <Input
                            id="first_name"
                            type="text"
                            autoComplete="given-name"
                            aria-invalid={!!errors.first_name}
                            className={errors.first_name ? "border-destructive focus-visible:ring-destructive" : ""}
                            {...register("first_name")}
                        />
                        {errors.first_name && <p className="text-sm text-destructive mt-1">{errors.first_name.message}</p>}
                    </Field>

                    <Field data-anim="last_name">
                        <FieldLabel htmlFor="last_name">اسم العائلة</FieldLabel>
                        <Input
                            id="last_name"
                            type="text"
                            autoComplete="family-name"
                            aria-invalid={!!errors.last_name}
                            className={errors.last_name ? "border-destructive focus-visible:ring-destructive" : ""}
                            {...register("last_name")}
                        />
                        {/* ✅ إصلاح الغلط هنا */}
                        {errors.last_name && <p className="text-sm text-destructive mt-1">{errors.last_name.message}</p>}
                    </Field>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-1">
                    <Field data-anim="email">
                        <FieldLabel htmlFor="email">الإيميل</FieldLabel>
                        <Input
                            id="email"
                            type="email"
                            placeholder="m@example.com"
                            autoComplete="email"
                            aria-invalid={!!errors.email}
                            className={errors.email ? "border-destructive focus-visible:ring-destructive" : ""}
                            {...register("email")}
                        />
                        {errors.email && <p className="text-sm text-destructive mt-1">{errors.email.message}</p>}
                    </Field>

                    <Field data-anim="phone">
                        <FieldLabel htmlFor="phone">رقم الهاتف</FieldLabel>
                        <Input
                            id="phone"
                            type="text"
                            placeholder="+9665xxxxxxxx"
                            autoComplete="tel"
                            aria-invalid={!!errors.phone}
                            className={errors.phone ? "border-destructive focus-visible:ring-destructive" : ""}
                            {...register("phone")}
                        />
                        {errors.phone && <p className="text-sm text-destructive mt-1">{errors.phone.message}</p>}
                    </Field>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-1">
                    <Field data-anim="password">
                        <FieldLabel htmlFor="password">كلمة المرور</FieldLabel>

                        <div className="relative">
                            <Input
                                id="password"
                                type={showPassword ? "text" : "password"}
                                autoComplete="new-password"
                                aria-invalid={!!errors.password}
                                className={`pr-10 ${errors.password ? "border-destructive focus-visible:ring-destructive" : ""}`}
                                {...register("password")}
                            />

                            <button
                                type="button"
                                onClick={() => setShowPassword((p) => !p)}
                                className="absolute inset-y-0 end-2 flex items-center text-muted-foreground hover:text-foreground"
                                tabIndex={-1}
                            >
                                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                            </button>
                        </div>

                        {errors.password && (
                            <p className="text-sm text-destructive mt-1">{errors.password.message}</p>
                        )}
                    </Field>

                    <Field data-anim="confirm_password">
                        <FieldLabel htmlFor="confirm_password">تأكيد كلمة المرور</FieldLabel>

                        <div className="relative">
                            <Input
                                id="confirm_password"
                                type={showConfirmPassword ? "text" : "password"}
                                autoComplete="new-password"
                                aria-invalid={!!errors.confirm_password}
                                className={`pr-10 ${errors.confirm_password ? "border-destructive focus-visible:ring-destructive" : ""}`}
                                {...register("confirm_password")}
                            />

                            <button
                                type="button"
                                onClick={() => setShowConfirmPassword((p) => !p)}
                                className="absolute inset-y-0 end-2 flex items-center text-muted-foreground hover:text-foreground"
                                tabIndex={-1}
                            >
                                {showConfirmPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                            </button>
                        </div>

                        {errors.confirm_password && (
                            <p className="text-sm text-destructive mt-1">
                                {errors.confirm_password.message}
                            </p>
                        )}
                    </Field>

                </div>

                {/* Company-only fields */}
                {tenantType === "Company" && (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-1" data-anim="company_fields">
                        <Field>
                            <FieldLabel htmlFor="company_name">اسم الشركة</FieldLabel>
                            <Input
                                id="company_name"
                                type="text"
                                aria-invalid={!!errors.company_name}
                                className={errors.company_name ? "border-destructive focus-visible:ring-destructive" : ""}
                                {...register("company_name")}
                            />
                            {errors.company_name && <p className="text-sm text-destructive mt-1">{String(errors.company_name.message)}</p>}
                        </Field>

                        <Field>
                            <FieldLabel htmlFor="commercial_registration">السجل التجاري</FieldLabel>
                            <Input
                                id="commercial_registration"
                                type="text"
                                aria-invalid={!!errors.commercial_registration}
                                className={errors.commercial_registration ? "border-destructive focus-visible:ring-destructive" : ""}
                                {...register("commercial_registration")}
                            />
                            {errors.commercial_registration && (
                                <p className="text-sm text-destructive mt-1">{String(errors.commercial_registration.message)}</p>
                            )}
                        </Field>

                        <Field className="sm:col-span-2">
                            <FieldLabel htmlFor="tax_id">الرقم الضريبي</FieldLabel>
                            <Input
                                id="tax_id"
                                type="text"
                                aria-invalid={!!errors.tax_id}
                                className={errors.tax_id ? "border-destructive focus-visible:ring-destructive" : ""}
                                {...register("tax_id")}
                            />
                            {errors.tax_id && <p className="text-sm text-destructive mt-1">{String(errors.tax_id.message)}</p>}
                        </Field>
                    </div>
                )}

                <div className="flex justify-between items-center">
                    <Link
                        to="/login"
                        className="text-sm underline-offset-4 transition-colors duration-300 hover:underline text-gray-400"
                    >
                        هل لديك حساب؟ سجل الدخول
                    </Link>
                </div>

                <Field data-anim="btn">
                    <Button type="submit" disabled={isSubmitting || (submitCount > 0 && !isValid)}>
                        {isSubmitting ? "جاري تسجيل الحساب..." : "تسجيل الحساب"}
                    </Button>
                </Field>
            </FieldGroup>
        </form>
    );
}