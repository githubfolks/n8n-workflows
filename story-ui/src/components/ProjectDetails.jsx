import React from 'react';

function ProjectDetails({ project, onBack }) {
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
    <section id="view-project-details" className="view active">
      <div className="dashboard-header">
        <h2 id="detail-topic-title">{project.topic_prompt}</h2>
        <button onClick={onBack} className="secondary-btn small-btn">Back to Dashboard</button>
      </div>

      <div className="detail-grid">
        <div className="detail-text-column">
          <h3>Story</h3>
          <div className="story-content content-box">{project.generated_story || "No story text."}</div>

          <h3 style={{ marginTop: '1.5rem' }}>Scenes</h3>
          <div className="scenes-grid">
            {project.scenes_json && Array.isArray(project.scenes_json) ? (
              project.scenes_json.map((scene) => (
                <div key={scene.id} className="scene-card">
                  <div className="scene-number">Scene {scene.id}</div>
                  <div className="scene-desc">{escapeHtml(scene.description)}</div>
                </div>
              ))
            ) : (
              <p>No scenes generated.</p>
            )}
          </div>
        </div>

        <div className="detail-video-column">
          <h3>Final Video</h3>
          <div 
            className={`video-placeholder ${project.status === 'completed' ? '' : ''}`}
            style={project.status === 'completed' ? { background: 'rgba(16, 185, 129, 0.1)', borderColor: '#10b981' } : {}}
          >
            {project.status === 'completed' && project.video_path ? (
              <>
                <p style={{ color: '#10b981', fontWeight: 600 }}>✔️ Video Rendered Successfully!</p>
                <p style={{ fontSize: '0.8rem', marginTop: '0.5rem' }}>File: {project.video_path}</p>
              </>
            ) : project.status === 'publishing' ? (
              <p>Video is currently building in n8n...</p>
            ) : (
              <p>No video rendering in progress.</p>
            )}
          </div>
          <div className={`status-badge mt-1 ${
            project.status === 'completed' ? 'success-bg' : 
            project.status === 'publishing' ? 'publishing-bg' : 'draft-bg'
          }`}>
            Status: {project.status.toUpperCase()}
          </div>
        </div>
      </div>
    </section>
  );
}

export default ProjectDetails;
