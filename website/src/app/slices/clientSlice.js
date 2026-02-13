import { createSlice } from "@reduxjs/toolkit";
import { getClientAction } from "../actions/clientActions";

const initState = {
    clients: [],
    isLoading: false,
    errors: null,
};

const clientSlice = createSlice({
    name: "clients",
    initialState: initState,
    reducers: {},
    extraReducers: (builder) => {
        builder.addCase(getClientAction.pending, (state) => {
            state.isLoading = true;
            state.clients = [];
            state.errors = null;
        });
        builder.addCase(getClientAction.fulfilled, (state, action) => {
            state.isLoading = false;
            state.clients = action.payload;
            state.errors = null;
        });
        builder.addCase(getClientAction.rejected, (state, action) => {
            state.isLoading = false;
            state.clients = [];
            state.errors = action.payload;
        });
    },
});

export default clientSlice.reducer;
