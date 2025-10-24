// web/src/components/ChatWindow.js
import React, { useState } from "react";
import { askQuestion } from "../api";

export default function ChatWindow() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;
    setLoading(true);

    const userMessage = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);

    try {
      const res = await askQuestion(input);
      const botMessage = {
        sender: res.source === "faq" ? "faq" : "llm",
        text: res.answer,
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { sender: "system", text: "Error: " + err.message },
      ]);
    } finally {
      setInput("");
      setLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <h2>SupportBot Lite 💬</h2>
      <div className="chat-box">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`message ${msg.sender}`}
            style={{
              alignSelf: msg.sender === "user" ? "flex-end" : "flex-start",
              backgroundColor:
                msg.sender === "user"
                  ? "#DCF8C6"
                  : msg.sender === "faq"
                  ? "#E6F3FF"
                  : msg.sender === "llm"
                  ? "#FFE6E6"
                  : "#EEE",
            }}
          >
            <p>{msg.text}</p>
          </div>
        ))}
      </div>

      <div className="chat-input">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question..."
        />
        <button onClick={handleSend} disabled={loading}>
          {loading ? "..." : "Send"}
        </button>
      </div>
    </div>
  );
}
