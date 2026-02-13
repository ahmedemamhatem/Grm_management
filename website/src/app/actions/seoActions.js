import { api } from "@/api/axios";
import { createAsyncThunk } from "@reduxjs/toolkit";

export const getOneSeoAction = createAsyncThunk(
    "seo/get-one-seo",
    async (page, thunkAPI) => {
        const { rejectWithValue } = thunkAPI;
        try {
            const { data } = await api.get(`${import.meta.env.VITE_BASE_ENDPOINT}.seo.get_seo?page=${page}`)

            return data?.message?.data
        } catch (error) {
            return rejectWithValue(error?.response?.data?.message)
        }
    }
);