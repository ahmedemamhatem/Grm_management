import { api } from "@/api/axios";
import { createAsyncThunk } from "@reduxjs/toolkit";

export const getAllPackagesAction = createAsyncThunk(
    "packages/get-all-packages",
    async (_, thunkAPI) => {
        const { rejectWithValue } = thunkAPI;
        try {
            const { data } = await api.get(`${import.meta.env.VITE_BASE_ENDPOINT}.spaces.get_spaces_by_type`)

            return {
                spaces: data?.message?.data,
                space_count: data?.message?.data?.total_spaces,
                space_types: data?.message?.data?.total_types,
            };
        } catch (error) {
            return rejectWithValue(error?.response?.data?.message);
        }
    }
);

export const getOnePackageAction = createAsyncThunk(
    "packages/get-one-package",
    async (id, thunkAPI) => {
        const { rejectWithValue } = thunkAPI;
        try {
            const { data } = await api.get(`${import.meta.env.VITE_BASE_ENDPOINT}.spaces.get_space_by_id?id=${id}`)

            return data?.message?.data
        } catch (error) {
            return rejectWithValue(error?.response?.data?.message);
        }
    }
);