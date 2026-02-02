import { AboutUsSection, SetMetaTags } from '@/components'
import { useEffect } from 'react'

const AboutPage = () => {
    useEffect(() => {
        SetMetaTags({
            title: "عن قرم",
            description: "",
            keywords: "",
        })
    }, [])
    return (
        <>
            <AboutUsSection />
        </>
    )
}

export default AboutPage