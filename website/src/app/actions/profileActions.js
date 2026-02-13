import { api } from "@/api/axios";
import { createAsyncThunk } from "@reduxjs/toolkit";

export const getProfileAction = createAsyncThunk(
    "profile/get-profile",
    async (_, thunkAPI) => {
        const { rejectWithValue } = thunkAPI;
        try {
            const { data } = await api.get(`${import.meta.env.VITE_BASE_ENDPOINT}.auth.get_current_user`)

            return data?.message?.data
        } catch (error) {
            return rejectWithValue(error?.response?.data?.message)
        }
    }
);

export const getProfileBookingsAction = createAsyncThunk(
    "profile/get-profile-bookings",
    async (_, thunkAPI) => {
        const { rejectWithValue } = thunkAPI;
        try {
            const { data } = await api.get(`${import.meta.env.VITE_BASE_ENDPOINT}.booking.get_my_bookings`)

            return data?.message?.data?.bookings
        } catch (error) {
            return rejectWithValue(error?.response?.data?.message)
        }
    }
);

export const updateProfileAction = createAsyncThunk(
    "profile/update-profile",
    async ({ first_name, last_name, phone, city, address }, thunkAPI) => {
        const { rejectWithValue } = thunkAPI;
        try {
            const { data } = await api.post(`${import.meta.env.VITE_BASE_ENDPOINT}.auth.update_profile`, {
                first_name,
                last_name,
                phone,
                city,
                address
            })

            return data?.message?.message
        } catch (error) {
            return rejectWithValue(error?.response?.data?.message)
        }
    }
);

export const updateProfilePasswordAction = createAsyncThunk(
    "profile/update-profile-password",
    async ({ current_password, new_password }, thunkAPI) => {
        const { rejectWithValue } = thunkAPI;
        try {
            const { data } = await api.post(`${import.meta.env.VITE_BASE_ENDPOINT}.auth.change_password`, {
                current_password,
                new_password
            })

            return data?.message?.message
        } catch (error) {
            return rejectWithValue(error?.response?.data?.message?.message)
        }
    }
);