import { useEffect, useState, useRef } from "react";
import { Prompt } from "../common/types";
import {v4 as uuidv4} from 'uuid';

import { 
    fetchPromptLibrary,
    addPrompt as apiAddPrompt,
    deletePrompt as apiDeletePrompt,
    updatePrompt as apiUpdatePrompt
} from "../api/promptLibraryApi";


export function usePrompts(userId: string | null) {
    const [prompts, setPrompts] = useState<Prompt[]>([]);
    const [editingId, setEditingId] = useState<string | null>(null);
    const [editingText, setEditingText] = useState("");
    const [newPromptText, setNewPromptText] = useState("");
    const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());

    // prevents save-before-load overwrite
    const initializedRef = useRef(false);

    /* -------------------- persistence -------------------- */

    // Load prompt library
    useEffect(() => {
        // No userId yet - no loading prompt library
        if (!userId) return;

        const loadPrompts = async () => {
            try {
                const data = await fetchPromptLibrary(userId);
                setPrompts(data);
                initializedRef.current = true;

                console.log("Load prompt library for user:", userId);
            } 
            catch (err) {
                console.warn("Failed to load prompts:", err);
            }
        };

        loadPrompts();
    }, [userId]);


    /* -------------------- actions -------------------- */

    const addPrompt = async (text: string) => {
        // For name - name just a truncated text
        const name = text.split("\n")[0].slice(0, 50);

        if (!userId) return;

        const tempId = uuidv4();

        // optimistic update
        setPrompts((p) => [{ id: tempId, name, text }, ...p]);

        try {
            const realId = await apiAddPrompt(userId, name, text);
            setPrompts((p) =>
                p.map((it) => (it.id === tempId ? { ...it, id: realId } : it))
            );
        } 
        catch (err) {
            console.warn("Failed to add prompt:", err);
            setPrompts((p) => p.filter((it) => it.id !== tempId));
        }
    };

    const startEdit = (id: string, text: string) => {
        setEditingId(id);
        setEditingText(text);
    };

    const updatePrompt = async (
        id: string,
        text: string
    ) => {
        // For name - name just a truncated text
        const name = text.split("\n")[0].slice(0, 50);

        const prev = prompts;

        // optimistic update
        setPrompts(p =>
            p.map(pr =>
                pr.id === id ? { ...pr, text, name } : pr
            )
        );

        try {
            await apiUpdatePrompt(id, name, text);
            setEditingId(null);
            setEditingText("");
        
        } catch (err) {
            console.warn("Failed to update prompt:", err);
            setPrompts(prev); // rollback
        }
    };

    const cancelEdit = () => {
        setEditingId(null);
        setEditingText("");
    };

    const deletePrompt = async (promptId: string) => {
        const prev = prompts;
        setPrompts((p) => p.filter((it) => it.id !== promptId));

        try {
            await apiDeletePrompt(promptId);
        } 
        catch (err) {
            console.warn("Failed to delete prompt:", err);
            setPrompts(prev); // rollback
        }
    };

    const toggleExpand = (id: string) => {
        setExpandedIds(prev => {
            const copy = new Set(prev);
            copy.has(id) ? copy.delete(id) : copy.add(id);
            return copy;
        });
    };

    /* -------------------- exposed API -------------------- */

    return {
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
    };
}
