import { PackagesContainer, SetMetaTags } from '@/components';
import { GetOneSeoPageHook } from '@/logic';
import { useEffect } from 'react';

const PackagesPage = () => {
    const { metaData } = GetOneSeoPageHook("spaces");
    useEffect(() => {
        SetMetaTags({
            title: metaData.title_ar,
            description: metaData.description_ar,
            keywords: metaData.keywords_ar,
        })
    }, [metaData])
    return <PackagesContainer />
}

export default PackagesPage
