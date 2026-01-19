import React from "react";

interface UploadButtonProps {
    onClick: () => void;
}

export const UploadButton: React.FC<UploadButtonProps> = ({ onClick }) => (
    <button
        type="button"
        className="upload-button icon-btn"
        onClick={onClick}
        aria-label="Upload files"
    >
        <img src="/upload.png" alt="Upload" />
    </button>
);
