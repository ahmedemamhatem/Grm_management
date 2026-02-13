import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";

import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogContent,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { CreateBookingHook } from "@/logic";
import { BookingSchema } from "@/validation";
import { toast } from "sonner";


function BookingDialog({ open, onOpenChange, space, booking_date, start_time, end_time }) {
    const { createBooking, isLoading } = CreateBookingHook();
    const form = useForm({
        resolver: zodResolver(BookingSchema),
        defaultValues: {
            attendees: "",
            purpose: "",
            notes: "",
        },
        mode: "onChange",
    });

    async function onSubmit(values) {
        const payload = {
            attendees: values.attendees,
            purpose: values.purpose,
            notes: values.notes ?? "",
            space,
            booking_date,
            start_time,
            end_time,
            booking_type: "Hourly",
        };

        try {
            createBooking(payload);
            toast.success("تم حجز المساحه بنجاح");
            onOpenChange(false);
        } catch (error) {
            toast.error(error);
        }
    }


    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[520px]">
                <DialogHeader>
                    <DialogTitle>احجز مساحه</DialogTitle>
                </DialogHeader>

                <Form {...form}>
                    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                        {/* attendees */}
                        <FormField
                            control={form.control}
                            name="attendees"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>عدد الحضور</FormLabel>
                                    <FormControl>
                                        <Input
                                            type="number"
                                            inputMode="numeric"
                                            min={1}
                                            value={field.value ?? 0}
                                            onChange={(e) => field.onChange(Number(e.target.value))}
                                            placeholder="مثال: 4"
                                        />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        {/* purpose */}
                        <FormField
                            control={form.control}
                            name="purpose"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>الغرض من الاجتماع</FormLabel>
                                    <FormControl>
                                        <Input placeholder="مثال: اجتماع فريق العمل" {...field} />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        {/* notes */}
                        <FormField
                            control={form.control}
                            name="notes"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>ملاحظات</FormLabel>
                                    <FormControl>
                                        <Textarea
                                            placeholder="مثال: يرجى تجهيز جهاز عرض"
                                            className="min-h-[90px]"
                                            {...field}
                                        />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <DialogFooter className="gap-2">
                            <Button
                                type="button"
                                variant="outline"
                                onClick={() => {
                                    onOpenChange(false);
                                    form.reset(defaultValues);
                                }}
                            >
                                الغاء
                            </Button>

                            <Button type="submit" disabled={!form.formState.isValid || isLoading}>
                                {isLoading ? "جاري الحفظ..." : "حفظ"}
                            </Button>
                        </DialogFooter>
                    </form>
                </Form>
            </DialogContent>
        </Dialog>
    );
}


export default BookingDialog;