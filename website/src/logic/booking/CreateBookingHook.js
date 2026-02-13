
import { createBookingAction } from "@/app/actions/bookingActions";
import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { toast } from "sonner";

const CreateBookingHook = () => {
    const dispatch = useDispatch();
    const { bookingInfo, isLoading, errors } = useSelector((state) => state.booking);

    const createBooking = (payload) => {
        dispatch(createBookingAction(payload));
    };

    useEffect(() => {
        const message = errors?.message;
        if (errors && message) {
            toast.error(message?.ar);
        }
    }, [errors]);

    return {
        createBooking,
        bookingInfo,
        isLoading,
        errors,
    };
};

export default CreateBookingHook;