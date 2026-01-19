import React, { useState, useEffect } from "react";

interface DropdownInfoProps {
    menuVisible: boolean;
    handleOpenMenu: () => void;
};

export const DropdownInfo: React.FC<DropdownInfoProps> = ({
    menuVisible, 
    handleOpenMenu
}) => {
    if (menuVisible) return null;

    const [showInfoDropdown, setShowInfoDropdown] = useState(false);

    // Close info dropdown when clicking outside
    useEffect(() => {
        if (!showInfoDropdown) return;
        const handleClickOutside = () => {
            setShowInfoDropdown(false);
        };
        document.addEventListener('click', handleClickOutside);
        return () => document.removeEventListener('click', handleClickOutside);
    }, [showInfoDropdown]);

    return (
        <>
            <div
                className="menu-strip"
                onClick={handleOpenMenu}
                aria-label="Открыть диалоги"
                role="button"
            />

            <div className="info-btn-hidden-wrapper">
                <button
                    className="info-btn-hidden"
                    aria-label="Помощь по сервису"
                    onClick={(e) => {
                        e.stopPropagation();
                        setShowInfoDropdown(!showInfoDropdown);
                    }}
                >
                    <img src="/info.png" alt="Info" />
                </button>
                
                {showInfoDropdown && (
                    <div className="info-dropdown info-dropdown--hidden" onClick={(e) => e.stopPropagation()}>
                        <button className="info-dropdown-item">О сервисе</button>
                        <button className="info-dropdown-item">Документация</button>
                        <button className="info-dropdown-item">Поддержка</button>
                    </div>
                )}
            </div>
        </>
    )
};