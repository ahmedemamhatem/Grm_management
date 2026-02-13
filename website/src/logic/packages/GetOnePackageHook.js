
import { getOnePackageAction } from "@/app/actions/packagesActions";
import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { toast } from "sonner";


const GetOnePackageHook = (id) => {
    const dispatch = useDispatch();

    useEffect(() => {
        dispatch(getOnePackageAction(id));
    }, [id]);

    const { isLoading, onePackage, errors } = useSelector(
        (state) => state.packages
    );

    useEffect(() => {
        const message = errors?.message;
        if (message) {
            toast.error(message);
        }
    }, [errors]);

    return { isLoading, onePackage, errors };
};

export default GetOnePackageHook;
