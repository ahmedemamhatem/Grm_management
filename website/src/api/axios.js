import axios from "axios";

axios.defaults.withCredentials = true;

const csrfInterceptor = (config) => {
    const method = (config.method || "get").toLowerCase();
    const needsCsrf = ["post", "put", "patch", "delete"].includes(method);

    const csrf =
        window.csrf_token ||
        (window.frappe && window.frappe.csrf_token);

    if (needsCsrf && csrf) {
        config.headers["X-Frappe-CSRF-Token"] = csrf;
    }

    return config;
};


axios.interceptors.request.use(csrfInterceptor);

export const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
    withCredentials: true,
});

api.interceptors.request.use(csrfInterceptor);


export default api;