import React from "react";

interface ShowChatsButtonProps {
    setMenuVisible: () => void;
}


export const ShowChatsButton: React.FC<ShowChatsButtonProps> = ({
    setMenuVisible
}) => (
    <button 
        className="menu-btn" 
        onClick={() => setMenuVisible()}
        title="Открыть диалоги"
    >
        <img src="/menu.png" alt="menu" className="menu-icon" />
    </button>
);
