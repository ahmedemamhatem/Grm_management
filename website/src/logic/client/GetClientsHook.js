import { getClientAction } from "@/app/actions/clientActions";
import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";

const GetClientsHook = () => {
    const dispatch = useDispatch();

    useEffect(() => {
        dispatch(getClientAction());
    }, []);

    const { isLoading, clients, errors } = useSelector(
        (state) => state.client
    );

    return { isLoading, clients, errors };
};

export default GetClientsHook;
