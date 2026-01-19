import React, {useState} from "react";
import { RatingType } from "../../common/types";

interface MessageRatingProps {
    message_id: string;
    currentRating: RatingType;
    onRate: (message_id: string, rating: RatingType) => void;
}

const MessageRating: React.FC<MessageRatingProps> = ({
    message_id,
    currentRating,
    onRate,
}) => {
    const [rating, setRating] = useState<RatingType>(currentRating)

    const toggle = (nextRating: RatingType) => {
        // Handle event when user wants to clear rating
        // when presses rating button that was already pressed
        let newRating = nextRating;
        // If the same rating was sent - clear
        if (newRating == rating) {
            newRating = null;
        }
        
        // Change message current rating
        setRating(newRating);
        // Set new rating to backend
        onRate(message_id, newRating);
    };


    return (
    <>
        <button
            className={`rate-btn like-btn ${rating === "like" ? "rated" : ""}`}
            onClick={() => toggle("like")}
            title="Лайк"
        >
            <img src="/like.png" alt="Лайк" width="20" height="20" />
        </button>

        <button
            className={`rate-btn dislike-btn ${rating === "dislike" ? "rated" : ""}`}
            onClick={() => toggle("dislike")}
            title="Дизлайк"
        >
            <img src="/like.png" alt="Дизлайк" width="20" height="20" className="flipped" />
        </button>
    </>
    );
};

export default MessageRating;
