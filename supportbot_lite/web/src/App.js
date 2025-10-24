// web/src/App.js
import React, { useState } from "react";
import ChatWindow from "./components/ChatWindow";
import { uploadCSV } from "./api";

export default function App() {
  const [uploading, setUploading] = useState(false);
  const [file, setFile] = useState(null);
  const [uploaded, setUploaded] = useState(false);

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    try {
      const res = await uploadCSV(file);
      alert(res.message);
      setUploaded(true);
    } catch (e) {
      alert("Upload failed: " + e.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="app">
      <h1>SupportBot Lite 🤖</h1>

      <div className="upload-box">
        <input
          type="file"
          accept=".csv"
          onChange={(e) => setFile(e.target.files[0])}
        />
        <button onClick={handleUpload} disabled={!file || uploading}>
          {uploading ? "Uploading..." : "Upload FAQ CSV"}
        </button>
      </div>

      {uploaded && <ChatWindow />}
    </div>
  );
}
