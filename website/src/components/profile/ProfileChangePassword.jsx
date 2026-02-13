import { zodResolver } from "@hookform/resolvers/zod"
import { gsap } from "gsap"
import { Lock } from "lucide-react"
import { useEffect, useRef, useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Separator } from "@/components/ui/separator"
import { UpdateProfilePasswordHook } from "@/logic"
import { ChangePasswordSchema } from "@/validation"
import { toast } from "sonner"



const ProfileChangePassword = () => {
    const { updateProfilePassFN, isLoading, profilePasswordUpdate } = UpdateProfilePasswordHook()

    const [isOpen, setIsOpen] = useState(false)
    const formRef = useRef(null)

    const form = useForm({
        resolver: zodResolver(ChangePasswordSchema),
        defaultValues: {
            current_password: "",
            new_password: "",
            confirm_password: "",
        },
    })

    const openForm = () => {
        setIsOpen(true)

        gsap.fromTo(
            formRef.current,
            { height: 0, opacity: 0 },
            {
                height: "auto",
                opacity: 1,
                duration: 0.4,
                ease: "power2.out",
            }
        )
    }

    const closeForm = () => {
        gsap.to(formRef.current, {
            height: 0,
            opacity: 0,
            duration: 0.3,
            ease: "power2.in",
            onComplete: () => {
                setIsOpen(false)
                form.reset()
            },
        })
    }

    const onSubmit = async (values) => {
        updateProfilePassFN(values)
    }

    useEffect(() => {
        if (!isLoading && Object.keys(profilePasswordUpdate).length > 0) {
            toast.success("تم تغيير كلمة المرور بنجاح")
            closeForm()
        }
    }, [profilePasswordUpdate, isLoading])

    return (
        <Card className="rounded-2xl shadow-sm">
            <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="flex items-center gap-2 text-lg">
                    <Lock className="h-5 w-5" />
                    تغيير كلمة المرور
                </CardTitle>

                {!isOpen && (
                    <Button variant="outline" onClick={openForm}>
                        تعديل
                    </Button>
                )}
            </CardHeader>

            <CardContent className="pt-0">
                <div ref={formRef} style={{ height: 0, overflow: "hidden" }}>
                    <div className="pt-4">
                        <Separator className="mb-4" />

                        <Form {...form}>
                            <form
                                onSubmit={form.handleSubmit(onSubmit)}
                                className="space-y-4"
                            >
                                <FormField
                                    control={form.control}
                                    name="current_password"
                                    render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>كلمة المرور الحالية</FormLabel>
                                            <FormControl>
                                                <Input
                                                    type="password"
                                                    disabled={isLoading}
                                                    {...field}
                                                />
                                            </FormControl>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />

                                <FormField
                                    control={form.control}
                                    name="new_password"
                                    render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>كلمة المرور الجديدة</FormLabel>
                                            <FormControl>
                                                <Input
                                                    type="password"
                                                    disabled={isLoading}
                                                    {...field}
                                                />
                                            </FormControl>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />

                                <FormField
                                    control={form.control}
                                    name="confirm_password"
                                    render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>تأكيد كلمة المرور</FormLabel>
                                            <FormControl>
                                                <Input
                                                    type="password"
                                                    disabled={isLoading}
                                                    {...field}
                                                />
                                            </FormControl>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />

                                <div className="flex justify-end gap-2 pt-2">
                                    <Button
                                        type="button"
                                        variant="outline"
                                        onClick={closeForm}
                                        disabled={isLoading}
                                    >
                                        إلغاء
                                    </Button>

                                    <Button type="submit" disabled={isLoading}>
                                        {isLoading ? "جارٍ الحفظ..." : "حفظ"}
                                    </Button>
                                </div>
                            </form>
                        </Form>
                    </div>
                </div>
            </CardContent>
        </Card>
    )
}

export default ProfileChangePassword
