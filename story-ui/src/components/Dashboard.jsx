import React, { useState, useEffect } from 'react';
import { fetchProjects } from '../services/api';

function Dashboard({ token, onCreateNew, onViewDetails }) {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadProjects = async () => {
      try {
        const data = await fetchProjects();
        setProjects(data || []);
      } catch (err) {
        setError('Could not load active projects.');
      } finally {
        setLoading(false);
      }
    };
    loadProjects();
  }, [token]);

  const escapeHtml = (unsafe) => {
    if (!unsafe) return '';
    return unsafe
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  };

  return (
    <section id="view-dashboard" className="view active">
      <div className="dashboard-header">
        <h2>My Stories</h2>
        <button onClick={onCreateNew} className="primary-btn small-btn">
          <span>+ Create New Story</span>
          <div className="btn-glow"></div>
        </button>
      </div>

      {loading && <div className="spinner-container"><div className="spinner"></div><p>Loading projects...</p></div>}
      {error && <p className="error-msg">{error}</p>}

      {!loading && !error && (
        <div className="projects-grid">
          {projects.length === 0 ? (
            <p style={{ gridColumn: '1/-1', textAlign: 'center', color: '#a1a1aa' }}>
              No stories found. Create your first one!
            </p>
          ) : (
            projects.map((project) => (
              <div 
                key={project.id} 
                className="scene-card" 
                onClick={() => onViewDetails(project)}
              >
                <div className="scene-number">{project.status.toUpperCase()}</div>
                <div className="scene-desc" style={{ fontWeight: 600, fontSize: '1.1rem', marginBottom: '0.5rem', color: 'white' }}>
                  {escapeHtml(project.topic_prompt)}
                </div>
                <div style={{ fontSize: '0.8rem', color: '#a1a1aa' }}>
                  {new Date(project.created_at).toLocaleString()}
                </div>
                <div className="edit-hint" style={{ marginTop: '1rem' }}>Click to view 👁️</div>
              </div>
            ))
          )}
        </div>
      )}
    </section>
  );
}

export default Dashboard;
