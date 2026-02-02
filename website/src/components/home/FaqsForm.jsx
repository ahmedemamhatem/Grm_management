import { Button } from "@/components/ui/button";
import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { Field, FieldError, FieldGroup } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { zodResolver } from "@hookform/resolvers/zod";
import { Controller, useForm } from "react-hook-form";
import { toast } from "sonner";
import * as z from "zod";
import {
    InputGroup,
    InputGroupAddon,
    InputGroupText,
    InputGroupTextarea,
} from "../ui/input-group";

import { useGSAP } from "@gsap/react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useRef } from "react";

gsap.registerPlugin(ScrollTrigger);

const faqsFormSchema = z.object({
    name: z.string().min(5, "الاسم يجب أن يكون 5 أحرف على الأقل.").max(32, "الاسم يجب ألا يزيد عن 32 حرفًا."),
    email: z.string().min(5, "البريد الإلكتروني غير صحيح.").max(100, "البريد الإلكتروني طويل جدًا."),
    phone: z.string().min(8, "رقم الهاتف قصير جدًا.").max(20, "رقم الهاتف طويل جدًا."),
    message: z.string().min(20, "الرسالة يجب أن تكون 20 حرفًا على الأقل.").max(100, "الرسالة يجب ألا تزيد عن 100 حرف."),
});

const FaqsForm = () => {
    const rootRef = useRef(null);

    const form = useForm({
        resolver: zodResolver(faqsFormSchema),
        mode: "onSubmit",
        defaultValues: {
            name: "",
            email: "",
            phone: "",
            message: "",
        },
    });

    function onSubmit(data) {
        toast("تم إرسال البيانات بنجاح", {
            description: (
                <pre className="bg-code text-code-foreground mt-2 w-[320px] overflow-x-auto rounded-md p-4">
                    <code>{JSON.stringify(data, null, 2)}</code>
                </pre>
            ),
            position: "bottom-right",
            classNames: { content: "flex flex-col gap-2" },
            style: { "--border-radius": "calc(var(--radius)  + 4px)" },
        });
    }

    useGSAP(
        () => {
            const root = rootRef.current;
            if (!root) return;

            const ctx = gsap.context(() => {
                const card = root.querySelector("[data-form-card]");
                const header = root.querySelectorAll("[data-form-head]");
                const fields = root.querySelectorAll("[data-form-field]");
                const btn = root.querySelector("[data-form-btn]");

                // initial
                if (card) gsap.set(card, { opacity: 0, y: 26, scale: 0.98 });
                gsap.set(header, { opacity: 0, y: 14 });
                gsap.set(fields, { opacity: 0, y: 14 });
                if (btn) gsap.set(btn, { opacity: 0, y: 14 });

                const tl = gsap.timeline({
                    scrollTrigger: {
                        trigger: root,
                        start: "top 80%",
                        once: true,
                    },
                });

                if (card) {
                    tl.to(card, {
                        opacity: 1,
                        y: 0,
                        scale: 1,
                        duration: 0.9,
                        ease: "power3.out",
                    });
                }

                tl.to(
                    header,
                    {
                        opacity: 1,
                        y: 0,
                        duration: 0.6,
                        ease: "power3.out",
                        stagger: 0.12,
                    },
                    0.15
                ).to(
                    fields,
                    {
                        opacity: 1,
                        y: 0,
                        duration: 0.6,
                        ease: "power3.out",
                        stagger: 0.08,
                    },
                    0.25
                );

                if (btn) {
                    tl.to(
                        btn,
                        {
                            opacity: 1,
                            y: 0,
                            duration: 0.6,
                            ease: "power3.out",
                        },
                        0.35
                    );
                }
            }, rootRef);

            return () => ctx.revert();
        },
        { scope: rootRef }
    );

    return (
        <div ref={rootRef}>
            <Card data-form-card className="w-full bg-[#052125] rounded-xl text-white p-10">
                <CardHeader>
                    <CardTitle data-form-head className="text-xl sm:text-2xl">
                        نساعدك في إتمام عملية الحجز بكل سهولة
                    </CardTitle>
                    <CardDescription data-form-head className="leading-7 text-sm sm:text-base text-inherit">
                        لنتعاون معًا ونحوّل الأفكار إلى إنجازات مبهرة
                    </CardDescription>
                </CardHeader>

                <CardContent>
                    <form id="form-rhf-demo" onSubmit={form.handleSubmit(onSubmit)}>
                        <FieldGroup>
                            <div data-form-field>
                                <Controller
                                    name="name"
                                    control={form.control}
                                    render={({ field, fieldState }) => (
                                        <Field data-invalid={fieldState.invalid}>
                                            <Input
                                                {...field}
                                                id="form-rhf-demo-title"
                                                aria-invalid={fieldState.invalid}
                                                placeholder="الاسم"
                                                autoComplete="off"
                                                className="border-0 border-b-2 border-white rounded-none placeholder:text-white"
                                            />
                                            {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
                                        </Field>
                                    )}
                                />
                            </div>

                            <div className="grid md:grid-cols-2 gap-2" data-form-field>
                                <Controller
                                    name="phone"
                                    control={form.control}
                                    render={({ field, fieldState }) => (
                                        <Field data-invalid={fieldState.invalid}>
                                            <Input
                                                {...field}
                                                id="form-rhf-demo-phone"
                                                aria-invalid={fieldState.invalid}
                                                placeholder="رقم الهاتف"
                                                autoComplete="off"
                                                className="border-0 border-b-2 border-white rounded-none placeholder:text-white"
                                            />
                                            {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
                                        </Field>
                                    )}
                                />

                                <Controller
                                    name="email"
                                    control={form.control}
                                    render={({ field, fieldState }) => (
                                        <Field data-invalid={fieldState.invalid}>
                                            <Input
                                                {...field}
                                                id="form-rhf-demo-email"
                                                type="email"
                                                aria-invalid={fieldState.invalid}
                                                placeholder="البريد الإلكتروني"
                                                autoComplete="off"
                                                className="border-0 border-b-2 border-white rounded-none placeholder:text-white"
                                            />
                                            {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
                                        </Field>
                                    )}
                                />
                            </div>

                            <div data-form-field>
                                <Controller
                                    name="message"
                                    control={form.control}
                                    render={({ field, fieldState }) => (
                                        <Field data-invalid={fieldState.invalid}>
                                            <InputGroup className="border-0 border-b-2 border-white rounded-none">
                                                <InputGroupTextarea
                                                    {...field}
                                                    id="form-rhf-demo-message"
                                                    placeholder="الرسالة"
                                                    rows={6}
                                                    className="min-h-24 resize-none placeholder:text-white"
                                                    aria-invalid={fieldState.invalid}
                                                />
                                                <InputGroupAddon align="block-end">
                                                    <InputGroupText className="tabular-nums">
                                                        {field.value.length}/100 حرف
                                                    </InputGroupText>
                                                </InputGroupAddon>
                                            </InputGroup>

                                            {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
                                        </Field>
                                    )}
                                />
                            </div>
                        </FieldGroup>
                    </form>
                </CardContent>

                <CardFooter>
                    <Button
                        data-form-btn
                        type="submit"
                        className="w-full py-6 font-bold"
                        form="form-rhf-demo"
                    >
                        إرسال الطلب
                    </Button>
                </CardFooter>
            </Card>
        </div>
    );
};

export default FaqsForm;
