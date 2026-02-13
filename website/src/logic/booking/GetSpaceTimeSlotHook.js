
import { getAvailabilityTimeSlotsSpaceAction } from "@/app/actions/bookingActions";
import { useCallback, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { toast } from "sonner";

const GetSpaceTimeSlotHook = () => {
    const dispatch = useDispatch();

    const getSpaceTimeSlot = useCallback((payload) => {
        dispatch(getAvailabilityTimeSlotsSpaceAction(payload));
    }, [dispatch]);

    const { isLoading, timeSlots, errors } = useSelector(
        (state) => state.booking
    );

    useEffect(() => {
        const message = errors?.message;
        if (errors && message) {
            toast.error(message?.ar);
        }
    }, [errors]);

    return { isLoading, timeSlots, errors, getSpaceTimeSlot };
};

export default GetSpaceTimeSlotHook;