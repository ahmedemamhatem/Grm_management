import { IsLoginInHook } from "@/logic";
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

const WithGuard = ({ children }) => {
    const navigate = useNavigate();
    const { isLogin, checkLogin, is_website_user, isLoading, authChecked } = IsLoginInHook();

    useEffect(() => checkLogin(), []);

    useEffect(() => {
        if (!authChecked) return;
        if (!isLogin || !is_website_user) {
            if (!isLogin) {
                navigate("/login", { replace: true });
            } else {
                navigate("/", { replace: true });
            }
        }
    }, [authChecked, isLogin, is_website_user, navigate]);

    if (isLoading) return null;

    return children;
};

export default WithGuard;
