// Props:
//   online  = bool (data DOWN ⬇️)
//   onClose = function to close the widget (event UP ⬆️)

import "./ChatHeader.css";
function ChatHeader({ online, onClose }) {
  return (
    <div className="chat-header">
      <div className="header-left">
        <div className="header-avatar">🎯</div>
        <div>
          <div className="header-title">Northwind Co-pilot</div>
          <div className="header-status">
            <span className={online ? "dot dot-on" : "dot dot-off"} />
            {online ? "Online" : "Offline"}
          </div>
        </div>
      </div>

      {/* Clicking ✕ tells the parent to close (event UP) */}
      <button className="header-close" onClick={onClose} aria-label="Close chat">
        ✕
      </button>
    </div>
  );
}

export default ChatHeader;