
import { getOneSeoAction } from "@/app/actions/seoActions";
import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";

const GetOneSeoPageHook = (PageName) => {
    const dispatch = useDispatch();

    useEffect(() => {
        dispatch(getOneSeoAction(PageName));
    }, []);

    const { isLoading, metaData, errors } = useSelector(
        (state) => state.seo
    );

    return { isLoading, metaData, errors };
};

export default GetOneSeoPageHook;
