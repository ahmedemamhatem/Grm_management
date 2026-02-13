
import { logoutAction } from "@/app/actions/authActions";
import Cookies from "js-cookie";
import { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";

const LogoutHook = () => {
    const dispatch = useDispatch();
    const [isLoggedIn, setIsLoggedIn] = useState(false);

    const logoutSubmit = async () => {
        dispatch(logoutAction());
        setIsLoggedIn(false);
        window.location.href = "/";
    }


    useEffect(() => {
        const checkLoginStatus = () => {
            const userId = Cookies.get("user_id");
            const systemUser = Cookies.get("system_user");

            // Check if user is not logged in (Guest) or no system user
            if (!systemUser || userId === "Guest") {
                setIsLoggedIn(false);
            } else {
                setIsLoggedIn(true);
            }
        };

        checkLoginStatus();
        const interval = setInterval(checkLoginStatus, 1000);
        return () => clearInterval(interval);
    }, []);


    const { isLoading, error, authChecked } = useSelector(
        (state) => state.auth
    );

    return { isLoading, error, logoutSubmit, authChecked, isLoggedIn };
};

export default LogoutHook;
