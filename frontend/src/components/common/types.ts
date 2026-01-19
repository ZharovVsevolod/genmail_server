// One chat message stored in React state
export interface ChatMessage {
    id: string;
    sender: string;
    message: string;
    message_id?: string; // what id message has in database
    rating?: RatingType;
};

export type RatingType = "like" | "dislike" | null;

export type AuthState = null | "success" | "error";

// Prompt Library
export interface Prompt {
    id: string;
    name?: string;
    text: string;
};

// List of user's chats
export interface ChatItem {
    session_id: string;
    name: string;
};


// WebSocket types
// Incoming events from backend
type AuthSuccessEvent = {
    event: "auth_success";
    message: string;
    state: string;
    user_id: string;
    user_name: string;
};
type AuthErrorEvent = {
    event: "auth_error";
    state: string;
    message: string;
};
type DocumentExtractionEvent = {
    event: "document_extraction";
    run_id: string;
    name: string;
};
type DocumentSummarizationEvent = {
    event: "document_summarization";
    run_id: string;
    name: string;
};
type OnParserStartEvent = {
     event: "on_parser_start";
    run_id: string;
    name: string;
};
type OnThinkingStartEvent = {
    event: "thinking_start";
    run_id: string;
    name: string;
};
type OnThinkingEndEvent = {
    event: "thinking_end";
    run_id: string;
    name: string;
};
type OnParserStreamEvent = {
    event: "on_parser_stream";
    run_id: string;
    name: string;
    data: { 
        chunk: string 
    };
};
type OnGenerationEndEvent = {
    event: "on_generation_end";
    run_id: string;
    name: string;
    message_id: string;
};
type SummaryEvent = {
    event: "summary";
    run_id: string;
    name: string;
    data: Record<string, string>;
};
type DonwloadEvent = {
    event: "download";
    run_id: string;
    name: string;
    filename: string;
};
type ChatCreationEvent = {
    event: "chat_creation";
    session_id: string;
};
type ChatLoadEvent = {
    event: "chat_load";
    session_id: string;
    history: [
        {
            id: string;
            sender: string;
            message: string;
            message_id: string;
            rating: string | null;
        }
    ];
};

export type WSIncomingEvent = 
    AuthSuccessEvent |
    AuthErrorEvent | 
    DocumentExtractionEvent |
    DocumentSummarizationEvent |
    OnParserStartEvent |
    OnThinkingStartEvent | 
    OnThinkingEndEvent |
    OnParserStreamEvent |
    OnGenerationEndEvent |
    SummaryEvent | 
    DonwloadEvent |
    ChatCreationEvent | 
    ChatLoadEvent;


// Outgoing message shape
//
// action filed could be:
// - SUMMARY
// - QUERY
// - FORMALIZE
// - CREATE
// - RATE
// - AUTH
//
export interface WSOutgoingMessage {
    action: string;
    message?: string; // for QUERY action
    message_id?: string; // for FORMALIZE and RATE action
    rating?: RatingType; // for RATE action
    user_id?: string; // for AUTH action
    user_password?: string; // for AUTH action
    session_id?: string; // For LOAD_CHAT action
};