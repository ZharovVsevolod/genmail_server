import React from "react";
import { ChatItem } from "../../common/types";
import { ChatRow } from "./ChatRow";

interface ChatListProps {
    chats: ChatItem[];
    currentSessionId: string;
    loading: boolean;
    onSelect: (sessionId: string) => void;
    onRename: (sessionId: string, name: string) => Promise<void>;
    onDelete: (sessionId: string) => Promise<void>;
}

export const ChatList: React.FC<ChatListProps> = ({
    chats,
    currentSessionId,
    loading,
    onSelect,
    onRename,
    onDelete,
}) => {
    if (loading) {
        return <div>Загрузка...</div>;
    }

    if (!chats.length) {
        return <div className="empty-chats">Нет диалогов</div>;
    }

    return (
        <>
            {chats.map((chat) => (
                <ChatRow
                    key={chat.session_id}
                    chat={chat}
                    currentSessionId={currentSessionId}
                    onSelect={onSelect}
                    onRename={onRename}
                    onDelete={onDelete}
                />
            ))}
        </>
    );
};
