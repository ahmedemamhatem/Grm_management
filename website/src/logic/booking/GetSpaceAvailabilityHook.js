
import { checkAvailabilitySpaceAction } from "@/app/actions/bookingActions";
import { useCallback, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { toast } from "sonner";

const GetSpaceAvailabilityHook = () => {
    const dispatch = useDispatch();

    const getSpaceAvailability = useCallback((payload) => {
        dispatch(checkAvailabilitySpaceAction(payload));
    }, [dispatch]);

    const { isLoading, spaceAvailability, errors } = useSelector(
        (state) => state.booking
    );

    useEffect(() => {
        const message = errors?.message?.ar;

        if (errors && message) {
            toast.error(message);
        }
    }, [errors]);

    return { isLoading, spaceAvailability, errors, getSpaceAvailability };
};

export default GetSpaceAvailabilityHook;