import { AboutSection, FaqSection, FeaturesSection, HeroSection, HomePricingSection, SetMetaTags, TestimonialsSection, WorkflowSection } from "@/components"
import { useEffect } from "react"


const HomePage = () => {
    useEffect(() => {
        SetMetaTags({
            title: "الصفحة الرئيسية",
            description: "",
            keywords: "",
        })
    }, [])
    return (
        <>
            <HeroSection />
            <AboutSection />
            <FeaturesSection />
            <WorkflowSection />
            <HomePricingSection />
            <TestimonialsSection />
            <FaqSection />
        </>
    )
}

export default HomePage