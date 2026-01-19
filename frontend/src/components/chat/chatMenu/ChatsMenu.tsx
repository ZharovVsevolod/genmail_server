import React, {useState} from "react";
import { useChatsMenu } from "../../hooks/useChatsMenu";
import { ChatList } from "./ChatList";
import { CreateChatButton } from "./CreateChatButton";
import { ShowChatsButton } from "./ShowChatsButton";

interface ChatsMenuProps {
    userId: string;
    currentSessionId: string;
    sendCreateNewChatMessage: () => void;
    sendLoadPreviousChatMessage: (session_id: string) => void;
}

const ChatsMenu: React.FC<ChatsMenuProps> = ({
    userId,
    currentSessionId,
    sendCreateNewChatMessage,
    sendLoadPreviousChatMessage,
}) => {
    const [visible, setVisible] = useState(false);
    const openMenu = () => {setVisible(true)};
    const closeMenu = () => {setVisible(false)};

    const {
        chats,
        loading,
        renameChat,
        deleteChat,
    } = useChatsMenu({ userId, visible });

    // Before Menu is visible - we show button to
    // activate this menu
    if (!visible) return (
        <ShowChatsButton
            setMenuVisible={openMenu}
        />
    );

    return (
        <div className="chats-menu-overlay" onClick={closeMenu}>
            <div className="chats-menu" onClick={(e) => e.stopPropagation()}>
                <div className="chats-menu-header">
                    <strong>Диалоги</strong>

                    <button className="close-menu" onClick={closeMenu}>
                        <img src="/delete.png" alt="Close" className="menu-icon" />
                    </button>
                </div>

                <div className="chats-list">
                    <CreateChatButton
                        onCreate={() => {
                            sendCreateNewChatMessage();
                            closeMenu();
                        }}
                    />

                    <ChatList
                        chats={chats}
                        currentSessionId={currentSessionId}
                        loading={loading}
                        onSelect={sendLoadPreviousChatMessage}
                        onRename={renameChat}
                        onDelete={deleteChat}
                    />
                </div>
            </div>
        </div>
    );
};

export default ChatsMenu;
