import { SetMetaTags, WhyChooseGrmSection } from '@/components';
import { GetOneSeoPageHook } from '@/logic';
import { useEffect } from 'react';

const WhyChooseUsPage = () => {
    const { metaData } = GetOneSeoPageHook("why_choose_us");
    useEffect(() => {
        SetMetaTags({
            title: metaData.title_ar,
            description: metaData.description_ar,
            keywords: metaData.keywords_ar,
        })
    }, [metaData])
    return (
        <>
            <WhyChooseGrmSection />
        </>
    )
}

export default WhyChooseUsPage
