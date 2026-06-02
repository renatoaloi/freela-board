import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const toolbarButtons = [
  { label: 'B', cmd: 'bold', style: 'font-bold', action: (ta) => wrap(ta, '**') },
  { label: 'I', cmd: 'italic', style: 'italic', action: (ta) => wrap(ta, '_') },
  { label: 'H1', cmd: 'h1', action: (ta) => insertLine(ta, '# ') },
  { label: 'H2', cmd: 'h2', action: (ta) => insertLine(ta, '## ') },
  { label: 'H3', cmd: 'h3', action: (ta) => insertLine(ta, '### ') },
  { label: '•', cmd: 'ul', action: (ta) => insertLine(ta, '- ') },
  { label: '1.', cmd: 'ol', action: (ta) => insertLine(ta, '1. ') },
  { label: '☐', cmd: 'task', action: (ta) => insertLine(ta, '- [ ] ') },
  { label: '>', cmd: 'quote', action: (ta) => insertLine(ta, '> ') },
  { label: '---', cmd: 'hr', action: (ta) => insertAtCursor(ta, '\n---\n') },
];

function wrap(ta, char) {
  const start = ta.selectionStart;
  const end = ta.selectionEnd;
  const text = ta.value;
  const selected = text.substring(start, end);
  const before = text.substring(0, start);
  const after = text.substring(end);
  ta.value = `${before}${char}${selected}${char}${after}`;
  ta.selectionStart = start + char.length;
  ta.selectionEnd = end + char.length;
  ta.focus();
  ta.dispatchEvent(new Event('input', { bubbles: true }));
}

function insertLine(ta, prefix) {
  const start = ta.selectionStart;
  const text = ta.value;
  const before = text.substring(0, start);
  const after = text.substring(start);
  ta.value = `${before}${prefix}${after}`;
  ta.selectionStart = start + prefix.length;
  ta.selectionEnd = start + prefix.length;
  ta.focus();
  ta.dispatchEvent(new Event('input', { bubbles: true }));
}

function insertAtCursor(ta, text) {
  const start = ta.selectionStart;
  const val = ta.value;
  ta.value = val.substring(0, start) + text + val.substring(start);
  ta.selectionStart = start + text.length;
  ta.selectionEnd = start + text.length;
  ta.focus();
  ta.dispatchEvent(new Event('input', { bubbles: true }));
}

export default function MarkdownEditor({ value, onChange, label, placeholder = 'Escreva em markdown...', rows = 6 }) {
  const [showPreview, setShowPreview] = useState(false);
  const textareaRef = React.useRef(null);

  const handleToolbar = (action) => {
    if (textareaRef.current) {
      action(textareaRef.current);
    }
  };

  const handleChange = (e) => {
    onChange(e.target.value);
  };

  return (
    <div className="space-y-2">
      {label && (
        <label className="block text-sm font-medium text-gray-300">{label}</label>
      )}
      <div className="glass-card rounded-xl overflow-hidden border border-primary-600/50">
        <div className="flex items-center justify-between px-3 py-2 border-b border-primary-600/50 bg-primary-800/50">
          <div className="flex flex-wrap gap-1">
            {toolbarButtons.map((btn) => (
              <button
                key={btn.cmd}
                type="button"
                onClick={() => handleToolbar(btn.action)}
                className={`px-2 py-1 text-xs rounded text-gray-400 hover:text-white hover:bg-primary-700 transition-colors ${btn.style || ''}`}
                title={btn.cmd}
              >
                {btn.label}
              </button>
            ))}
          </div>
          <button
            type="button"
            onClick={() => setShowPreview(!showPreview)}
            className={`text-xs px-3 py-1 rounded transition-colors ${
              showPreview
                ? 'bg-accent-cyan/20 text-accent-cyan'
                : 'text-gray-400 hover:text-gray-200'
            }`}
          >
            {showPreview ? 'Editar' : 'Preview'}
          </button>
        </div>
        {showPreview ? (
          <div className="p-4 min-h-[200px] prose prose-invert prose-sm max-w-none">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{value || '*Nenhum conteúdo*'}</ReactMarkdown>
          </div>
        ) : (
          <textarea
            ref={textareaRef}
            value={value}
            onChange={handleChange}
            placeholder={placeholder}
            rows={rows}
            className="w-full bg-transparent text-gray-200 px-4 py-3 resize-y focus:outline-none font-mono text-sm placeholder-gray-500"
          />
        )}
      </div>
    </div>
  );
}
