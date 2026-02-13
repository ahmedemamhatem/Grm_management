import { SetMetaTags } from '@/components';
import ProfileSection from '@/components/profile/Profile';
import { GetOneSeoPageHook } from '@/logic';
import { useEffect } from 'react';

const ProfilePage = () => {
    const { metaData } = GetOneSeoPageHook("profile");
    useEffect(() => {
        SetMetaTags({
            title: metaData.title_ar,
            description: metaData.description_ar,
            keywords: metaData.keywords_ar,
        })
    }, [metaData])
    return <ProfileSection />
}

export default ProfilePage