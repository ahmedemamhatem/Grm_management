import { configureStore } from '@reduxjs/toolkit'
import { authSlice, bookingSlice, clientSlice, packagesSlice, profileSlice, seoSlice } from './slices'

export const store = configureStore({
    reducer: {
        packages: packagesSlice,
        auth: authSlice,
        booking: bookingSlice,
        client: clientSlice,
        profile: profileSlice,
        seo: seoSlice,
    },
})