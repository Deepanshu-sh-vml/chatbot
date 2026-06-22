// Props:
//   onOpen = function to open the widget (event UP ⬆️)
import "./ChatButton.css";
function ChatButton({ onOpen }) {
  return (
    <button className="chat-fab" onClick={onOpen} aria-label="Open chat">
      💬
    </button>
  );
}

export default ChatButton;