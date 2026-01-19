import React, { useState } from "react";
import { ChatItem } from "../../common/types";

interface ChatRowProps {
    chat: ChatItem;
    currentSessionId: string;
    onSelect: (sessionId: string) => void;
    onRename: (sessionId: string, name: string) => Promise<void>;
    onDelete: (sessionId: string) => Promise<void>;
}

export const ChatRow: React.FC<ChatRowProps> = ({
    chat,
    currentSessionId,
    onSelect,
    onRename,
    onDelete,
}) => {
    const [isEditing, setIsEditing] = useState(false);
    const [name, setName] = useState(chat.name);
    const [saving, setSaving] = useState(false);

    const handleSave = async () => {
        const trimmed = name.trim();
        if (!trimmed || trimmed === chat.name) {
            setIsEditing(false);
            setName(chat.name);
            return;
        }

        try {
            setSaving(true);
            await onRename(chat.session_id, trimmed);
            setIsEditing(false);
        } catch (err) {
            console.error("Rename failed", err);
            alert("Не удалось переименовать диалог");
            setName(chat.name);
        } finally {
            setSaving(false);
        }
    };

    const handleDelete = async () => {
        if (!confirm(`Удалить диалог "${chat.name}"?`)) return;

        try {
            await onDelete(chat.session_id);
        } catch (err) {
            console.error("Delete failed", err);
            alert("Не удалось удалить диалог");
        }
    };

    return (
        // className={`prompts-panel ${!hasMessages ? 'prompts-panel--bottom' : ''}`}
        <div className={`chat-row ${currentSessionId == chat.session_id ? "chat-row-selected" : ""}`}>
            <div
                className="chat-main"
                onClick={() => !isEditing && onSelect(chat.session_id)}
            >
                {isEditing ? (
                <input
                    className="chat-edit-input"
                    value={name}
                    autoFocus
                    disabled={saving}
                    onChange={(e) => setName(e.target.value)}
                    onKeyDown={(e) => {
                    if (e.key === "Enter") handleSave();
                    if (e.key === "Escape") {
                        setIsEditing(false);
                        setName(chat.name);
                    }
                    }}
                />
                ) : (
                <div className="chat-title">{chat.name}</div>
                )}
            </div>

            <div className="chat-actions">
                {isEditing ? (
                    <>
                        <button
                            className="icon-btn save-btn"
                            onClick={handleSave}
                            disabled={saving}
                        >
                            Сохранить
                        </button>

                        <button
                            className="icon-btn cancel-btn"
                            onClick={() => {
                                setIsEditing(false);
                                setName(chat.name);
                            }}
                            disabled={saving}
                        >
                            Отмена
                        </button>
                    </>
                    ) : (
                    <>
                        <button
                            className="icon-btn edit-btn"
                            onClick={() => setIsEditing(true)}
                            title="Переименовать"
                        >
                            <img src="/edit.png" alt="edit" />
                        </button>

                        <button
                            className="icon-btn delete-btn"
                            onClick={handleDelete}
                            title="Удалить"
                        >
                            <img src="/delete.png" alt="delete" />
                        </button>
                    </>
                )}
            </div>
        </div>
    );
};
