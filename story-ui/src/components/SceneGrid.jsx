import React, { useState } from 'react';
import { saveDraft, publishProject } from '../services/api';

function SceneGrid({ topic, story, scenes, onBack, onPublished }) {
  const [localScenes, setLocalScenes] = useState(scenes);
  const [loading, setLoading] = useState(false);
  const [currentlyEditing, setCurrentlyEditing] = useState(null);
  const [editText, setEditText] = useState('');

  const handleSave = async () => {
    setLoading(true);
    try {
      const draft = await saveDraft(topic, story, localScenes);
      await publishProject(draft.project_id);
      alert('Video generation triggered successfully!');
      onPublished();
    } catch (err) {
      alert('Failed to publish: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const openEdit = (scene) => {
    setCurrentlyEditing(scene);
    setEditText(scene.description);
  };

  const saveEdit = () => {
    const updated = localScenes.map(s => s.id === currentlyEditing.id ? { ...s, description: editText } : s);
    setLocalScenes(updated);
    setCurrentlyEditing(null);
  };

  return (
    <section id="view-scenes" className="view active">
      <h2>Story Scenes</h2>
      <div className="scenes-grid">
        {localScenes.map((scene) => (
          <div key={scene.id} className="scene-card" onClick={() => openEdit(scene)}>
            <div className="scene-number">Scene {scene.id}</div>
            <div className="scene-desc">{scene.description}</div>
            <div className="edit-hint">Click to edit ✏️</div>
          </div>
        ))}
      </div>
      <div className="action-buttons">
        <button onClick={onBack} className="secondary-btn">Back to Story</button>
        <button onClick={handleSave} className="primary-btn" disabled={loading} style={{ width: 'auto', marginTop: 0 }}>
          <span>{loading ? 'Publishing...' : 'Publish Video'}</span>
          <div className="btn-glow"></div>
        </button>
      </div>

      {currentlyEditing && (
        <div className="modal" style={{ visibility: 'visible', opacity: 1 }}>
          <div className="modal-content glass-panel">
            <div className="modal-header">
              <h3>Edit Scene {currentlyEditing.id}</h3>
              <button onClick={() => setCurrentlyEditing(null)} className="close-btn">&times;</button>
            </div>
            <div className="modal-body">
              <label>Scene Description:</label>
              <textarea 
                value={editText} 
                onChange={(e) => setEditText(e.target.value)}
                style={{ height: '200px' }}
              />
            </div>
            <div className="modal-footer">
              <button onClick={saveEdit} className="primary-btn" style={{ width: 'auto', marginTop: 0 }}>Save Changes</button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}

export default SceneGrid;
