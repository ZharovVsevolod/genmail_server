import { useState, useEffect, useRef } from "react";
import type { ChatMessage, WSIncomingEvent, AuthState } from "../common/types";
import handleFileAutoDownload from "./useFileAutoDownload";

export const useWebSocket = (url: string) => {
    const ws = useRef<WebSocket | null>(null);
    const [responses, setResponses] = useState<ChatMessage[]>([]);
    const [currentSessionId, setCurrentSessionId] = useState<string>("");

    // For login pass
    const [authState, setAuthState] = useState<AuthState>(null);
    const [userId, setUserId] = useState<string>("");
    const [userName, setUserName] = useState<string | null>(null);


    useEffect(() => {
        ws.current = new WebSocket(`ws://${url}/ws/chat/`);
        let ongoingStream: { id: string; content: string } | null = null;

        ws.current.onmessage = (event: MessageEvent) => {
            const data: WSIncomingEvent = JSON.parse(event.data);
            const sender = (data as any).name ?? "System";

            console.log(data)

            switch (data.event) {
                case "on_parser_start":
                    ongoingStream = { id: data.run_id, content: "" };
                    setResponses((prev) => [
                        ...prev,
                        { 
                            id: data.run_id, 
                            sender, 
                            message: "" 
                        },
                    ]);
                    break;
                
                case "thinking_start":
                    if (data.run_id === ongoingStream?.id) {
                        setResponses((prev) =>
                            prev.map((msg) =>
                                msg.id === data.run_id
                                ? { ...msg, message: "Думаю..." }
                                : msg
                            )
                        );
                    }
                    break;
                
                case "thinking_end":
                    if (data.run_id === ongoingStream?.id) {
                        setResponses((prev) =>
                            prev.map((msg) =>
                                msg.id === data.run_id
                                ? { ...msg, message: "" }
                                : msg
                            )
                        );
                    }
                    break;

                case "on_parser_stream":
                    if (data.run_id === ongoingStream?.id) {
                        setResponses((prev) =>
                            prev.map((msg) =>
                                msg.id === data.run_id
                                ? { ...msg, message: msg.message + data.data.chunk }
                                : msg
                            )
                        );
                    }
                    break;

                case "on_generation_end":
                    // Сохраняем message_id для последнего сообщения бота
                    if (data.message_id) {
                        setResponses((prev) =>
                            prev.map((msg, index) =>
                                index === prev.length - 1 && msg.sender === sender
                                    ? { ...msg, message_id: data.message_id }
                                    : msg
                            )
                        );
                    }
                    break;

                case "document_extraction":
                    setResponses((prev) => [
                        ...prev,
                        { sender, message: "Обработка файла, извлечение текста...", id: data.run_id },
                    ]);
                    break;
                
                case "document_summarization":
                    setResponses((prev) =>
                        prev.map((msg) =>
                            msg.id === data.run_id
                            ? { ...msg, message: "Обработка файла, суммаризация текста..." }
                            : msg
                        )
                    );
                    break;

                case "summary":
                    let messageToSend: string = ""
                    for (const key in data.data) {
                        messageToSend += `#### ${key}\n${data.data[key]}`;
                        messageToSend += "\n";
                    }
                    setResponses((prev) => [
                        ...prev,
                        { 
                            id: data.run_id, 
                            sender, 
                            message: messageToSend 
                        },
                    ]);
                    break;

                case "download":
                    console.log("Download event received:", data);
                    const downloadUrl = `http://${url}/download?filename=${data.filename}`;
                    
                    // Автоматически скачиваем файл
                    setTimeout(() => {
                        handleFileAutoDownload(downloadUrl, data.filename);
                    }, 100);
                    break;
                
                case "chat_creation":
                    setCurrentSessionId(data.session_id);
                    setResponses([]);
                    break;
                
                case "chat_load":
                    setCurrentSessionId(data.session_id);
                    const new_history = data.history as ChatMessage[];
                    setResponses(new_history);
                    break;
                
                case "auth_success":
                    setUserId(data.user_id);
                    setUserName(data.user_name);
                    setAuthState("success");
                    break;
                
                case "auth_error":
                    setAuthState("error");
                    console.error(data.message)
                    break;
            }
        };

        return () => {
            ws.current?.close();
        };
    }, [url]);



    return {
        // WS connection
        ws,
        currentSessionId,
        authState,
        userId,
        userName,

        // Chat messages
        responses, 
        setResponses
    };
};