import axios from "axios";
import Cookies from "js-cookie";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const UserLoggedInHook = () => {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const navigate = useNavigate();

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

    const handleAuthClick = async () => {
        if (isLoggedIn) {
            try {
                await axios.get(`${import.meta.env.VITE_BASE_URL}/api/method/logout`, {
                    withCredentials: true,
                    headers: {
                        Accept: "application/json",
                        "Content-Type": "application/json",
                    },
                });
                setIsLoggedIn(false);
                navigate("/login");
            } catch (error) {
                console.error("Logout failed:", error);
            }
        }
    };

    return { isLoggedIn, handleAuthClick };
};

export default UserLoggedInHook;
