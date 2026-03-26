import { env } from '$env/dynamic/public';

export const getApiUrl = () => {
    const apiUrl = env.PUBLIC_API_URL || import.meta.env.VITE_API_URL;
    
    if (!apiUrl) {
        throw new Error("CRITICAL: API URL is not set. Please set PUBLIC_API_URL or VITE_API_URL in your environment or .env file.");
    }
    
    return apiUrl;
};
