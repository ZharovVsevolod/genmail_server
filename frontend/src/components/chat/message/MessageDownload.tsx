import React from "react";

interface MessageDownloadProps {
    message_id: string;
    onDownload?: (message_id: string) => void;
}

const MessageDownload: React.FC<MessageDownloadProps> = ({ message_id, onDownload }) => {
    return (
        <button
            className="download-btn"
            onClick={() => onDownload?.(message_id)}
            title="Скачать отчёт"
        >
            <img src="/download.png" alt="Скачать" width="20" height="20" />
        </button>
    );
};

export default MessageDownload;
