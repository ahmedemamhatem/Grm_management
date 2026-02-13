import { LoginSection, SetMetaTags } from "@/components";
import { GetOneSeoPageHook } from "@/logic";
import { useEffect } from "react";

const LoginPage = () => {
    const { metaData } = GetOneSeoPageHook("login");
    useEffect(() => {
        SetMetaTags({
            title: metaData.title_ar,
            description: metaData.description_ar,
            keywords: metaData.keywords_ar,
        })
    }, [metaData])

    return (
        <LoginSection />
    )
}

export default LoginPage