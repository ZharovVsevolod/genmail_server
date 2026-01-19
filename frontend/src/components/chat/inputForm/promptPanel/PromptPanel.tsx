import React, { RefObject } from "react";
import { Prompt } from "../../../common/types";
import { PromptAdd } from "./PromptAdd";
import { PromptEditor } from "./PromptEditor";
import { PromptList } from "./PromptList";

interface PromptPanelProps {
    prompts: Prompt[];
    editingId: string | null;
    editingText: string;
    newPromptText: string;
    expandedIds: Set<string>;

    setEditingText: (v: string) => void;
    setNewPromptText: (v: string) => void;

    addPrompt: (text: string) => void;
    startEdit: (id: string, text: string) => void;
    updatePrompt: (
        promptId: string,
        text: string
    ) => void;
    cancelEdit: () => void;
    deletePrompt: (id: string) => void;
    toggleExpand: (id: string) => void;

    onApplyPrompt: (text: string) => void;

    newPromptRef: RefObject<HTMLInputElement | null>;
    hasMessages: boolean;
}

export const PromptPanel: React.FC<PromptPanelProps> = (props) => {
    const {
        prompts,
        editingId,
        editingText,
        newPromptText,
        expandedIds,
        setEditingText,
        setNewPromptText,
        addPrompt,
        startEdit,
        updatePrompt,
        cancelEdit,
        deletePrompt,
        toggleExpand,
        onApplyPrompt,
        newPromptRef,
        hasMessages
    } = props;

    return (
        <div
            className={`prompts-panel ${!hasMessages ? 'prompts-panel--bottom' : ''}`}
            onMouseDown={(e) => e.stopPropagation()}
            onClick={() => newPromptRef.current?.focus()}
        >
            <div className="prompts-header">
                <strong>Сохранённые промпты</strong>
            </div>

            {editingId ? (
                <PromptEditor
                    prompt={prompts.find(p => p.id === editingId) ?? null}
                    editingText={editingText}
                    setEditingText={setEditingText}
                    onSave={updatePrompt}
                    onCancel={cancelEdit}
                />
            ) : (
                <>
                    <PromptAdd
                        value={newPromptText}
                        setValue={setNewPromptText}
                        onAdd={addPrompt}
                        inputRef={newPromptRef}
                    />

                    <PromptList
                        prompts={prompts}
                        expandedIds={expandedIds}
                        onEdit={startEdit}
                        onDelete={deletePrompt}
                        onToggleExpand={toggleExpand}
                        onApply={onApplyPrompt}
                    />
                </>
            )}
        </div>
    );
};
