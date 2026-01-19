import React, {useRef, useState} from "react";


export const getHightligherProps = () => {
    const [selectedText, setSelectedText] = useState<string>("");
    const [show, setShow] = useState<boolean>(false);
    const bubbleRef = useRef<HTMLDivElement | null>(null);
    const [pos, setPos] = useState<{left:number, top:number}>(
        { left: 12, top: 12 }
    );

    const handleMouseUp = () => {
        const sel = window.getSelection();
        const text = sel?.toString().trim() || "";
        if (!text) return setShow(false);

        setSelectedText(text);

        try {
            const rect = sel!.getRangeAt(0).getBoundingClientRect();
            const container = bubbleRef.current?.getBoundingClientRect();

            if (container) {
                setPos({
                    left: Math.max(8, rect.left - container.left),
                    top: Math.max(8, rect.top - container.top - 36),
                });
            }
            setShow(true);
        } catch {}
    };

    return {selectedText, show, bubbleRef, pos, setShow, handleMouseUp}
}


interface TextHighlighterProps {
    pos: {left: number, top: number};
    selectedText: string;
    setShow: React.Dispatch<React.SetStateAction<boolean>>;
    appendToInput: (text: string) => void;
}

const TextHighlighter: React.FC<TextHighlighterProps> = ({
    pos, 
    selectedText, 
    setShow, 
    appendToInput
}) => {
    return (
        <button
            type="button"
            className="insert-btn"
            style={{ left: pos.left, top: pos.top, position: "absolute" }}
            onClick={() => {
                appendToInput(selectedText)
                setShow(false);
                window.getSelection()?.removeAllRanges();
            }}
        >
            Вставить
        </button>
    )
};

export default TextHighlighter;
