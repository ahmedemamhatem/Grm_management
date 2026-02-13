import { createSlice } from "@reduxjs/toolkit";
import { getProfileAction, getProfileBookingsAction, updateProfileAction, updateProfilePasswordAction } from "../actions/profileActions";

const initState = {
    profile: {},
    profileUpdate: {},
    bookings: [],
    profilePasswordUpdate: {},
    isLoading: false,
    errors: null,
};

const profileSlice = createSlice({
    name: "profile",
    initialState: initState,
    reducers: {},
    extraReducers: (builder) => {
        builder.addCase(getProfileAction.pending, (state) => {
            state.isLoading = true;
            state.profile = {};
            state.errors = null;
        });
        builder.addCase(getProfileAction.fulfilled, (state, action) => {
            state.isLoading = false;
            state.profile = action.payload;
            state.errors = null;
        });
        builder.addCase(getProfileAction.rejected, (state, action) => {
            state.isLoading = false;
            state.profile = {};
            state.errors = action.payload;
        });
        builder.addCase(getProfileBookingsAction.pending, (state) => {
            state.isLoading = true;
            state.bookings = [];
            state.errors = null;
        });
        builder.addCase(getProfileBookingsAction.fulfilled, (state, action) => {
            state.isLoading = false;
            state.bookings = action.payload;
            state.errors = null;
        });
        builder.addCase(getProfileBookingsAction.rejected, (state, action) => {
            state.isLoading = false;
            state.bookings = [];
            state.errors = action.payload;
        });
        builder.addCase(updateProfileAction.pending, (state) => {
            state.isLoading = true;
            state.profileUpdate = {};
            state.errors = null;
        });
        builder.addCase(updateProfileAction.fulfilled, (state, action) => {
            state.isLoading = false;
            state.profileUpdate = action.payload;
            state.errors = null;
        });
        builder.addCase(updateProfileAction.rejected, (state, action) => {
            state.isLoading = false;
            state.profileUpdate = {};
            state.errors = action.payload;
        });
        builder.addCase(updateProfilePasswordAction.pending, (state) => {
            state.isLoading = true;
            state.profilePasswordUpdate = {};
            state.errors = null;
        });
        builder.addCase(updateProfilePasswordAction.fulfilled, (state, action) => {
            state.isLoading = false;
            state.profilePasswordUpdate = action.payload;
            state.errors = null;
        });
        builder.addCase(updateProfilePasswordAction.rejected, (state, action) => {
            state.isLoading = false;
            state.profilePasswordUpdate = {};
            state.errors = action.payload;
        });
    },
});

export default profileSlice.reducer;
