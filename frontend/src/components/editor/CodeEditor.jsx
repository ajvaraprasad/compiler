import Editor from '@monaco-editor/react';
import { useEditorStore } from '../../context/editorStore';

const CodeEditor = () => {
  const { code, language, theme, setCode } = useEditorStore();

  const languageMap = {
    python: 'python',
    javascript: 'javascript',
    java: 'java',
    cpp: 'cpp',
    c: 'c',
  };

  return (
    <div className="h-full">
      <Editor
        height="100%"
        language={languageMap[language] || 'plaintext'}
        theme={theme}
        value={code}
        onChange={(value) => setCode(value || '')}
        options={{
          minimap: { enabled: false },
          fontSize: 14,
          automaticLayout: true,
          scrollBeyondLastLine: false,
          renderWhitespace: 'selection',
          wordWrap: 'on',
        }}
      />
    </div>
  );
};

export default CodeEditor;
