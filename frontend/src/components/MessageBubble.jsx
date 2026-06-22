import "./MessageBubble.css";// A single chat message bubble. // Props (data coming DOWN ⬇️): // message = { // role: "user" | "bot", // text: "...", // behavior?: "grounded_reply" | "grounded_denial" | "escalate", // isError?: boolean // }

function MessageBubble({ message })
{ const isUser = message.role === "user";

// Pick a badge color class based on the pipeline behavior (optional flair) function badgeClass(behavior) { if (behavior === "grounded_reply") return "badge badge-green"; if (behavior === "grounded_denial") return "badge badge-amber"; if (behavior === "escalate") return "badge badge-orange"; return ""; }

return ( <div className={isUser ? "bubble bubble-user" : "bubble bubble-bot"}> {/* Show a small badge on bot messages that have a behavior */} {!isUser && message.behavior && ( <span className={badgeClass(message.behavior)}>{message.behavior.replace("_", " ")}</span> )}

  <div className="bubble-text">{message.text}</div>
</div>
); }

export default MessageBubble;

