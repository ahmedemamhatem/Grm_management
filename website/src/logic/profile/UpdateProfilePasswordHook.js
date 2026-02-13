
import { updateProfilePasswordAction } from "@/app/actions/profileActions";
import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { toast } from "sonner";

const UpdateProfilePasswordHook = () => {
    const dispatch = useDispatch();
    const { profilePasswordUpdate, isLoading, errors } = useSelector((state) => state.profile);

    const updateProfilePassFN = (payload) => {
        dispatch(updateProfilePasswordAction(payload));
    };

    useEffect(() => {
        if (errors && errors?.ar) {
            toast.error(errors?.ar);
        }
    }, [errors]);

    return {
        updateProfilePassFN,
        profilePasswordUpdate,
        isLoading,
        errors,
    };
};

export default UpdateProfilePasswordHook