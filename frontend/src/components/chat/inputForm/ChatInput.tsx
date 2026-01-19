import React from "react";

interface ChatInputProps {
    value: string;
    onChange: (value: string) => void;
    onSubmit: () => void;
    onFocus?: () => void;
    inputRef: React.RefObject<HTMLTextAreaElement | null>;
}

export const ChatInput: React.FC<ChatInputProps> = ({
    value,
    onChange,
    onSubmit,
    onFocus,
    inputRef,
}) => {
    return (
        <textarea
            ref={inputRef}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onFocus={onFocus}
            onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    onSubmit();
                }
            }}
            placeholder="Напишите свой запрос..."
            id="chat-input"
        />
    );
};
