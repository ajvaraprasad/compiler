import { useState } from 'react';
import { useEditorStore } from '../../context/editorStore';
import { executionService } from '../../services/api';

const languages = [
  { value: 'python', label: 'Python' },
  { value: 'javascript', label: 'JavaScript' },
  { value: 'java', label: 'Java' },
  { value: 'cpp', label: 'C++' },
  { value: 'c', label: 'C' },
];

const EditorToolbar = () => {
  const { 
    language, 
    input, 
    setLanguage, 
    setInput, 
    setIsRunning, 
    setOutput, 
    setError,
    clearOutput 
  } = useEditorStore();
  
  const [isSaving, setIsSaving] = useState(false);

  const handleRun = async () => {
    const store = useEditorStore.getState();
    setIsRunning(true);
    clearOutput();
    
    try {
      const result = await executionService.executeCode(
        language,
        store.code,
        input
      );
      
      setOutput(result.output || '');
      setError(result.error || '');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to execute code');
    } finally {
      setIsRunning(false);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    // Save logic will be implemented with project context
    setTimeout(() => setIsSaving(false), 500);
  };

  return (
    <div className="card mb-4">
      <div className="flex flex-wrap items-center gap-4">
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Language:
          </label>
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="input-field w-auto py-1.5"
          >
            {languages.map((lang) => (
              <option key={lang.value} value={lang.value}>
                {lang.label}
              </option>
            ))}
          </select>
        </div>

        <div className="flex items-center gap-2 flex-1">
          <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Input:
          </label>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Program input (optional)"
            className="input-field flex-1 py-1.5"
          />
        </div>

        <div className="flex items-center gap-2 ml-auto">
          <button
            onClick={handleRun}
            disabled={isSaving}
            className="btn-primary flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Run
          </button>
          
          <button
            onClick={handleSave}
            disabled={isSaving}
            className="btn-secondary flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
            </svg>
            {isSaving ? 'Saving...' : 'Save'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default EditorToolbar;
