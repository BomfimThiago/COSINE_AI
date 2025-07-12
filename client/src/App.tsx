import React, { useState, useRef, useEffect } from "react";

const API_BASE = "http://localhost:8000";

type Message = {
  sender: "user" | "system";
  text: string;
};

type TicketResult = {
  tickets: {
    description: string;
    label: string;
    assignee: string;
    solution: string;
    linear_ticket: any;
  }[];
};

function App() {
  const [messages, setMessages] = useState<Message[]>([
    {
      sender: "system",
      text: "¡Hola! Describe en lenguaje natural tu idea de proyecto o tarea, y crearé los tickets automáticamente.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    const userMsg = input.trim();
    if (!userMsg) return;

    setMessages((msgs) => [...msgs, { sender: "user", text: userMsg }]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/chat_orchestrate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMsg }),
      });
      const data: TicketResult = await res.json();

      if (data && data.tickets && data.tickets.length > 0) {
        data.tickets.forEach((ticket, idx) => {
          setMessages((msgs) => [
            ...msgs,
            {
              sender: "system",
              text:
                `🎟️ Ticket #${idx + 1}:\n` +
                `Descripción: ${ticket.description}\n` +
                `Label: ${ticket.label}\n` +
                `Asignado a: ${ticket.assignee}\n` +
                `Solución Inicial:\n${ticket.solution}` +
                (ticket.linear_ticket
                  ? `\n\nTicket creado en Linear: ${ticket.linear_ticket.identifier || ticket.linear_ticket.id}`
                  : ""),
            },
          ]);
        });
      } else {
        setMessages((msgs) => [
          ...msgs,
          { sender: "system", text: "No se pudieron generar tickets desde tu mensaje." },
        ]);
      }
    } catch (err) {
      setMessages((msgs) => [
        ...msgs,
        { sender: "system", text: "Ocurrió un error al procesar tu solicitud." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        maxWidth: 600,
        margin: "2rem auto",
        background: "#fff",
        borderRadius: 12,
        boxShadow: "0 2px 16px #0001",
        padding: 24,
        minHeight: 500,
        display: "flex",
        flexDirection: "column",
      }}
    >
      <h2 style={{ marginBottom: 16, textAlign: "center" }}>
        🤖 Chat Orquestador de Tickets Linear
      </h2>
      <div
        style={{
          flex: 1,
          overflowY: "auto",
          background: "#f7f7fa",
          borderRadius: 8,
          padding: 16,
          marginBottom: 12,
          minHeight: 320,
        }}
      >
        {messages.map((msg, i) => (
          <div
            key={i}
            style={{
              textAlign: msg.sender === "user" ? "right" : "left",
              marginBottom: 12,
              whiteSpace: "pre-wrap",
            }}
          >
            <span
              style={{
                display: "inline-block",
                padding: "10px 16px",
                borderRadius: 16,
                background: msg.sender === "user" ? "#e0e7ff" : "#f1f5f9",
                color: "#20223a",
                maxWidth: "80%",
              }}
            >
              {msg.text}
            </span>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      <form onSubmit={handleSend} style={{ display: "flex", gap: 8 }}>
        <input
          type="text"
          placeholder="Describe tu idea aquí..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          style={{
            flex: 1,
            padding: 12,
            borderRadius: 8,
            border: "1px solid #ccc",
            fontSize: 16,
          }}
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          style={{
            background: "#6366f1",
            color: "#fff",
            border: "none",
            borderRadius: 8,
            padding: "0 18px",
            fontWeight: 600,
            fontSize: 16,
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          {loading ? "..." : "Enviar"}
        </button>
      </form>
      <div style={{ fontSize: 12, color: "#999", marginTop: 8, textAlign: "center" }}>
        Escribe una idea como: "Quiero una app con login y visualización de métricas"
      </div>
    </div>
  );
}

export default App;
