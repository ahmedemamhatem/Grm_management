import { AboutSection, FaqSection, FeaturesSection, HeroSection, HomePricingSection, SetMetaTags, TestimonialsSection, WorkflowSection } from "@/components";
import { GetOneSeoPageHook } from "@/logic";
import { useEffect } from "react";
import { toast } from "sonner";


const HomePage = () => {
    const { metaData } = GetOneSeoPageHook("home");
    useEffect(() => {
        SetMetaTags({
            title: metaData.title_ar,
            description: metaData.description_ar,
            keywords: metaData.keywords_ar,
        })
    }, [metaData])
    return (
        <>
            <HeroSection />
            <AboutSection />
            <FeaturesSection />
            <WorkflowSection />
            {/* <HomePricingSection /> */}
            <TestimonialsSection />
            <FaqSection />
        </>
    )
}

export default HomePage