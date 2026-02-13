
import { getAllPackagesAction } from "@/app/actions/packagesActions";
import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";

const GetAllPackagesHook = () => {
    const dispatch = useDispatch();

    useEffect(() => {
        dispatch(getAllPackagesAction());
    }, []);

    const { isLoading, packages, space_count, space_types, errors } = useSelector(
        (state) => state.packages
    );

    return { isLoading, packages, space_count, space_types, errors };
};

export default GetAllPackagesHook;
