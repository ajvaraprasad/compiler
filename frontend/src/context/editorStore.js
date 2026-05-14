import { create } from 'zustand';

export const useEditorStore = create((set, get) => ({
  code: '',
  language: 'python',
  input: '',
  output: '',
  error: '',
  isRunning: false,
  theme: 'vs-dark',
  
  setCode: (code) => set({ code }),
  
  setLanguage: (language) => set({ language }),
  
  setInput: (input) => set({ input }),
  
  setOutput: (output) => set({ output }),
  
  setError: (error) => set({ error }),
  
  setIsRunning: (isRunning) => set({ isRunning }),
  
  setTheme: (theme) => set({ theme }),
  
  clearOutput: () => set({ output: '', error: '' }),
  
  toggleTheme: () => {
    const current = get().theme;
    set({ theme: current === 'vs-dark' ? 'light' : 'vs-dark' });
  },
}));
