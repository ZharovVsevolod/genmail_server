import React from "react";
import { Prompt } from "../../../common/types";
import { PromptItem } from "./PromptItem";

interface PromptListProps {
    prompts: Prompt[];
    expandedIds: Set<string>;
    onEdit: (id: string, text: string) => void;
    onDelete: (id: string) => void;
    onToggleExpand: (id: string) => void;
    onApply: (text: string) => void;
}

export const PromptList: React.FC<PromptListProps> = ({
    prompts,
    expandedIds,
    onEdit,
    onDelete,
    onToggleExpand,
    onApply,
}) => {
    if (prompts.length === 0) {
        return <div className="prompts-empty">Нет промптов</div>;
    }

    return (
        <div className="prompts-list">
            {prompts.map((p) => (
                <PromptItem
                    key={p.id}
                    prompt={p}
                    isExpanded={expandedIds.has(p.id)}
                    onEdit={onEdit}
                    onDelete={onDelete}
                    onToggleExpand={onToggleExpand}
                    onApply={onApply}
                />
            ))}
        </div>
    );
};
