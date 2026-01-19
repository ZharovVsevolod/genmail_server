import React from "react";
import { ChatMessage, WSOutgoingMessage, RatingType } from "../common/types";

const useSendWSMessage = (
    ws: React.RefObject<WebSocket | null>,
    setResponses: React.Dispatch<React.SetStateAction<ChatMessage[]>>,
    backend_url: string
) => {
    // Base message sending
    const baseSendMessage = (msg: WSOutgoingMessage) => {
        if (msg.action === "QUERY" && msg.message) {
            const userMessage: ChatMessage = {
                id: Date.now().toString(),
                sender: "Вы",
                message: msg.message
            };
            setResponses(prev => [...prev, userMessage]);
        }

        if (ws.current && ws.current.readyState === WebSocket.OPEN) {
            ws.current.send(JSON.stringify(msg));
        }
    };


    // Sending message for basic default QUERY action
    const sendBasicMessage = (message: string) => {
        baseSendMessage({ action: "QUERY", message });
        console.log("Sent basic QUERY message");
    };


    // Sending message for RATE action
    const sendRateMessage = (message_id: string, rating: RatingType) => {
        const message: WSOutgoingMessage = {
            action: "RATE",
            message_id: message_id,
            rating: rating || undefined
        };
        baseSendMessage(message);
        console.log(`Sent RATE request (${rating || 'remove'}) for message_id:`, message_id);
    };


    // Sending message for final FORMALIZE action
    const sendFormalizeMessage = (message_id: string) => {
        const message: WSOutgoingMessage = {
            action: "FORMALIZE",
            message_id: message_id
        };
        baseSendMessage(message);
        console.log("Sent FORMALIZE request for message_id:", message_id);
    };


    // Upload file and sending start SUMMARIZE message
    const sendUploadAndSummarizeMessage = async () => {
        const input = document.createElement("input");
        input.type = "file";
        input.multiple = true;
        input.onchange = async (event: any) => {
            const files = event.target.files;
            if (!files || files.length === 0) return;

            const formData = new FormData();

            for (const file of files) {
                formData.append("files", file);
            }

            try {
                const response = await fetch(`http://${backend_url}/upload`, {
                    method: "POST",
                    body: formData,
                });
                if (!response.ok) throw new Error("Upload failed");

                const result = await response.json();
                console.log("Uploaded:", result);
                
                // Send SUMMARY action message
                baseSendMessage({ action: "SUMMARY" });

            } catch (err) {
                console.error("Upload error:", err);
            }
        };
        input.click();
    };


    // Send AUTH message
    const sendAuthMessage = (login: string, password: string) => {
        const message: WSOutgoingMessage = {
            action: "AUTH",
            user_id: login,
            user_password: password
        };
        baseSendMessage(message);
        console.log("Sent AUTH request for user", login);
    };


    // Send CREATE message
    const sendCreateNewChatMessage = () => {
        const message: WSOutgoingMessage = {
            action: "CREATE"
        };
        baseSendMessage(message);
        console.log("Sent CREATE new chat message");
    };


    // Send LOAD previous chat message
    const sendLoadPreviousChatMessage = (session_id: string) => {
        const message: WSOutgoingMessage = {
            action: "LOAD_CHAT",
            session_id: session_id
        };
        baseSendMessage(message);
        console.log("Sent LOAD_CHAT message");
    };


    return {
        sendBasicMessage,
        sendRateMessage,
        sendFormalizeMessage,
        sendUploadAndSummarizeMessage,
        sendAuthMessage,
        sendCreateNewChatMessage,
        sendLoadPreviousChatMessage
    }
};

export default useSendWSMessage;