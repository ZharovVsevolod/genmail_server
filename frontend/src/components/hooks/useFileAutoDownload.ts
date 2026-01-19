const handleFileAutoDownload = (url: string, filename: string) => {
    try {
        const a = document.createElement("a");
        a.href = url;
        a.download = filename;
        a.style.display = "none";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    } 
    catch (err) {
        console.error("Auto-download failed:", err);
    }
};

export default handleFileAutoDownload;