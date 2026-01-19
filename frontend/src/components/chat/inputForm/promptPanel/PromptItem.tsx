import React from "react";
import { Prompt } from "../../../common/types";

interface PromptItemProps {
    prompt: Prompt;
    isExpanded: boolean;
    onEdit: (id: string, text: string) => void;
    onDelete: (id: string) => void;
    onToggleExpand: (id: string) => void;
    onApply: (text: string) => void;
}

export const PromptItem: React.FC<PromptItemProps> = ({
    prompt,
    isExpanded,
    onEdit,
    onDelete,
    onToggleExpand,
    onApply,
}) => {
    const isLong = prompt.text.length > 120;
    const showTruncated = isLong && !isExpanded;

    return (
        <div className="prompt-item">
            <div
                className={`prompt-text ${showTruncated ? "truncated" : ""}`}
                title={prompt.text}
                onClick={() => {
                    if (isLong) onToggleExpand(prompt.id);
                }}
                style={{ cursor: isLong ? "pointer" : "default" }}
            >
                {showTruncated
                ? `${prompt.text.slice(0, 120)}...`
                : prompt.text}
            </div>

            <div className="prompt-actions">
                <div className="prompt-left-actions">
                    <button
                        type="button"
                        className="icon-btn"
                        onClick={() => onEdit(prompt.id, prompt.text)}
                        aria-label="Edit prompt"
                    >
                        <img src="/edit.png" alt="Edit" />
                    </button>

                    <button
                        type="button"
                        className="icon-btn"
                        onClick={() => onDelete(prompt.id)}
                        aria-label="Delete prompt"
                    >
                        <img src="/delete.png" alt="Delete" />
                    </button>
                </div>

                <div className="prompt-right-actions">
                    <button
                        type="button"
                        className="apply-btn"
                        onClick={() => onApply(prompt.text)}
                    >
                        Применить
                    </button>
                </div>
            </div>
        </div>
    );
};
