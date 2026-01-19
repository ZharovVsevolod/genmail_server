import React from "react";

interface MessageCopyProps {
    message: string;
}

const MessageCopy: React.FC<MessageCopyProps> = ({ message }) => {
    return (
        <button
            type="button"
            className="copy-btn"
            onClick={() => navigator.clipboard?.writeText(message)}
            title="Копировать текст"
        >
            <img src="/copy.png" alt="Copy" width="20" height="20" />
        </button>
    );
};

export default MessageCopy;
