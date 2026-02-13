import { createSlice } from "@reduxjs/toolkit";
import { getOneSeoAction } from "../actions/seoActions";

const initState = {
    metaData: {},
    isLoading: false,
    errors: null,
};

const seoSlice = createSlice({
    name: "seo",
    initialState: initState,
    reducers: {},
    extraReducers: (builder) => {
        builder.addCase(getOneSeoAction.pending, (state) => {
            state.isLoading = true;
            state.errors = null;
            state.metaData = {};
        });
        builder.addCase(getOneSeoAction.fulfilled, (state, action) => {
            state.isLoading = false;
            state.metaData = action.payload;
            state.errors = null;
        });
        builder.addCase(getOneSeoAction.rejected, (state, action) => {
            state.isLoading = false;
            state.errors = action.payload;
        });
    },
});

export default seoSlice.reducer;
