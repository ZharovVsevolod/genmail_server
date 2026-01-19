import React from "react";
import ReactMarkdown from "react-markdown";

interface MessageContentProps {
    sender: string;
    message: string;
}

const MessageContent: React.FC<MessageContentProps> = ({ sender, message }) => {
    return (
        <>
            <div className="message-header">
                <strong>{sender}</strong>
                <span className="message-time">
                    {new Date().toLocaleTimeString("ru-RU", {
                        hour: "2-digit",
                        minute: "2-digit",
                    })}
                </span>
            </div>

            <ReactMarkdown>{message}</ReactMarkdown>
        </>
    );
};

export default MessageContent;
