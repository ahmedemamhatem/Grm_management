
import { signUpAction } from "@/app/actions/authActions";
import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { toast } from "sonner";

export default function SignUpHook() {
    const dispatch = useDispatch();
    const { loading, error, user } = useSelector((s) => s.auth);

    const signUpSubmit = async (formValues) => {
        return dispatch(signUpAction(formValues)).unwrap();
    };

    useEffect(() => {
        const message = error?.message;
        if (message) {
            toast.error(message);
        }
    }, [error]);

    return { signUpSubmit, loading, error, user };
}
