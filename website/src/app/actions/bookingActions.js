import { api } from "@/api/axios";
import { createAsyncThunk } from "@reduxjs/toolkit";

export const checkAvailabilitySpaceAction = createAsyncThunk(
    "booking/check-availability-space",
    async ({ space, booking_date, start_time, end_time }, thunkAPI) => {
        const { rejectWithValue } = thunkAPI;
        try {
            const { data } = await api.get(`${import.meta.env.VITE_BASE_ENDPOINT}.booking.check_availability?space=${space}&booking_date=${booking_date}&start_time=${start_time}&end_time=${end_time}`)

            return data?.message?.booking_info
        } catch (error) {
            return rejectWithValue(error?.response?.data?.message)
        }
    }
);

export const getAvailabilityTimeSlotsSpaceAction = createAsyncThunk(
    "booking/get-availability-time-slots-space",
    async ({ space, date, slot_duration_minutes }, thunkAPI) => {
        const { rejectWithValue } = thunkAPI;
        try {
            const { data } = await api.get(`${import.meta.env.VITE_BASE_ENDPOINT}.booking.get_available_slots?space=${space}&date=${date}&slot_duration_minutes=${slot_duration_minutes}`)

            return data?.message?.data?.slots
        } catch (error) {
            return rejectWithValue(error?.response?.data?.message)
        }
    }
);

export const createBookingAction = createAsyncThunk(
    "booking/create-booking",
    async (payload, thunkAPI) => {
        const { rejectWithValue } = thunkAPI;
        try {
            const { data } = await api.post(`${import.meta.env.VITE_BASE_ENDPOINT}.booking.create_booking`, payload)

            return data?.message?.message
        } catch (error) {
            return rejectWithValue(error?.response?.data?.message)
        }
    }
);