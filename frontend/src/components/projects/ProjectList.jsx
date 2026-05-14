import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuthStore } from '../../context/authStore';
import { projectService } from '../../services/api';

const ProjectList = () => {
  const { token } = useAuthStore();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showNewProject, setShowNewProject] = useState(false);
  const [newProjectName, setNewProjectName] = useState('');
  const [newProjectLanguage, setNewProjectLanguage] = useState('python');

  const fetchProjects = async () => {
    if (!token) return;
    setLoading(true);
    try {
      const data = await projectService.getProjects();
      setProjects(data);
    } catch (error) {
      console.error('Failed to fetch projects:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProject = async (e) => {
    e.preventDefault();
    if (!newProjectName.trim()) return;
    
    try {
      const project = await projectService.createProject(
        newProjectName,
        newProjectLanguage
      );
      setProjects([...projects, project]);
      setNewProjectName('');
      setShowNewProject(false);
    } catch (error) {
      console.error('Failed to create project:', error);
    }
  };

  const handleDeleteProject = async (projectId) => {
    if (!confirm('Are you sure you want to delete this project?')) return;
    
    try {
      await projectService.deleteProject(projectId);
      setProjects(projects.filter(p => p.id !== projectId));
    } catch (error) {
      console.error('Failed to delete project:', error);
    }
  };

  return (
    <div className="card">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold text-gray-800 dark:text-white">My Projects</h2>
        <button
          onClick={() => setShowNewProject(!showNewProject)}
          className="btn-primary flex items-center gap-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          New Project
        </button>
      </div>

      {showNewProject && (
        <form onSubmit={handleCreateProject} className="mb-6 p-4 bg-gray-50 dark:bg-dark-bg rounded-lg">
          <div className="flex gap-4">
            <input
              type="text"
              value={newProjectName}
              onChange={(e) => setNewProjectName(e.target.value)}
              placeholder="Project name"
              className="input-field flex-1"
              autoFocus
            />
            <select
              value={newProjectLanguage}
              onChange={(e) => setNewProjectLanguage(e.target.value)}
              className="input-field w-auto"
            >
              <option value="python">Python</option>
              <option value="javascript">JavaScript</option>
              <option value="java">Java</option>
              <option value="cpp">C++</option>
              <option value="c">C</option>
            </select>
            <button type="submit" className="btn-primary">Create</button>
            <button
              type="button"
              onClick={() => setShowNewProject(false)}
              className="btn-secondary"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {loading ? (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      ) : projects.length === 0 ? (
        <p className="text-gray-500 dark:text-gray-400 text-center py-8">
          No projects yet. Create your first project!
        </p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {projects.map((project) => (
            <div
              key={project.id}
              className="card hover:shadow-xl transition-shadow cursor-pointer"
            >
              <Link to={`/editor/${project.id}`}>
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-semibold text-gray-800 dark:text-white truncate">
                    {project.name}
                  </h3>
                  <span className="text-xs px-2 py-1 bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300 rounded">
                    {project.language}
                  </span>
                </div>
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-4 line-clamp-2">
                  {project.description || 'No description'}
                </p>
                <div className="flex justify-between items-center text-xs text-gray-400">
                  <span>Updated: {new Date(project.updated_at).toLocaleDateString()}</span>
                  <button
                    onClick={(e) => {
                      e.preventDefault();
                      handleDeleteProject(project.id);
                    }}
                    className="text-red-500 hover:text-red-700"
                  >
                    Delete
                  </button>
                </div>
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ProjectList;
