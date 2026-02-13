import { getProfileAction } from "@/app/actions/profileActions";
import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { toast } from "sonner";


const GetProfileHook = () => {
    const dispatch = useDispatch();

    useEffect(() => {
        dispatch(getProfileAction());
    }, []);

    const { isLoading, profile, errors } = useSelector(
        (state) => state.profile
    );

    useEffect(() => {
        const message = errors?.message;
        if (message) {
            toast.error(message);
        }
    }, [errors]);

    return { isLoading, profile, errors };
};

export default GetProfileHook;
