import { AboutBenefitsSection, AboutUsSection, SetMetaTags } from '@/components';
import { GetOneSeoPageHook } from '@/logic';
import { useEffect } from 'react';

const AboutPage = () => {
    const { metaData } = GetOneSeoPageHook("about");
    useEffect(() => {
        SetMetaTags({
            title: metaData.title_ar,
            description: metaData.description_ar,
            keywords: metaData.keywords_ar,
        })
    }, [metaData])
    return (
        <>
            <AboutUsSection />
            <AboutBenefitsSection />
        </>
    )
}

export default AboutPage