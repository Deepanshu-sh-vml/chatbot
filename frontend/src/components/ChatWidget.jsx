import ChatHeader from "./ChatHeader";
import MessageList from "./MessageList";
import ChatInput from "./ChatInput";
import "./ChatWidget.css";

function ChatWidget({ online, messages, loading, onClose, onSend }) {
  return (
    <div className="chat-widget">
      <ChatHeader online={online} onClose={onClose} />
      <MessageList messages={messages} loading={loading} onSend={onSend} />
      <ChatInput onSend={onSend} disabled={loading || !online} />
    </div>
  );
}

export default ChatWidget;