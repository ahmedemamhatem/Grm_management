import { zodResolver } from "@hookform/resolvers/zod"
import { format } from "date-fns"
import { ChevronDownIcon, Loader2 } from "lucide-react"
import { useEffect, useState } from "react"
import { useForm } from "react-hook-form"

import { Button } from "@/components/ui/button"
import { Calendar } from "@/components/ui/calendar"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { TabsContent } from "../ui/tabs"

import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"

import { GetSpaceAvailabilityHook, GetSpaceTimeSlotHook, IsLoginInHook } from "@/logic"
import { checkAvailabilitySpaceSchema } from "@/validation"

import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import Cookies from "js-cookie"
import { useNavigate } from "react-router-dom"
import { toast } from "sonner"
import BookingDialog from "./BookingDialog"

const BookingForm = ({ spaceID }) => {
    const navigate = useNavigate();
    const [open, setOpen] = useState(false)
    const [bookingRequested, setBookingRequested] = useState(false)
    const [showAvailability, setShowAvailability] = useState(false)
    const [bookingDialogOpen, setBookingDialogOpen] = useState(false);
    const [selectedSlot, setSelectedSlot] = useState(null);
    const isSystemUser = Cookies.get("system_user") === "yes" ? true : false;

    const { spaceAvailability, isLoading, getSpaceAvailability, errors } = GetSpaceAvailabilityHook()
    const { errors: errorsTimeSlots, timeSlots, isLoading: isLoadingTimeSlots, getSpaceTimeSlot } = GetSpaceTimeSlotHook()

    const { isLoading: isLoadingIsLogin, checkLogin, isLogin } = IsLoginInHook()

    const form = useForm({
        resolver: zodResolver(checkAvailabilitySpaceSchema),
        defaultValues: {
            date: undefined,
            start_time: "10:30:00",
            end_time: "11:30:00",
        },
        mode: "onChange",
    })

    const onSubmit = async (values) => {
        const payload = {
            space: spaceID,
            booking_date: values.date ? format(values.date, "yyyy-MM-dd") : null,
            start_time: values.start_time.slice(0, 5),
            end_time: values.end_time.slice(0, 5),
        }

        try {
            getSpaceAvailability(payload)
            setShowAvailability(true)
        } catch (e) {
            console.error(e)
        }
    }

    const handleBooking = () => {
        setBookingRequested(true);
        checkLogin();
    };

    const handleDailyAvailability = () => {
        const payload = {
            space: spaceID,
            date: format(form.getValues("date"), "yyyy-MM-dd"),
            slot_duration_minutes: spaceAvailability?.duration_hours
        }
        getSpaceTimeSlot(payload)
    }

    useEffect(() => {
        if (!bookingRequested) return;
        if (isLoadingIsLogin) return;
        if (isSystemUser) {
            toast.warning("غير مصرح لك بحجز مساحات الا من داخل التطبيق");
            return;
        }

        if (isLogin) {
            setBookingDialogOpen(true);
        } else {
            navigate("/login");
        }

        setBookingRequested(false);
    }, [bookingRequested, isLoadingIsLogin, isLogin, navigate]);

    return (
        <TabsContent value="book" className="m-0">
            <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                    {/* Date */}
                    <FormField
                        control={form.control}
                        name="date"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel htmlFor="booking_date">التاريخ</FormLabel>

                                <Popover open={open} onOpenChange={setOpen}>
                                    <PopoverTrigger asChild>
                                        <FormControl>
                                            <Button
                                                type="button"
                                                variant="secondary"
                                                id="booking_date"
                                                disabled={isLoading}
                                                className="w-full justify-between"
                                            >
                                                {field.value ? format(field.value, "PPP") : "اختر التاريخ"}
                                                <ChevronDownIcon className="size-4 opacity-70" />
                                            </Button>
                                        </FormControl>
                                    </PopoverTrigger>

                                    <PopoverContent className="w-auto overflow-hidden p-0" align="start">
                                        <Calendar
                                            mode="single"
                                            selected={field.value}
                                            captionLayout="dropdown"
                                            defaultMonth={field.value}
                                            onSelect={(d) => {
                                                field.onChange(d)
                                                setOpen(false)
                                            }}
                                            disabled={isLoading}
                                        />
                                    </PopoverContent>
                                </Popover>

                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <div className="grid grid-cols-2 gap-2">
                        {/* End time */}
                        <FormField
                            control={form.control}
                            name="end_time"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel htmlFor="end_time">الى</FormLabel>
                                    <FormControl>
                                        <Input
                                            {...field}
                                            type="time"
                                            id="end_time"
                                            step="60"
                                            disabled={isLoading}
                                            className="bg-background appearance-none [&::-webkit-calendar-picker-indicator]:hidden [&::-webkit-calendar-picker-indicator]:appearance-none hover:border-emerald-600"
                                        />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        {/* Start time */}
                        <FormField
                            control={form.control}
                            name="start_time"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel htmlFor="start_time">من</FormLabel>
                                    <FormControl>
                                        <Input
                                            {...field}
                                            type="time"
                                            id="start_time"
                                            step="60"
                                            disabled={isLoading}
                                            className="bg-background appearance-none [&::-webkit-calendar-picker-indicator]:hidden [&::-webkit-calendar-picker-indicator]:appearance-none hover:border-emerald-600"
                                        />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                    </div>

                    <Button
                        type="submit"
                        className="w-full"
                        disabled={isLoading || !form.formState.isValid}
                    >
                        {isLoading ? (
                            <>
                                <Loader2 className="mr-2 size-4 animate-spin" />
                                جاري التحقق...
                            </>
                        ) : (
                            "تحقق"
                        )}
                    </Button>

                    {!errors && showAvailability && spaceAvailability && (
                        <>
                            <Button
                                type="button"
                                className="w-full"
                                variant="outline"
                                disabled={isLoadingTimeSlots}
                                onClick={handleDailyAvailability}
                            >
                                {isLoadingTimeSlots ? (
                                    <>
                                        <Loader2 className="mr-2 size-4 animate-spin" />
                                        جاري فحص التوفر اليومي...
                                    </>
                                ) : (
                                    "فحص التوفر اليومي"
                                )}
                            </Button>
                            <Card className="mt-4">
                                <CardHeader className="space-y-2">
                                    <div className="flex items-center justify-between">
                                        <CardTitle className="text-base">نتيجة التحقق</CardTitle>
                                        <Badge variant="secondary" className="px-2">
                                            {spaceAvailability.rate_type === "Hourly" ? "ساعة" :
                                                spaceAvailability.rate_type === "Daily" ? "يوم" :
                                                    spaceAvailability.rate_type === "Monthly" ? "شهر" : ""}
                                        </Badge>
                                    </div>

                                    <Separator />
                                </CardHeader>

                                <CardContent className="grid grid-cols-3 gap-2 text-center">
                                    <div className="rounded-md border p-3">
                                        <p className="text-xs text-muted-foreground">المدة</p>
                                        <p className="mt-1 font-semibold">
                                            {spaceAvailability.duration_hours} ساعات
                                        </p>
                                    </div>

                                    <div className="rounded-md border p-3">
                                        <p className="text-xs text-muted-foreground">السعر المتوقع</p>
                                        <p className="mt-1 font-semibold text-emerald-600">
                                            {spaceAvailability.estimated_price}
                                        </p>
                                    </div>

                                    <div className="rounded-md border p-3">
                                        <p className="text-xs text-muted-foreground">نوع التسعير</p>
                                        <p className="mt-1 font-semibold">
                                            {spaceAvailability.rate_type}
                                        </p>
                                    </div>
                                </CardContent>

                                <CardFooter>
                                    <Button
                                        type="button"
                                        className="w-full"
                                        disabled={isLoadingIsLogin}
                                        onClick={handleBooking}
                                    >
                                        {isLoadingIsLogin ? "جاري التحقق..." : "احجز الوقت المحدد"}
                                    </Button>
                                </CardFooter>
                            </Card>
                        </>
                    )}

                    {!errorsTimeSlots && showAvailability && timeSlots && timeSlots.length > 0 && (
                        <div className="mt-4 flex flex-wrap gap-2">
                            {timeSlots.map((slot, index) => {
                                const key = slot.id ?? `${slot.start_time}-${slot.end_time}-${index}`

                                const isSelected =
                                    selectedSlot?.id
                                        ? selectedSlot.id === slot.id
                                        : selectedSlot?.start_time === slot.start_time &&
                                        selectedSlot?.end_time === slot.end_time

                                return (
                                    <Button
                                        key={key}
                                        type="button"
                                        variant={isSelected ? "default" : "secondary"}
                                        className="rounded-full"
                                        onClick={() => setSelectedSlot(slot)}
                                    >
                                        {slot.start_time} - {slot.end_time}
                                    </Button>
                                )
                            })}
                            {selectedSlot && (
                                <Button
                                    type="button"
                                    className="w-full mt-4"
                                    disabled={isLoadingIsLogin}
                                    onClick={handleBooking}
                                >
                                    {isLoadingIsLogin ? "جاري الحجز..." : "احجز المده المحدد"}
                                </Button>
                            )}
                        </div>

                    )}
                </form>
            </Form>
            <BookingDialog
                open={bookingDialogOpen}
                onOpenChange={setBookingDialogOpen}
                space={spaceID}
                booking_date={form.getValues("date") ? format(form.getValues("date"), "yyyy-MM-dd") : null}
                start_time={selectedSlot ? selectedSlot.start_time : form.getValues("start_time") ? form.getValues("start_time").slice(0, 5) : null}
                end_time={selectedSlot ? selectedSlot.end_time : form.getValues("end_time") ? form.getValues("end_time").slice(0, 5) : null}
            />
        </TabsContent>
    )
}

export default BookingForm
