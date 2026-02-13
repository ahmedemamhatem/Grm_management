import { createSlice } from "@reduxjs/toolkit";
import { getAllPackagesAction, getOnePackageAction } from "../actions/packagesActions";

const initState = {
    packages: {},
    onePackage: {},
    space_count: 0,
    space_types: 0,
    isLoading: false,
    errors: null,
};

const packagesSlice = createSlice({
    name: "packages",
    initialState: initState,
    reducers: {},
    extraReducers: (builder) => {
        builder.addCase(getAllPackagesAction.pending, (state) => {
            state.isLoading = true;
            state.packages = {};
            state.space_count = 0;
            state.space_types = 0;
            state.errors = null;
        });
        builder.addCase(getAllPackagesAction.fulfilled, (state, action) => {
            state.isLoading = false;
            state.packages = action.payload.spaces;
            state.space_count = action.payload.space_count;
            state.space_types = action.payload.space_types;
            state.errors = null;
        });
        builder.addCase(getAllPackagesAction.rejected, (state, action) => {
            state.isLoading = false;
            state.packages = {};
            state.space_count = 0;
            state.space_types = 0;
            state.errors = action.payload;
        });
        builder.addCase(getOnePackageAction.pending, (state) => {
            state.isLoading = true;
            state.onePackage = {};
            state.errors = null;
        });
        builder.addCase(getOnePackageAction.fulfilled, (state, action) => {
            state.isLoading = false;
            state.onePackage = action.payload;
            state.errors = null;
        });
        builder.addCase(getOnePackageAction.rejected, (state, action) => {
            state.isLoading = false;
            state.onePackage = {};
            state.errors = action.payload;
        });
    },
});

export default packagesSlice.reducer;
