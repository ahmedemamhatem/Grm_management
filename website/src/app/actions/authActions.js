import api from "@/api/axios";
import { createAsyncThunk } from "@reduxjs/toolkit";

export const signUpAction = createAsyncThunk(
    "auth/sign-up",
    async ({ first_name, last_name, email, password, phone, tenant_type, company_name, commercial_registration, tax_id }, thunkAPI) => {
        const { rejectWithValue } = thunkAPI;
        try {
            const { data } = await api.post(`${import.meta.env.VITE_BASE_ENDPOINT}.auth.signup`, {
                first_name,
                last_name,
                email,
                password,
                phone,
                tenant_type,
                company_name,
                commercial_registration,
                tax_id
            })

            return data?.message
        } catch (error) {
            return rejectWithValue(error?.response?.data?.message);
        }
    }
);

export const loginAction = createAsyncThunk(
    "auth/login",
    async ({ usr, pwd }, thunkAPI) => {
        const { rejectWithValue } = thunkAPI;
        try {
            const { data } = await api.post(`${import.meta.env.VITE_BASE_ENDPOINT}.auth.login`, {
                usr,
                pwd,
            })

            return {
                user: data?.message?.data,
                home: data?.home_page
            }
        } catch (error) {
            return rejectWithValue(error?.response?.data?.message);
        }
    }
);

export const userIsLoginAction = createAsyncThunk(
    "auth/user-is-login",
    async (_, thunkAPI) => {
        const { rejectWithValue } = thunkAPI;
        try {
            const { data } = await api.get(`${import.meta.env.VITE_BASE_ENDPOINT}.auth.auth_status`)

            return data?.message?.data
        } catch (error) {
            return rejectWithValue(error?.response?.data?.message);
        }
    }
);

export const logoutAction = createAsyncThunk(
    "auth/logout",
    async (_, thunkAPI) => {
        const { rejectWithValue } = thunkAPI;
        try {
            const { data } = await api.get(`${import.meta.env.VITE_BASE_ENDPOINT}.auth.logout`)

            return data?.message
        } catch (error) {
            return rejectWithValue(error?.response?.data?.message);
        }
    }
);