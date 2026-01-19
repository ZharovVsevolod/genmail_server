const config = {
    pageUrl: import.meta.env.VITE_PAGE_URL as string,
    chatName: import.meta.env.VITE_CHAT_NAME as string,
    portUrl: import.meta.env.VITE_BACKEND_PORT as string,
    user_storage_id: import.meta.env.VITE_USER_ID as string,
    user_storage_name: import.meta.env.VITE_USER_NAME as string
};

export default config;
