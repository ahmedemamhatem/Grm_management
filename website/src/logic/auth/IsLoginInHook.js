
import { userIsLoginAction } from "@/app/actions/authActions";
import { useDispatch, useSelector } from "react-redux";

const IsLoginInHook = () => {
    const dispatch = useDispatch();

    const checkLogin = () => {
        dispatch(userIsLoginAction());
    }

    const { isLoading, isLogin, errors, is_website_user, authChecked } = useSelector(
        (state) => state.auth
    );

    return { isLoading, isLogin, errors, checkLogin, is_website_user, authChecked };
};

export default IsLoginInHook;
