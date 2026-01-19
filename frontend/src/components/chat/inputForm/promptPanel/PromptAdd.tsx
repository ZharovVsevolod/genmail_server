import React, { RefObject } from "react";

interface PromptAddProps {
    value: string;
    setValue: (v: string) => void;
    onAdd: (text: string) => void;
    inputRef: RefObject<HTMLInputElement | null>;
}

export const PromptAdd: React.FC<PromptAddProps> = ({
    value,
    setValue,
    onAdd,
    inputRef,
}) => {
    const handleAdd = () => {
        const text = value.trim();
        if (!text) return;
        onAdd(text);
        setValue("");
    };

    return (
        <div className="prompts-add">
            <input
                ref={inputRef}
                type="text"
                value={value}
                onChange={(e) => setValue(e.target.value)}
                onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault();
                        handleAdd();
                    }
                }}
                placeholder="Новый промпт"
            />

            <button
                type="button"
                className="icon-btn add-btn"
                onClick={handleAdd}
                aria-label="Add prompt"
            >
                <img src="/add.png" alt="Add" />
            </button>
        </div>
    );
};
