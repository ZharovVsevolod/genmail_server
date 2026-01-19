import { ChatItem, ChatMessage } from "../common/types";
import config from "../../config/config";


const API_BASE = `http://${config.pageUrl}:${config.portUrl}`


export async function fetchChats(userId: string): Promise<ChatItem[]> {
    const res = await fetch(
        `${API_BASE}/chat/list?user_id=${encodeURIComponent(userId)}`
    );

    if (!res.ok) {
        throw new Error("Failed to fetch chats");
    }

    const data = await res.json();
    return data.chat_list as ChatItem[];
}


export async function updateChatName(
    sessionId: string,
    name: string
): Promise<void> {
    const res = await fetch(
        `${API_BASE}/chat/update?session_id=${encodeURIComponent(
        sessionId
        )}&session_name=${encodeURIComponent(name)}`
    );

    if (!res.ok) {
        throw new Error("Failed to update chat");
    }
}


export async function deleteChat(
    sessionId: string
): Promise<void> {
    const res = await fetch(
        `${API_BASE}/chat/delete?session_id=${encodeURIComponent(sessionId)}`
    );

    if (!res.ok) {
        throw new Error("Failed to delete chat");
    }
}
