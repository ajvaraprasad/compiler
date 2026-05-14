import { useState } from 'react';
import { useEditorStore } from '../../context/editorStore';
import { executionService } from '../../services/api';

const OutputConsole = () => {
  const { output, error, isRunning, setIsRunning, setOutput, setError } = useEditorStore();
  const [activeTab, setActiveTab] = useState('output');

  return (
    <div className="card h-full flex flex-col">
      <div className="flex border-b border-gray-200 dark:border-dark-border mb-4">
        <button
          onClick={() => setActiveTab('output')}
          className={`px-4 py-2 font-medium ${
            activeTab === 'output'
              ? 'text-primary-600 border-b-2 border-primary-600'
              : 'text-gray-500 hover:text-gray-700 dark:text-gray-400'
          }`}
        >
          Output
        </button>
        <button
          onClick={() => setActiveTab('error')}
          className={`px-4 py-2 font-medium ${
            activeTab === 'error'
              ? 'text-red-600 border-b-2 border-red-600'
              : 'text-gray-500 hover:text-gray-700 dark:text-gray-400'
          }`}
        >
          Errors
        </button>
      </div>

      <div className="flex-1 overflow-auto font-mono text-sm">
        {isRunning ? (
          <div className="flex items-center justify-center h-full">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
            <span className="ml-3 text-gray-500">Running...</span>
          </div>
        ) : activeTab === 'output' ? (
          output ? (
            <pre className="whitespace-pre-wrap text-gray-800 dark:text-gray-200">{output}</pre>
          ) : (
            <p className="text-gray-400 italic">No output yet. Run your code to see results.</p>
          )
        ) : error ? (
          <pre className="whitespace-pre-wrap text-red-600 dark:text-red-400">{error}</pre>
        ) : (
          <p className="text-gray-400 italic">No errors.</p>
        )}
      </div>
    </div>
  );
};

export default OutputConsole;
