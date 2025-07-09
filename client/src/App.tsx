import React, { useEffect, useState } from 'react';

interface Team {
  id: string;
  name: string;
  key: string;
}

interface Member {
  id: string;
  name: string;
  email: string;
}

interface Label {
  id: string;
  name: string;
  color: string;
}

interface TicketResponse {
  ticket_id?: string;
  linear_ticket?: any;
  linear_team?: any;
  linear_assignee?: any;
  error?: string;
}

const API_BASE = "http://localhost:8000";

function App() {
  const [teams, setTeams] = useState<Team[]>([]);
  const [members, setMembers] = useState<Member[]>([]);
  const [labels, setLabels] = useState<Label[]>([]);
  const [selectedTeam, setSelectedTeam] = useState<string>("");
  const [selectedMember, setSelectedMember] = useState<string>("");
  const [selectedLabels, setSelectedLabels] = useState<string[]>([]);
  const [titulo, setTitulo] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [result, setResult] = useState<TicketResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API_BASE}/linear/teams`)
      .then(res => res.json())
      .then(setTeams)
      .catch(() => setError("Failed to load teams"));
    fetch(`${API_BASE}/linear/labels`)
      .then(res => res.json())
      .then(setLabels)
      .catch(() => setError("Failed to load labels"));
  }, []);

  useEffect(() => {
    if (selectedTeam) {
      fetch(`${API_BASE}/linear/team_members?team_key=${selectedTeam}`)
        .then(res => res.json())
        .then(setMembers)
        .catch(() => setError("Failed to load members"));
    } else {
      setMembers([]);
      setSelectedMember("");
    }
  }, [selectedTeam]);

  const handleLabelChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const options = Array.from(e.target.selectedOptions);
    setSelectedLabels(options.map(opt => opt.value));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch(`${API_BASE}/create_ticket`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          titulo,
          descripcion,
          team_key: selectedTeam,
          assignee_email: members.find(m => m.id === selectedMember)?.email,
          labelIds: selectedLabels,
        }),
      });
      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError("Failed to create ticket");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 500, margin: '2rem auto', padding: 20, border: '1px solid #ccc', borderRadius: 8 }}>
      <h2>Create Linear Ticket</h2>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: 12 }}>
          <label>Team:<br />
            <select value={selectedTeam} onChange={e => setSelectedTeam(e.target.value)} required>
              <option value="">Select a team</option>
              {teams.map(team => (
                <option key={team.id} value={team.key}>{team.name} ({team.key})</option>
              ))}
            </select>
          </label>
        </div>
        <div style={{ marginBottom: 12 }}>
          <label>Assign to:<br />
            <select value={selectedMember} onChange={e => setSelectedMember(e.target.value)} required={!!selectedTeam} disabled={!selectedTeam}>
              <option value="">Select a member</option>
              {members.map(member => (
                <option key={member.id} value={member.id}>{member.name} ({member.email})</option>
              ))}
            </select>
          </label>
        </div>
        <div style={{ marginBottom: 12 }}>
          <label>Labels:<br />
            <select multiple value={selectedLabels} onChange={handleLabelChange} style={{ width: '100%', height: 80 }}>
              {labels.map(label => (
                <option key={label.id} value={label.id}>{label.name}</option>
              ))}
            </select>
          </label>
          <div style={{ marginTop: 4, fontSize: 12 }}>
            {selectedLabels.length > 0 && (
              <span>Selected: {labels.filter(l => selectedLabels.includes(l.id)).map(l => l.name).join(', ')}</span>
            )}
          </div>
        </div>
        <div style={{ marginBottom: 12 }}>
          <label>Title:<br />
            <input value={titulo} onChange={e => setTitulo(e.target.value)} required style={{ width: '100%' }} />
          </label>
        </div>
        <div style={{ marginBottom: 12 }}>
          <label>Description:<br />
            <textarea value={descripcion} onChange={e => setDescripcion(e.target.value)} required style={{ width: '100%' }} rows={4} />
          </label>
        </div>
        <button type="submit" disabled={loading}>{loading ? "Creating..." : "Create Ticket"}</button>
      </form>
      {error && <div style={{ color: 'red', marginTop: 16 }}>{error}</div>}
      {result && (
        <div style={{ marginTop: 16 }}>
          <h4>Result:</h4>
          <pre style={{ background: '#f6f6f6', padding: 10, borderRadius: 4 }}>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default App;
