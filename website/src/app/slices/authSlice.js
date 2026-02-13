import { createSlice } from "@reduxjs/toolkit";
import { loginAction, logoutAction, signUpAction, userIsLoginAction } from "../actions/authActions";

const initState = {
    user: {},
    isLogin: false,
    isLoading: false,
    is_website_user: false,
    authChecked: false,
    error: null,
    home_page: null
};

const authSlice = createSlice({
    name: "auth",
    initialState: initState,
    reducers: {},
    extraReducers: (builder) => {
        builder.addCase(signUpAction.pending, (state) => {
            state.isLoading = true;
            state.error = null;
            state.user = {};
        });
        builder.addCase(signUpAction.fulfilled, (state, action) => {
            state.isLoading = false;
            state.user = action.payload;
            state.error = null;
        });
        builder.addCase(signUpAction.rejected, (state, action) => {
            state.isLoading = false;
            state.user = {};
            state.error = action.payload;
        });
        builder.addCase(loginAction.pending, (state) => {
            state.isLoading = true;
            state.error = null;
            state.user = {};
            state.authChecked = false;
            state.home_page = null;
        });
        builder.addCase(loginAction.fulfilled, (state, action) => {
            state.isLoading = false;
            state.user = action.payload.user;
            state.home_page = action.payload.home;
            state.error = null;
            state.authChecked = true;
        });
        builder.addCase(loginAction.rejected, (state, action) => {
            state.isLoading = false;
            state.user = {};
            state.error = action.payload;
            state.authChecked = true;
            state.home_page = null;
        });
        builder.addCase(userIsLoginAction.pending, (state) => {
            state.isLoading = true;
            state.error = null;
            state.isLogin = false;
            state.is_website_user = false;
            state.authChecked = false;
        });
        builder.addCase(userIsLoginAction.fulfilled, (state, action) => {
            state.isLoading = false;
            state.isLogin = action.payload?.authenticated;
            state.is_website_user = action.payload?.is_website_user;
            state.error = null;
            state.authChecked = true;
        });
        builder.addCase(userIsLoginAction.rejected, (state, action) => {
            state.isLoading = false;
            state.error = action.payload;
            state.isLogin = false;
            state.is_website_user = false;
            state.authChecked = true;
        });
        builder.addCase(logoutAction.pending, (state) => {
            state.isLoading = true;
            state.error = null;
            state.authChecked = false;
        });
        builder.addCase(logoutAction.fulfilled, (state, action) => {
            state.isLoading = false;
            state.error = null;
            state.isLogin = false;
            state.authChecked = true;
        });
        builder.addCase(logoutAction.rejected, (state, action) => {
            state.isLoading = false;
            state.error = action.payload;
            state.authChecked = true;
        });
    },
});

export default authSlice.reducer;
