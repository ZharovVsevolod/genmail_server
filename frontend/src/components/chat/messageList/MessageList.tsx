import React, { useEffect } from "react";
import Message from "../message/Message";
import { ChatMessage, RatingType } from "../../common/types";
import { useAutoScroll } from "./AutoScroll";

interface MessageListProps {
    responses: ChatMessage[];
    onDownload?: (message_id: string) => void;
    onRate: (message_id: string, rating: RatingType) => void;
    appendToInput: (text: string) => void;
}

const MessageList: React.FC<MessageListProps> = ({ 
    responses, 
    onDownload, 
    onRate, 
    appendToInput 
}) => {
    // Auto scroll when new text appears
    const { ref: messagesEndRef, scroll } = useAutoScroll<HTMLDivElement>();
    useEffect(() => scroll(), [responses]);

    return (
        <div className="messages-container">
            {responses.map((res, i) => (
                <Message 
                    key={res.message_id || i}
                    sender={res.sender}
                    message={res.message}
                    message_id={res.message_id}
                    currentRating={res.rating ?? null}
                    onDownload={onDownload}
                    onRate={onRate}
                    appendToInput={appendToInput}
                />
            ))}
            <div ref={messagesEndRef} />
        </div>
    );
};

export default MessageList