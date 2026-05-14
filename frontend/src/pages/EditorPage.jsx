import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import CodeEditor from '../components/editor/CodeEditor';
import EditorToolbar from '../components/editor/EditorToolbar';
import OutputConsole from '../components/editor/OutputConsole';
import { useEditorStore } from '../context/editorStore';
import { projectService } from '../services/api';
import { useAuthStore } from '../context/authStore';

const EditorPage = () => {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const { token } = useAuthStore();
  const { setCode, setLanguage, code, language } = useEditorStore();
  const [loading, setLoading] = useState(true);
  const [projectName, setProjectName] = useState('');

  useEffect(() => {
    if (!token) {
      navigate('/login');
      return;
    }

    const loadProject = async () => {
      if (projectId === 'new') {
        // New project - use defaults
        setCode('// Start coding here...\n');
        setLanguage('javascript');
        setProjectName('New Project');
        setLoading(false);
        return;
      }

      try {
        const project = await projectService.getProject(projectId);
        setCode(project.code || '');
        setLanguage(project.language);
        setProjectName(project.name);
      } catch (error) {
        console.error('Failed to load project:', error);
        navigate('/dashboard');
      } finally {
        setLoading(false);
      }
    };

    loadProject();
  }, [projectId, token, navigate]);

  const handleSave = async () => {
    try {
      if (projectId === 'new') {
        const name = prompt('Enter project name:', 'My Project');
        if (!name) return;
        
        const project = await projectService.createProject(
          name,
          language,
          code
        );
        navigate(`/editor/${project.id}`);
      } else {
        await projectService.updateProject(projectId, { code, language });
        alert('Project saved successfully!');
      }
    } catch (error) {
      console.error('Failed to save project:', error);
      alert('Failed to save project');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-dark-bg">
      {/* Header */}
      <header className="bg-white dark:bg-dark-surface border-b border-gray-200 dark:border-dark-border px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="text-gray-500 hover:text-gray-700 dark:text-gray-400"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
            </button>
            <h1 className="text-xl font-bold text-gray-800 dark:text-white">
              {projectName}
            </h1>
          </div>
          <button onClick={handleSave} className="btn-primary">
            Save Project
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="p-6 h-[calc(100vh-80px)]">
        <EditorToolbar />
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100%-100px)]">
          <div className="lg:col-span-2 h-[60vh] lg:h-auto">
            <div className="card h-full p-0 overflow-hidden">
              <CodeEditor />
            </div>
          </div>
          <div className="h-[40vh] lg:h-auto">
            <OutputConsole />
          </div>
        </div>
      </main>
    </div>
  );
};

export default EditorPage;
