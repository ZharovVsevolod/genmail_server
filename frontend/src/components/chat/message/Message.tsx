import React, {useEffect} from "react";
import { RatingType } from "../../common/types";
import MessageContent from "./MessageContent";
import MessageRating from "./MessageRating";
import TextHighlighter, {getHightligherProps} from "./TextHighlighter";
import MessageCopy from "./MessageCopy";
import MessageDownload from "./MessageDownload";

import config from "../../../config/config";

interface MessageProps {
    sender: string;
    message: string;
    message_id?: string;
    currentRating: RatingType;
    onDownload?: (message_id: string) => void;
    onRate: (message_id: string, rating: RatingType) => void;
    appendToInput: (text: string) => void;
}

const Message: React.FC<MessageProps> = ({
    sender,
    message,
    message_id,
    currentRating,
    onDownload,
    onRate,
    appendToInput
}) => {
    const {selectedText, show, bubbleRef, pos, setShow, handleMouseUp} = getHightligherProps();

    const isBot = sender === config.chatName;

    useEffect(() => {
        const hide = () => {
            // hide insert when clicking elsewhere
            const sel = window.getSelection();
            if (!sel || !sel.toString()) {
                setShow(false);
            }
        };
        document.addEventListener("mousedown", hide);
        return () => document.removeEventListener("mousedown", hide);
    }, []);

    return (
        <div 
            className={`message-bubble ${isBot ? 'message-bot' : 'message-user'}`}
            ref={bubbleRef} 
            onMouseUp={handleMouseUp}
        >
            {/* Actual text context of message */}
            <MessageContent sender={sender} message={message} />

            {/* Rating/Actions only for assistant messages */}
            {sender === config.chatName && message_id && (
                <div className="actions-section">
                    <MessageCopy message={message} />

                    <MessageRating
                        message_id={message_id}
                        currentRating={currentRating}
                        onRate={onRate}
                    />

                    <MessageDownload
                        message_id={message_id}
                        onDownload={onDownload}
                    />
                </div>
            )}

            {/* Text selection highlight logic */}
            {show && 
                <TextHighlighter
                    pos={pos}
                    selectedText={selectedText}
                    setShow={setShow}
                    appendToInput={appendToInput}
                />
            }
        </div>
    );
};

export default Message;
