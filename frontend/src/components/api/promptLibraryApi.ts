import { Prompt } from "../common/types";
import config from "../../config/config";

const API_BASE = `http://${config.pageUrl}:${config.portUrl}`

export async function fetchPromptLibrary(userId: string): Promise<Prompt[]> {
    const res = await fetch(
        `${API_BASE}/plibrary/list?user_id=${encodeURIComponent(userId)}`
    );

    if (!res.ok) {
        throw new Error("Failed to load prompt library");
    }

    const data = await res.json();

    return data.prompt_library.map((p: any) => ({
        id: p.prompt_id,
        name: p.name,
        text: p.prompt,
    }));
}

export async function addPrompt(
    userId: string,
    name: string,
    text: string
): Promise<string> {
    const res = await fetch(
        `${API_BASE}/plibrary/add?user_id=${encodeURIComponent(userId)}&name=${encodeURIComponent(
            name
        )}&prompt=${encodeURIComponent(text)}`
    );

    if (!res.ok) {
        throw new Error("Failed to add prompt");
    }

    const data = await res.json();
    return data.prompt_id;
}

export async function deletePrompt(promptId: string): Promise<void> {
    const res = await fetch(
        `${API_BASE}/plibrary/delete?prompt_id=${encodeURIComponent(promptId)}`
    );

    if (!res.ok) {
        throw new Error("Failed to delete prompt");
    }
}

export async function updatePrompt(
    promptId: string,
    name: string,
    text: string
): Promise<void> {
    const res = await fetch(
        `${API_BASE}/plibrary/update?prompt_id=${encodeURIComponent(
            promptId
        )}&name=${encodeURIComponent(name)}&prompt=${encodeURIComponent(text)}`
    );

    if (!res.ok) {
        throw new Error("Failed to update prompt");
    }
}
