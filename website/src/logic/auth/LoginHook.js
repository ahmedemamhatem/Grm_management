import { loginAction } from "@/app/actions/authActions";
import Cookies from "js-cookie";
import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";

export default function LoginHook() {
    const dispatch = useDispatch();
    const navigate = useNavigate();
    const { isLoading, error, user, authChecked, home_page } = useSelector((s) => s.auth);

    const loginSubmit = async (formValues) => {
        dispatch(loginAction(formValues));
    };

    useEffect(() => {
        const message = error?.message;
        if (message) {
            toast.error(message);
        }
    }, [error]);

    useEffect(() => {
        if (!isLoading && user && home_page ) {
            if(home_page === "/home"){
                navigate("/profile")
            } else {
                window.location.href = home_page;
            }
        }
    }, [isLoading, user, home_page]);


    return { loginSubmit, isLoading, error, user, authChecked };
}
