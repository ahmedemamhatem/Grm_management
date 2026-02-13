import { ClientsSection, SetMetaTags } from '@/components';
import { GetOneSeoPageHook } from '@/logic';
import React, { useEffect } from 'react'

const ClientsPage = () => {
    const { metaData } = GetOneSeoPageHook("clients");
    useEffect(() => {
        SetMetaTags({
            title: metaData.title_ar,
            description: metaData.description_ar,
            keywords: metaData.keywords_ar,
        })
    }, [metaData])
    return (
        <ClientsSection />
    )
}

export default ClientsPage