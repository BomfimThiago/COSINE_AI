import React, { useState, useRef, useEffect } from "react";

// Simple styling for the chat interface
const styles = {
  container: {
    display: "flex",
    flexDirection: "column" as const,
    justifyContent: "center",
    alignItems: "center",
    minHeight: "100vh",
    background: "#f6f8fa",
    fontFamily: "Inter, sans-serif",
  },
  chatBox: {
    background: "#fff",
    borderRadius: "16px",
    boxShadow: "0 4px 24px rgba(60, 91, 158, 0.1)",
    width: "100%",
    maxWidth: "500px",
    minHeight: "480px",
    display: "flex",
    flexDirection: "column" as const,
    padding: "24px 18px 16px 18px",
    gap: "16px",
  },
  messages: {
    flex: 1,
    overflowY: "auto" as const,
    paddingBottom: "12px",
    display: "flex",
    flexDirection: "column" as const,
    gap: "12px",
  },
  inputRow: {
    display: "flex",
    gap: "10px",
    alignItems: "center",
    marginTop: "8px",
  },
  input: {
    flex: 1,
    padding: "12px 16px",
    borderRadius: "8px",
    border: "1px solid #e1e4e8",
    fontSize: "1rem",
    outline: "none",
  },
  button: {
    background: "linear-gradient(90deg, #2a62f7, #81e0fa)",
    color: "#fff",
    border: "none",
    borderRadius: "8px",
    padding: "10px 18px",
    fontWeight: 600,
    fontSize: "1rem",
    cursor: "pointer",
    transition: "background 0.2s",
  },
  userMsg: {
    alignSelf: "flex-end",
    background: "#2a62f7",
    color: "#fff",
    borderRadius: "12px 12px 4px 12px",
    padding: "12px 18px",
    maxWidth: "75%",
    fontSize: "1rem",
    boxShadow: "0 2px 8px rgba(60,91,158,0.08)",
  },
  agentMsg: {
    alignSelf: "flex-start",
    background: "#f1f4fb",
    color: "#222",
    borderRadius: "12px 12px 12px 4px",
    padding: "12px 18px",
    maxWidth: "75%",
    fontSize: "1rem",
    boxShadow: "0 2px 8px rgba(60,91,158,0.05)",
    borderLeft: "4px solid #2a62f7",
  },
  header: {
    textAlign: "center" as const,
    marginBottom: "12px",
    fontWeight: 700,
    fontSize: "1.45rem",
    color: "#2a62f7",
    letterSpacing: "0.5px",
  },
  subheader: {
    textAlign: "center" as const,
    marginBottom: "16px",
    color: "#777",
    fontSize: "1rem",
    fontWeight: 400,
  }
};

type Message = {
  sender: "user" | "agent";
  text: string;
};

const initialMsg: Message = {
  sender: "agent",
  text: "¡Hola! Cuéntame en lenguaje natural la idea general de tu proyecto (por ejemplo: 'Quiero una app con login y visualización de métricas') y te ayudaré a crear los tickets de trabajo.",
};

export default function App() {
  const [messages, setMessages] = useState<Message[]>([initialMsg]);
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  // Auto-scroll to bottom when messages update
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed) return;

    // Add user message
    setMessages((msgs) => [
      ...msgs,
      { sender: "user", text: trimmed },
    ]);
    setInput("");

    // Simulate agent/orchestrator response (to be replaced with backend call)
    setTimeout(() => {
      setMessages((msgs) => [
        ...msgs,
        {
          sender: "agent",
          text:
            "Procesando tu idea... (Aquí pronto verás cómo se desglosa en tickets con etiquetas y asignaciones automáticas).",
        },
      ]);
    }, 1100);
  };

  const handleInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.chatBox}>
        <div style={styles.header}>Cosine Genie · Conversational Ticketing</div>
        <div style={styles.subheader}>
          Transforma tus ideas en tickets de trabajo automáticamente.
        </div>
        <div style={styles.messages}>
          {messages.map((msg, i) => (
            <div
              key={i}
              style={msg.sender === "user" ? styles.userMsg : styles.agentMsg}
            >
              {msg.text}
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
        <div style={styles.inputRow}>
          <input
            type="text"
            style={styles.input}
            placeholder="Escribe tu idea de proyecto..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleInputKeyDown}
            autoFocus
            maxLength={400}
            aria-label="Escribe tu mensaje"
          />
          <button
            style={styles.button}
            onClick={handleSend}
            disabled={!input.trim()}
            aria-label="Enviar mensaje"
          >
            Enviar
          </button>
        </div>
      </div>
    </div>
  );
}