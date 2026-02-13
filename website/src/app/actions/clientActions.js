import { api } from "@/api/axios";
import { createAsyncThunk } from "@reduxjs/toolkit";

export const getClientAction = createAsyncThunk(
    "clients/get-all-clients",
    async (_, thunkAPI) => {
        const { rejectWithValue } = thunkAPI;
        try {
            const { data } = await api.get(`${import.meta.env.VITE_BASE_ENDPOINT}.customers.get_our_customers`)

            return data?.message?.data
        } catch (error) {
            return rejectWithValue(error?.response?.data?.message);
        }
    }
);