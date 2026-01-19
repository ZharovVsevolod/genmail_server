import React from "react";

interface CreateChatButtonProps {
    onCreate: () => void;
}

export const CreateChatButton: React.FC<CreateChatButtonProps> = ({
    onCreate,
}) => {
    return (
        <div className="create-chat-row">
            <button className="create-chat-btn" onClick={onCreate}>
                <img src="/add.png" alt="add" />
                <span className="create-text">Создать</span>
            </button>
        </div>
    );
};
