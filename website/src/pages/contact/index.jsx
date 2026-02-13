import { InfoSection, SetMetaTags } from '@/components';
import { GetOneSeoPageHook } from '@/logic';
import { useEffect } from 'react';

const ContactPage = () => {
    const { metaData } = GetOneSeoPageHook("contact");
    useEffect(() => {
        SetMetaTags({
            title: metaData.title_ar,
            description: metaData.description_ar,
            keywords: metaData.keywords_ar,
        })
    }, [metaData])
    return (
        <>
            <InfoSection />
        </>
    )
}


export default ContactPage
