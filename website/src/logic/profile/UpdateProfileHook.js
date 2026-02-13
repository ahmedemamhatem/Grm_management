
import { updateProfileAction } from "@/app/actions/profileActions";
import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { toast } from "sonner";

const UpdateProfileHook = () => {
    const dispatch = useDispatch();
    const { profileUpdate, isLoading, errors } = useSelector((state) => state.profile);

    const updateProfileFN = (payload) => {
        dispatch(updateProfileAction(payload));
    };

    useEffect(() => {
        const message = errors?.message;
        if (errors && message) {
            toast.error(message?.ar);
        }
    }, [errors]);

    return {
        updateProfileFN,
        profileUpdate,
        isLoading,
        errors,
    };
};

export default UpdateProfileHook