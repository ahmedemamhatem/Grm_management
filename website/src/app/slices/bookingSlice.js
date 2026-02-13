import { createSlice } from "@reduxjs/toolkit";
import { checkAvailabilitySpaceAction, createBookingAction, getAvailabilityTimeSlotsSpaceAction } from "../actions/bookingActions";

const initState = {
    spaceAvailability: {},
    bookingInfo: {},
    timeSlots: [],
    isLoading: false,
    errors: null,
};

const bookingSlice = createSlice({
    name: "booking",
    initialState: initState,
    reducers: {},
    extraReducers: (builder) => {
        builder.addCase(checkAvailabilitySpaceAction.pending, (state) => {
            state.isLoading = true;
            state.errors = null;
            state.spaceAvailability = {};
        });
        builder.addCase(checkAvailabilitySpaceAction.fulfilled, (state, action) => {
            state.isLoading = false;
            state.spaceAvailability = action.payload;
            state.errors = null;
        });
        builder.addCase(checkAvailabilitySpaceAction.rejected, (state, action) => {
            state.isLoading = false;
            state.spaceAvailability = {};
            state.errors = action.payload;
        });
        builder.addCase(createBookingAction.pending, (state) => {
            state.isLoading = true;
            state.errors = null;
            state.bookingInfo = {};
        });
        builder.addCase(createBookingAction.fulfilled, (state, action) => {
            state.isLoading = false;
            state.bookingInfo = action.payload;
            state.errors = null;
        });
        builder.addCase(createBookingAction.rejected, (state, action) => {
            state.isLoading = false;
            state.bookingInfo = {};
            state.errors = action.payload;
        });
        builder.addCase(getAvailabilityTimeSlotsSpaceAction.pending, (state) => {
            state.isLoading = true;
            state.errors = null;
            state.timeSlots = [];
        });
        builder.addCase(getAvailabilityTimeSlotsSpaceAction.fulfilled, (state, action) => {
            state.isLoading = false;
            state.timeSlots = action.payload;
            state.errors = null;
        });
        builder.addCase(getAvailabilityTimeSlotsSpaceAction.rejected, (state, action) => {
            state.isLoading = false;
            state.timeSlots = [];
            state.errors = action.payload;
        });
    },
});

export default bookingSlice.reducer;
