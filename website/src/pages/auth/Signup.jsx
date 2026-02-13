import { SetMetaTags, SignupSection } from "@/components";
import { GetOneSeoPageHook } from "@/logic";
import { useEffect } from "react";

const SignUpPage = () => {
    const { metaData } = GetOneSeoPageHook("signup");
    useEffect(() => {
        SetMetaTags({
            title: metaData.title_ar,
            description: metaData.description_ar,
            keywords: metaData.keywords_ar,
        })
    }, [metaData])

    return (
        <SignupSection />
    )
}

export default SignUpPage