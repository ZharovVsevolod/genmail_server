import React, { useState } from "react";

import { useWebSocket } from "../hooks/useWebSocket";
import useSendWSMessage from "../hooks/useSendWSMessage";

import MessageList from "./messageList/MessageList";
import InputForm from "./inputForm/InputForm";
import ChatsMenu from "./chatMenu/ChatsMenu";
import LoginModal from "./LoginModal";
// import { DropdownInfo } from "./DropdownInfo";

import config from "../../config/config";


const ChatWindow: React.FC = () => {
    // United Base URL (without bus because it could be different)
    const BASE_URL = `${config.pageUrl}:${config.portUrl}`

    // Establish connection. Handle incoming messages
    const {
        ws,
        currentSessionId,
        authState,
        userId,
        userName,
        responses, 
        setResponses
    } = useWebSocket(BASE_URL);

    // Handle outgoing messages
    const {
        sendBasicMessage,
        sendRateMessage,
        sendFormalizeMessage,
        sendUploadAndSummarizeMessage,
        sendAuthMessage,
        sendCreateNewChatMessage,
        sendLoadPreviousChatMessage
    } = useSendWSMessage(ws, setResponses, BASE_URL);

    // For shared input block between InputForm and TextHighligher
    const [inputOfUser, setInputOfUser] = useState("");
    const appendToInput = (text: string) => {
        setInputOfUser(prev => {
            const sep = prev && !prev.endsWith(" ") ? " " : "";
            return prev + sep + text;
        });
    };


    // Render block of whole Chat Window
    return (
        <>
            {/* This user registraton window will show until 
            correct login/password match */}
            <LoginModal
                authState={authState}
                sendAuth={sendAuthMessage}
            />

            {/* Main window */}
            <div className="chat-container">
                {/* <DropdownInfo
                    menuVisible={menuVisible}
                    handleOpenMenu={handleOpenMenu}
                /> */}

                <MessageList 
                    responses={responses} 
                    onDownload={sendFormalizeMessage}
                    onRate={sendRateMessage}
                    appendToInput={appendToInput}
                />

                <InputForm
                    input={inputOfUser}
                    setInput={setInputOfUser}
                    onSend={sendBasicMessage}
                    onUpload={sendUploadAndSummarizeMessage}
                    userId={userId}
                    userName={userName}
                    hasMessages={responses.length > 0}
                />

                <ChatsMenu
                    userId={userId}
                    currentSessionId={currentSessionId}
                    sendCreateNewChatMessage={sendCreateNewChatMessage}
                    sendLoadPreviousChatMessage={sendLoadPreviousChatMessage}
                />
            </div>
        </>
    );
};

export default ChatWindow;