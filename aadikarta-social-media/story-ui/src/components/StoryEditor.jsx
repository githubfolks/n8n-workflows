import React, { useState } from 'react';
import { generateStory } from '../services/api';

function StoryEditor({ token, onBack, onStoryGenerated }) {
  const [topicInput, setTopicInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleGenerate = async () => {
    if (!topicInput.trim()) {
      setError('Please enter a story idea.');
      return;
    }
    setLoading(true);
    setError('');

    try {
      const data = await generateStory(topicInput);
      onStoryGenerated(topicInput, data.story);
    } catch (err) {
      setError('Failed to generate story. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <section id="view-loading-story" className="view active">
        <div className="spinner-container">
          <div className="spinner"></div>
          <p>Weaving your story together...</p>
        </div>
      </section>
    );
  }

  return (
    <section id="view-input" className="view active">
      <div className="dashboard-header">
        <h2>New Story Idea</h2>
        <button onClick={onBack} className="secondary-btn small-btn">Back to Dashboard</button>
      </div>
      <div className="input-group">
        <label htmlFor="story-input">Enter your idea (will generate a 30-second video script):</label>
        <textarea 
          id="story-input"
          placeholder="e.g. A solitary astronaut discovers an ancient artifact on Mars..."
          value={topicInput}
          onChange={(e) => setTopicInput(e.target.value)}
          style={{ height: '200px' }}
        ></textarea>
      </div>
      {error && <p className="error-msg">{error}</p>}
      <button onClick={handleGenerate} className="primary-btn">
        <span>Generate Story</span>
        <div className="btn-glow"></div>
      </button>
    </section>
  );
}

export default StoryEditor;
