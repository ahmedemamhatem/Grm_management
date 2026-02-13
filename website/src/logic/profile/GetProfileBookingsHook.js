import { getProfileBookingsAction } from "@/app/actions/profileActions";
import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { toast } from "sonner";


const GetProfileBookingsHook = () => {
    const dispatch = useDispatch();

    useEffect(() => {
        dispatch(getProfileBookingsAction());
    }, []);

    const { isLoading, bookings, errors } = useSelector(
        (state) => state.profile
    );

    useEffect(() => {
        const message = errors?.message;
        if (message) {
            toast.error(message);
        }
    }, [errors]);

    return { isLoading, bookings, errors };
};

export default GetProfileBookingsHook;
