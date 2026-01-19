import { useCallback, useEffect, useState } from "react";
import { ChatItem } from "../common/types";
import {
    fetchChats,
    updateChatName,
    deleteChat,
} from "../api/chatsApi";


interface UseChatsMenuParams {
    userId: string;
    visible: boolean;
}

export function useChatsMenu({
    userId,
    visible
}: UseChatsMenuParams) {
    const [chats, setChats] = useState<ChatItem[]>([]);
    const [loading, setLoading] = useState(false);

    // Fetch chats when menu opens
    useEffect(() => {
        if (!visible) return;

        const loadChats = async () => {
            setLoading(true);
            try {
                const list = await fetchChats(userId);
                setChats(list);
            } catch (err) {
                console.error("Failed to fetch chats", err);
                setChats([]);
            } finally {
                setLoading(false);
            }
        };

        loadChats();
    }, [userId, visible]);

    // Rename chat
    const handleRenameChat = useCallback(
        async (sessionId: string, name: string) => {
            await updateChatName(sessionId, name);

            setChats((prev) =>
                prev.map((c) =>
                    c.session_id === sessionId ? { ...c, name } : c
                )
            );
        },
        []
    );

    // Delete chat
    const handleDeleteChat = useCallback(
        async (sessionId: string) => {
            await deleteChat(sessionId);

            setChats((prev) =>
                prev.filter((c) => c.session_id !== sessionId)
            );
        },
        [userId]
    );

    return {
        chats,
        loading,
        renameChat: handleRenameChat,
        deleteChat: handleDeleteChat
    };
}
