import { useEffect } from "react";

export function useOutsideClick(
    ref: React.RefObject<HTMLElement | null>,
    onOutside: () => void
) {
    useEffect(() => {
        const handleMouseDown = (e: MouseEvent) => {
            if (!ref.current) return;
            if (!ref.current.contains(e.target as Node)) {
                onOutside();
            }
        };

        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.key === "Escape") {
                onOutside();
            }
        };

        document.addEventListener("mousedown", handleMouseDown);
        document.addEventListener("keydown", handleKeyDown);

        return () => {
            document.removeEventListener("mousedown", handleMouseDown);
            document.removeEventListener("keydown", handleKeyDown);
        };
    }, [ref, onOutside]);
}
