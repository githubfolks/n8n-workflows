document.addEventListener('DOMContentLoaded', () => {
    // API Configuration
    const API_BASE_URL = 'http://localhost:9001/api/v1';

    // Views
    const viewLogin = document.getElementById('view-login');
    const viewDashboard = document.getElementById('view-dashboard');
    const viewInput = document.getElementById('view-input');
    const viewLoadingStory = document.getElementById('view-loading-story');
    const viewStory = document.getElementById('view-story');
    const viewLoadingScenes = document.getElementById('view-loading-scenes');
    const viewScenes = document.getElementById('view-scenes');
    const viewProjectDetails = document.getElementById('view-project-details');

    // Elements
    const loginUsername = document.getElementById('login-username');
    const loginPassword = document.getElementById('login-password');
    const loginError = document.getElementById('login-error');
    const projectsContainer = document.getElementById('projects-container');
    const storyInput = document.getElementById('story-input');
    const storyDisplay = document.getElementById('story-display');
    const scenesContainer = document.getElementById('scenes-container');

    const detailTopicTitle = document.getElementById('detail-topic-title');
    const detailStoryDisplay = document.getElementById('detail-story-display');
    const detailScenesContainer = document.getElementById('detail-scenes-container');
    const detailVideoContainer = document.getElementById('detail-video-container');
    const detailStatusBadge = document.getElementById('detail-status-badge');

    // Buttons
    const btnLogin = document.getElementById('btn-login');
    const btnCreateNew = document.getElementById('btn-create-new');
    const btnBackToDashFromInput = document.getElementById('btn-back-to-dash-from-input');
    const btnBackToDashFromDetails = document.getElementById('btn-back-to-dash-from-details');
    const btnGenerateStory = document.getElementById('btn-generate-story');
    const btnBackToInput = document.getElementById('btn-back-to-input');
    const btnGenerateScenes = document.getElementById('btn-generate-scenes');
    const btnBackToStory = document.getElementById('btn-back-to-story');
    const btnPublish = document.getElementById('btn-publish');

    // Modal
    const modal = document.getElementById('editor-modal');
    const btnCloseModal = document.getElementById('btn-close-modal');
    const btnSaveScene = document.getElementById('btn-save-scene');
    const sceneEditorTextarea = document.getElementById('scene-editor-textarea');
    const modalSceneTitle = document.getElementById('modal-scene-title');

    // App State
    let currentTopic = '';
    let generatedStory = '';
    let generatedScenes = [];
    let currentlyEditingSceneId = null;

    // Authentication
    function getAuthToken() {
        return localStorage.getItem('auth_token');
    }

    function setAuthToken(token) {
        localStorage.setItem('auth_token', token);
    }

    function clearAuthToken() {
        localStorage.removeItem('auth_token');
    }

    function getAuthHeaders() {
        const token = getAuthToken();
        return {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        };
    }

    async function handleLogin() {
        const username = loginUsername.value.trim();
        const password = loginPassword.value.trim();

        if (!username || !password) {
            loginError.textContent = 'Please enter both username and password.';
            loginError.classList.remove('hidden');
            return;
        }

        btnLogin.disabled = true;
        loginError.classList.add('hidden');

        try {
            // Updated to match the available port
            const response = await fetch('http://localhost:9001/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            if (!response.ok) {
                throw new Error('Invalid credentials');
            }

            const data = await response.json();
            setAuthToken(data.access_token || data.token || 'mock-token'); // Fallback if API response differs
            
            // Success - load dashboard
            fetchProjects();
            switchView(viewDashboard);
        } catch (error) {
            console.error('Login error:', error);
            loginError.textContent = 'Login failed. Please check your credentials.';
            loginError.classList.remove('hidden');
        } finally {
            btnLogin.disabled = false;
        }
    }

    btnLogin.addEventListener('click', handleLogin);

    // Enter key to login
    loginPassword.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleLogin();
    });

    // View Switching Logic
    function switchView(viewToShow) {
        const views = [viewLogin, viewDashboard, viewInput, viewLoadingStory, viewStory, viewLoadingScenes, viewScenes, viewProjectDetails];
        views.forEach(v => {
            if (v === viewToShow) {
                v.classList.remove('hidden');
                setTimeout(() => {
                    v.classList.add('active');
                }, 10);
            } else {
                v.classList.remove('active');
                setTimeout(() => {
                    if (!v.classList.contains('active')) {
                        v.classList.add('hidden');
                    }
                }, 400);
            }
        });
    }

    // Navigation
    btnCreateNew.addEventListener('click', () => {
        storyInput.value = '';
        switchView(viewInput);
    });

    btnBackToDashFromInput.addEventListener('click', () => {
        switchView(viewDashboard);
    });

    btnBackToDashFromDetails.addEventListener('click', () => {
        switchView(viewDashboard);
    });

    // Story Generation Flow
    btnGenerateStory.addEventListener('click', async () => {
        const inputText = storyInput.value.trim();
        if (!inputText) {
            storyInput.style.borderColor = '#ef4444';
            setTimeout(() => storyInput.style.borderColor = '', 1000);
            return;
        }

        currentTopic = inputText;
        switchView(viewLoadingStory);

        try {
            const response = await fetch(`${API_BASE_URL}/story/generate-story`, {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify({ topic: inputText })
            });

            if (!response.ok) {
                if (response.status === 401) {
                    clearAuthToken();
                    switchView(viewLogin);
                    return;
                }
                throw new Error('API Error');
            }
            const data = await response.json();

            generatedStory = data.story;
            storyDisplay.textContent = generatedStory;
            switchView(viewStory);
        } catch (error) {
            console.error('Error generating story:', error);
            alert('Failed to generate story. Please try again.');
            switchView(viewInput);
        }
    });

    btnBackToInput.addEventListener('click', () => {
        switchView(viewInput);
    });

    // Scenes Generation Flow
    btnGenerateScenes.addEventListener('click', async () => {
        switchView(viewLoadingScenes);

        try {
            const response = await fetch(`${API_BASE_URL}/story/generate-scenes`, {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify({ story: generatedStory })
            });

            if (!response.ok) {
                if (response.status === 401) {
                    clearAuthToken();
                    switchView(viewLogin);
                    return;
                }
                throw new Error('API Error');
            }
            generatedScenes = await response.json();

            renderScenes();
            switchView(viewScenes);
        } catch (error) {
            console.error('Error generating scenes:', error);
            alert('Failed to generate scenes. Please try again.');
            switchView(viewStory);
        }
    });

    btnBackToStory.addEventListener('click', () => {
        switchView(viewStory);
    });

    btnPublish.addEventListener('click', async () => {
        const span = btnPublish.querySelector('span');
        const originalText = span.textContent;
        span.textContent = 'Saving to Database...';
        btnPublish.disabled = true;

        try {
            const saveResponse = await fetch(`${API_BASE_URL}/story/save-draft`, {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify({
                    topic: currentTopic,
                    story: generatedStory,
                    scenes: generatedScenes
                })
            });

            if (!saveResponse.ok) throw new Error('Failed to save to database');
            const saveResult = await saveResponse.json();
            const projectId = saveResult.project_id;

            span.textContent = 'Triggering n8n...';
            const publishResponse = await fetch(`${API_BASE_URL}/story/publish-project/${projectId}`, {
                method: 'POST',
                headers: getAuthHeaders()
            });

            if (!publishResponse.ok) throw new Error('Failed to trigger publishing');

            alert('Data saved to database and Video generation workflow triggered successfully!');
            fetchProjects(); // Refresh dashboard
            switchView(viewDashboard);
        } catch (error) {
            console.error('Error in publish flow:', error);
            alert('Failed to publish. ' + error.message);
        } finally {
            span.textContent = originalText;
            btnPublish.disabled = false;
        }
    });

    // Modal Logic
    function openModal(scene) {
        currentlyEditingSceneId = scene.id;
        modalSceneTitle.textContent = `Edit Scene ${scene.id}`;
        sceneEditorTextarea.value = scene.description;
        modal.classList.remove('hidden');
    }

    function closeModal() {
        modal.classList.add('hidden');
        currentlyEditingSceneId = null;
    }

    btnCloseModal.addEventListener('click', closeModal);

    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });

    btnSaveScene.addEventListener('click', () => {
        if (currentlyEditingSceneId !== null) {
            const sceneIndex = generatedScenes.findIndex(s => s.id === currentlyEditingSceneId);
            if (sceneIndex > -1) {
                generatedScenes[sceneIndex].description = sceneEditorTextarea.value;
                renderScenes();
            }
        }
        closeModal();
    });

    function renderScenes() {
        scenesContainer.innerHTML = '';
        generatedScenes.forEach(scene => {
            const card = document.createElement('div');
            card.className = 'scene-card';
            card.innerHTML = `
                <div class="scene-number">Scene ${scene.id}</div>
                <div class="scene-desc">${escapeHtml(scene.description)}</div>
                <div class="edit-hint">Click to edit ✏️</div>
            `;

            card.addEventListener('click', () => openModal(scene));
            scenesContainer.appendChild(card);
        });
    }

    function escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    async function fetchProjects() {
        try {
            const response = await fetch(`${API_BASE_URL}/story/projects`, {
                headers: getAuthHeaders()
            });
            if (!response.ok) {
                if (response.status === 401) {
                    clearAuthToken();
                    switchView(viewLogin);
                    return;
                }
                throw new Error('Failed to fetch projects');
            }
            const projects = await response.json();
            renderDashboard(projects);
        } catch (error) {
            console.error('Error fetching dashboard data:', error);
            projectsContainer.innerHTML = '<p class="error-msg">Could not load active projects.</p>';
        }
    }

    function renderDashboard(projects) {
        projectsContainer.innerHTML = '';
        if (projects.length === 0) {
            projectsContainer.innerHTML = '<p style="grid-column: 1/-1; text-align:center; color: #a1a1aa;">No stories found. Create your first one!</p>';
            return;
        }

        projects.forEach(project => {
            const card = document.createElement('div');
            card.className = 'scene-card';

            const dateObj = new Date(project.created_at);
            const dateStr = dateObj.toLocaleDateString() + ' ' + dateObj.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

            card.innerHTML = `
                <div class="scene-number">${escapeHtml(project.status.toUpperCase())}</div>
                <div class="scene-desc" style="font-weight:600; font-size:1.1rem; margin-bottom: 0.5rem; color:white;">
                    ${escapeHtml(project.topic_prompt)}
                </div>
                <div style="font-size: 0.8rem; color:#a1a1aa;">${dateStr}</div>
                <div class="edit-hint" style="margin-top:1rem;">Click to view 👁️</div>
            `;

            card.addEventListener('click', () => openProjectDetails(project));
            projectsContainer.appendChild(card);
        });
    }

    function openProjectDetails(project) {
        detailTopicTitle.textContent = project.topic_prompt;
        detailStoryDisplay.textContent = project.generated_story || "No story text.";

        detailScenesContainer.innerHTML = '';
        if (project.scenes_json && Array.isArray(project.scenes_json)) {
            project.scenes_json.forEach(scene => {
                const scard = document.createElement('div');
                scard.className = 'scene-card';
                scard.innerHTML = `
                    <div class="scene-number">Scene ${scene.id}</div>
                    <div class="scene-desc">${escapeHtml(scene.description)}</div>
                `;
                detailScenesContainer.appendChild(scard);
            });
        } else {
            detailScenesContainer.innerHTML = '<p>No scenes generated.</p>';
        }

        detailVideoContainer.innerHTML = '';
        detailStatusBadge.textContent = 'Status: ' + project.status.toUpperCase();

        if (project.status === 'completed' && project.video_path) {
            detailStatusBadge.className = 'status-badge mt-1 success-bg';
            detailVideoContainer.className = '';
            detailVideoContainer.innerHTML = `
                <div class="video-placeholder" style="background: rgba(16, 185, 129, 0.1); border-color: #10b981;">
                    <p style="color:#10b981; font-weight:600;">✔️ Video Rendered Successfully!</p>
                    <p style="font-size:0.8rem; margin-top:0.5rem;">File: ${escapeHtml(project.video_path)}</p>
                </div>
            `;
        } else if (project.status === 'publishing') {
            detailStatusBadge.className = 'status-badge mt-1 publishing-bg';
            detailVideoContainer.className = 'video-placeholder';
            detailVideoContainer.innerHTML = `<p>Video is currently building in n8n...</p>`;
        } else {
            detailStatusBadge.className = 'status-badge mt-1 draft-bg';
            detailVideoContainer.className = 'video-placeholder';
            detailVideoContainer.innerHTML = `<p>No video rendering in progress.</p>`;
        }

        switchView(viewProjectDetails);
    }

    // Initialize
    if (getAuthToken()) {
        fetchProjects();
        switchView(viewDashboard);
    } else {
        switchView(viewLogin);
    }
});
