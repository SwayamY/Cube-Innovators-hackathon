import React, { useState, useEffect } from "react";
import { v4 as uuidv4 } from "uuid"; // For unique user IDs

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [userId, setUserId] = useState(""); // Unique session ID

  useEffect(() => {
    // Generate a new user session ID when component loads
    setUserId(uuidv4());
  }, []);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { sender: "You", text: input };
    setMessages([...messages, userMessage]);
    setInput("");

    try {
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId, user_message: input }), // Added user_id
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();
      setMessages((prev) => [...prev, { sender: "Bot", text: data.reply }]);

    } catch (error) {
      console.error("Error:", error);
      setMessages((prev) => [...prev, { sender: "Bot", text: "Error connecting to server." }]);
    }
  };

  return (
    <div style={{ maxWidth: "600px", margin: "auto", padding: "20px", textAlign: "center" }}>
      <h2>AI Career Predictor Chat</h2>
      <div style={{ border: "1px solid #ccc", padding: "10px", height: "300px", overflowY: "auto" }}>
        {messages.map((msg, index) => (
          <p key={index} style={{ textAlign: msg.sender === "You" ? "right" : "left" }}>
            <strong>{msg.sender}:</strong> {msg.text}
          </p>
        ))}
      </div>
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Type your response..."
        style={{ width: "80%", padding: "5px", marginTop: "10px" }}
      />
      <button onClick={sendMessage} style={{ marginLeft: "10px", padding: "5px" }}>Send</button>
    </div>
  );
}

export default App;
