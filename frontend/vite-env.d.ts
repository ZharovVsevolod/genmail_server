interface ImportMetaEnv {
    readonly VITE_PAGE_URL: string; 
    readonly VITE_CHAT_NAME: string;
    readonly VITE_BACKEND_PORT: string;
    readonly VITE_USER_ID: string;
    readonly VITE_USER_NAME: string;
}

interface ImportMeta {
    readonly env: ImportMetaEnv;
}