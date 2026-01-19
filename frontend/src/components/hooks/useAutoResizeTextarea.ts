import { useEffect } from "react";

export function useAutoResizeTextarea(
    ref: React.RefObject<HTMLTextAreaElement | null>,
    value: string
) {
    useEffect(() => {
        const el = ref.current;
        if (!el) return;

        el.style.height = "auto";
        el.style.height = `${el.scrollHeight}px`;
    }, [value, ref]);
}
