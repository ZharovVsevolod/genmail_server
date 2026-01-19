import React from "react";
import { Prompt } from "../../../common/types";

interface PromptEditorProps {
    prompt: Prompt | null;
    editingText: string;
    setEditingText: (v: string) => void;
    onSave: (id: string, text: string) => void;
    onCancel: () => void;
}

export const PromptEditor: React.FC<PromptEditorProps> = ({
    prompt,
    editingText,
    setEditingText,
    onSave,
    onCancel,
}) => {
    if (!prompt) {
        return <div className="prompts-empty">Промпт не найден</div>;
    }

    return (
        <div className="prompts-list">
            <div className="prompt-item">
                <textarea
                    value={editingText}
                    onChange={(e) => setEditingText(e.target.value)}
                    rows={4}
                />
                <div className="prompt-actions">
                    <div className="prompt-left-actions">
                        <button type="button" onClick={() => onSave(prompt.id, editingText)}>
                            Save
                        </button>
                        
                        <button type="button" onClick={onCancel}>
                            Cancel
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};
