import { useState } from "react";
import "./ChatInput.css";
// Props:
//   onSend  = function(text) — report the ticket UP ⬆️
//   disabled = bool (data DOWN ⬇️) — disable while loading/offline

function ChatInput({ onSend, disabled }) {
  // This component owns its OWN small state: the current text being typed.
  const [text, setText] = useState("");

  function handleSubmit() {
    const trimmed = text.trim();
    if (!trimmed) return;
    onSend(trimmed);   // report UP to the parent
    setText("");       // clear the box after sending
  }

  function handleKeyDown(e) {
    // Enter sends; Shift+Enter makes a new line
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }

  return (
    <div className="chat-input">
      <textarea
        placeholder="Type a support ticket…"
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        rows={1}
      />
      <button
        className="send-btn"
        onClick={handleSubmit}
        disabled={disabled || !text.trim()}
        aria-label="Send"
      >
        ➤
      </button>
    </div>
  );
}

export default ChatInput;