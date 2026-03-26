import React, { useState, useEffect } from 'react';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import StoryEditor from './components/StoryEditor';
import SceneGrid from './components/SceneGrid';
import ProjectDetails from './components/ProjectDetails';
import { generateScenes } from './services/api';

function App() {
  const [view, setView] = useState('login');
  const [token, setToken] = useState(localStorage.getItem('auth_token'));
  const [currentProject, setCurrentProject] = useState(null);
  const [generatedStory, setGeneratedStory] = useState('');
  const [generatedScenes, setGeneratedScenes] = useState([]);
  const [topic, setTopic] = useState('');
  const [loadingScenes, setLoadingScenes] = useState(false);

  useEffect(() => {
    if (token) {
      setView('dashboard');
    } else {
      setView('login');
    }
  }, [token]);

  const handleLoginSuccess = (newToken) => {
    localStorage.setItem('auth_token', newToken);
    setToken(newToken);
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    setToken(null);
    setView('login');
  };

  return (
    <>
      <div className="background-elements">
        <div className="blob blob-1"></div>
        <div className="blob blob-2"></div>
        <div className="blob blob-3"></div>
      </div>
      
      <main className="container glass-panel" style={{ position: 'relative', zIndex: 10 }}>
        <header>
          <h1>Aadikarta Story Forge</h1>
          <p className="subtitle">Transform your ideas into visual scenes</p>
          {token && (
            <button 
              onClick={logout} 
              className="secondary-btn small-btn" 
              style={{ position: 'absolute', top: '1rem', right: '1rem', margin: 0 }}
            >
              Logout
            </button>
          )}
        </header>

        {view === 'login' && <Login onLoginSuccess={handleLoginSuccess} />}
        
        {view === 'dashboard' && (
          <Dashboard 
            token={token} 
            onCreateNew={() => setView('input')} 
            onViewDetails={(p) => { setCurrentProject(p); setView('details'); }}
          />
        )}

        {view === 'input' && (
          <StoryEditor 
            token={token}
            onBack={() => setView('dashboard')}
            onStoryGenerated={(t, s) => { setTopic(t); setGeneratedStory(s); setView('story'); }}
          />
        )}

        {view === 'story' && (
          <div className="view active">
            <h2>Your Generated Story</h2>
            <div className="story-content content-box">{generatedStory}</div>
            <div className="action-buttons">
              <button onClick={() => setView('input')} className="secondary-btn">Edit Input</button>
              <button 
                onClick={async () => {
                  setLoadingScenes(true);
                  setView('loading-scenes');
                  try {
                    const data = await generateScenes(generatedStory);
                    setGeneratedScenes(data.scenes);
                    setView('scenes');
                  } catch (err) {
                    alert('Scene generation failed');
                    setView('story');
                  } finally {
                    setLoadingScenes(false);
                  }
                }} 
                className="primary-btn"
                style={{ width: 'auto', marginTop: 0 }}
              >
                <span>Generate Scenes</span>
                <div className="btn-glow"></div>
              </button>
            </div>
          </div>
        )}

        {view === 'loading-scenes' && (
          <div className="view active">
            <div className="spinner-container">
              <div className="spinner"></div>
              <p>Visualizing your scenes...</p>
            </div>
          </div>
        )}

        {view === 'scenes' && (
          <SceneGrid 
            topic={topic}
            story={generatedStory}
            scenes={generatedScenes}
            onBack={() => setView('story')}
            onPublished={() => setView('dashboard')}
          />
        )}

        {/* Simplified Scene flow for now - porting the rest next */}
        {view === 'details' && currentProject && (
          <ProjectDetails 
            project={currentProject} 
            onBack={() => setView('dashboard')} 
          />
        )}
      </main>
    </>
  );
}

export default App;
