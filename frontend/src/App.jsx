import { useState, useEffect } from "react";
import ChatButton from "./components/ChatButton";
import ChatWidget from "./components/ChatWidget";
import * as api from "./api";
import "./styles.css";

function App() {
  // ---- STATE (the app's memory) ----
  const [isOpen, setIsOpen] = useState(false);    // chat open/closed
  const [online, setOnline] = useState(false);    // backend reachable?
  const [messages, setMessages] = useState([]);   // chat history
  const [loading, setLoading] = useState(false);  // waiting for reply?

  // ---- On mount: check if backend is alive ----
  useEffect(() => {
    api.getHealth()
      .then((h) => setOnline(h.status === "ok"))
      .catch(() => setOnline(false));
  }, []);

  // ---- LOGIC: send a ticket to the backend ----
  async function handleSend(ticketText) {
    // 1. Add the user's message immediately
    setMessages((prev) => [
      ...prev,
      { id: Date.now(), role: "user", text: ticketText },
    ]);
    setLoading(true);

    try {
      // 2. Call the backend (api.js does the HTTP work)
      const result = await api.sendTicket(ticketText);

      // 3. Handle manual mode (no API key) gracefully
      if (result.mode === "manual") {
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now() + 1,
            role: "bot",
            text: "⚙️ The assistant isn't connected to an LLM yet (manual mode). Please add an API key to enable automatic replies.",
            behavior: "escalate",
          },
        ]);
      } else {
        // 4. Add the bot's final reply (NESTED in stage4!)
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now() + 1,
            role: "bot",
            text: result.final_reply || "No reply returned.",
            behavior: result.stage3?.behavior,
          },
        ]);
      }
    } catch (err) {
      // 5. Show errors as a bot message instead of crashing
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: "bot",
          text: "⚠️ " + err.message,
          isError: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  // ---- RENDER: button when closed, widget when open ----
  return (
    <div className="page">
      {isOpen ? (
        <>
          <div className="chat-overlay" onClick={() => setIsOpen(false)} />
          <ChatWidget
            online={online}
            messages={messages}
            loading={loading}
            onClose={() => setIsOpen(false)}
            onSend={handleSend}
          />
        </>
      ) : (
        <ChatButton onOpen={() => setIsOpen(true)} />
      )}
    </div>
  );
}

export default App;