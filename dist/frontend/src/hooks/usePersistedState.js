import { useState } from 'react';

export default function usePersistedState(key, initialValue) {
  const [value, setValue] = useState(() => {
    if (typeof window === 'undefined') return initialValue;
    try {
      const stored = localStorage.getItem(key);
      return stored !== null ? JSON.parse(stored) : initialValue;
    } catch {
      return initialValue;
    }
  });

  const setPersistedValue = (newValue) => {
    setValue((prev) => {
      const resolved = typeof newValue === 'function' ? newValue(prev) : newValue;
      if (typeof window !== 'undefined') {
        try {
          localStorage.setItem(key, JSON.stringify(resolved));
        } catch {}
      }
      return resolved;
    });
  };

  return [value, setPersistedValue];
}
