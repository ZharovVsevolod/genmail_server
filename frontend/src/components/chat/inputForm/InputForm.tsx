import React, { useRef, useState } from "react";
import { usePrompts } from "../../hooks/usePrompts";
import { ChatInput } from "./ChatInput";
import { UploadButton } from "./UploadButton";
import { PromptPanel } from "./promptPanel/PromptPanel";
import { useOutsideClick } from "../../hooks/useOutsideClick";
import { useAutoResizeTextarea } from "../../hooks/useAutoResizeTextarea";
import InitMessage from "./InitMessage";

interface InputFormProps {
    input: string;
    setInput: React.Dispatch<React.SetStateAction<string>>;
    onSend: (message: string) => void;
    onUpload: () => void;
    userId: string | null;
    userName: string | null;
    hasMessages: boolean;
}

const InputForm: React.FC<InputFormProps> = ({
    input,
    setInput,
    onSend,
    onUpload,
    userId,
    userName,
    hasMessages
}) => {
    const inputRef = useRef<HTMLTextAreaElement>(null);
    const newPromptRef = useRef<HTMLInputElement>(null);
    const wrapperRef = useRef<HTMLDivElement>(null);

    const [showPrompts, setShowPrompts] = useState(false);

    const promptHook = usePrompts(userId);

    // Form submit
    const handleSubmit = (e?: React.FormEvent) => {
        e?.preventDefault();
        const message = input.trim();
        if (!message) return;

        onSend(message);
        setInput("");
        inputRef.current?.focus();
    };

    // Show and hide PromptPanel
    useOutsideClick(wrapperRef, () => setShowPrompts(false));

    // Resize TextArea
    useAutoResizeTextarea(inputRef, input);


    /* -------------------- render -------------------- */
    return (
        <form 
            onSubmit={(e) => {
                e.preventDefault(); 
                handleSubmit();
            }}
            className={`input-form ${hasMessages ? "input-form--bottom" : "input-form--center"}`}
        >
            {!hasMessages && 
                <InitMessage
                    userName={userName}
                />
            }

            <div
                ref={wrapperRef}
                className="input-with-prompts"
                onMouseEnter={() => setShowPrompts(true)}
            >
                <UploadButton onClick={onUpload} />

                <ChatInput
                    value={input}
                    onChange={setInput}
                    onSubmit={handleSubmit}
                    onFocus={() => setShowPrompts(true)}
                    inputRef={inputRef}
                />

                {showPrompts && (
                <PromptPanel
                    {...promptHook}
                    newPromptRef={newPromptRef}
                    onApplyPrompt={(text) => {
                        setInput(text);
                        setShowPrompts(false);
                        inputRef.current?.focus();
                    }}
                    hasMessages={hasMessages}
                />
                )}

                <button type="submit" aria-label="Send">
                    <img src="/send.png" alt="Send" />
                </button>
            </div>            
        </form>
    );
};

export default InputForm;
