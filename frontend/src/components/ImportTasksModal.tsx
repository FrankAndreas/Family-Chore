import React, { useState, useRef } from 'react';
import Modal from './Modal';
import type { TaskImportItem, ImportResult } from '../api';
import { importTasks } from '../api';
import { useToast } from '../context/ToastContext';
import './Modal.css';

interface ImportTasksModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSuccess: () => void;
}

const ImportTasksModal: React.FC<ImportTasksModalProps> = ({
    isOpen,
    onClose,
    onSuccess
}) => {
    const [jsonInput, setJsonInput] = useState('');
    const [parsedTasks, setParsedTasks] = useState<TaskImportItem[]>([]);
    const [parseError, setParseError] = useState<string | null>(null);
    const [skipDuplicates, setSkipDuplicates] = useState(false);
    const [isImporting, setIsImporting] = useState(false);
    const [importResult, setImportResult] = useState<ImportResult | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const { showToast } = useToast();

    const handleJsonChange = (text: string) => {
        setJsonInput(text);
        setParseError(null);
        setParsedTasks([]);
        setImportResult(null);

        if (!text.trim()) return;

        try {
            const parsed = JSON.parse(text);
            // Support both {tasks: [...]} and [...] formats
            const tasks = Array.isArray(parsed) ? parsed : parsed.tasks;
            if (!Array.isArray(tasks)) {
                throw new Error('Expected an array of tasks or object with "tasks" array');
            }
            setParsedTasks(tasks);
        } catch (e) {
            setParseError(e instanceof Error ? e.message : 'Invalid JSON');
        }
    };

    const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (event) => {
            const text = event.target?.result as string;
            handleJsonChange(text);
        };
        reader.readAsText(file);
    };

    const handleImport = async () => {
        if (parsedTasks.length === 0) return;

        setIsImporting(true);
        try {
            const response = await importTasks({
                tasks: parsedTasks,
                skip_duplicates: skipDuplicates
            });
            setImportResult(response.data);
            if (response.data.success && response.data.created.length > 0) {
                showToast(`Successfully imported ${response.data.created.length} tasks!`, 'success');
                onSuccess();
            } else if (response.data.success && response.data.created.length === 0) {
                showToast('No new tasks were imported (duplicates skipped).', 'info');
            } else {
                showToast('Import completed with some issues.', 'warning');
            }
        } catch (e: any) { // eslint-disable-line @typescript-eslint/no-explicit-any
            // Extract detailed error from FastAPI 422 response
            let errorMessage = 'Import failed';

            if (e.response && e.response.data && e.response.data.detail) {
                const detail = e.response.data.detail;
                if (Array.isArray(detail)) {
                    // FastAPI validation error array
                    errorMessage = detail.map((err: any) => // eslint-disable-line @typescript-eslint/no-explicit-any
                        `${err.loc.join('.')} - ${err.msg}`
                    ).join('\n');
                } else {
                    errorMessage = detail.toString();
                }
            } else if (e instanceof Error) {
                errorMessage = e.message;
            }

            setParseError(errorMessage);
            showToast('Failed to import tasks', 'error');
        } finally {
            setIsImporting(false);
        }
    };

    const [showSchema, setShowSchema] = useState(false);

    const handleClose = () => {
        setJsonInput('');
        setParsedTasks([]);
        setParseError(null);
        setImportResult(null);
        setSkipDuplicates(false);
        setShowSchema(false);
        onClose();
    };

    const taskSchema = `{
  "name": "string",
  "description": "string",
  "base_points": "number",
  "assigned_role": "string (optional, e.g. 'Partner', 'Child')",
  "schedule_type": "string (e.g. 'daily')",
  "default_due_time": "string (HH:MM)",
  "recurrence_min_days": "number (optional)",
  "recurrence_max_days": "number (optional)"
}`;

    const sampleJson = `{
  "tasks": [
    {
      "name": "Breakfast Prep",
      "description": "Help prepare breakfast",
      "base_points": 5,
      "assigned_role": "Child",
      "schedule_type": "daily",
      "default_due_time": "07:30"
    }
  ]
}`;

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text);
        showToast('Copied to clipboard!', 'success');
    };

    return (
        <Modal isOpen={isOpen} onClose={handleClose} title="Import Tasks" size="large">
            <div className="import-tasks-modal">
                <p className="import-description">
                    Paste task JSON below or upload a file. You can export existing tasks to see the format.
                </p>

                <div className="import-actions">
                    <input
                        type="file"
                        accept=".json"
                        ref={fileInputRef}
                        onChange={handleFileUpload}
                        style={{ display: 'none' }}
                    />
                    <button
                        type="button"
                        className="btn btn-secondary"
                        onClick={() => fileInputRef.current?.click()}
                    >
                        📁 Upload File
                    </button>
                    <button
                        type="button"
                        className="btn btn-secondary"
                        onClick={() => handleJsonChange(sampleJson)}
                    >
                        📝 Load Example
                    </button>
                    <button
                        type="button"
                        className="btn btn-secondary"
                        onClick={() => setShowSchema(!showSchema)}
                    >
                        {showSchema ? '🔽 Hide Schema' : 'ℹ️ Show Schema'}
                    </button>
                </div>

                {showSchema && (
                    <div className="schema-container">
                        <div className="schema-block">
                            <div className="schema-header">
                                <h5>Task Object Schema</h5>
                                <button
                                    className="btn-text"
                                    onClick={() => copyToClipboard(taskSchema)}
                                    title="Copy Schema"
                                >
                                    📋
                                </button>
                            </div>
                            <pre>{taskSchema}</pre>
                        </div>
                        <div className="schema-block">
                            <div className="schema-header">
                                <h5>Example JSON</h5>
                                <button
                                    className="btn-text"
                                    onClick={() => copyToClipboard(sampleJson)}
                                    title="Copy Example"
                                >
                                    📋
                                </button>
                            </div>
                            <pre>{sampleJson}</pre>
                        </div>
                    </div>
                )}

                <textarea
                    className="import-textarea"
                    placeholder="Paste JSON here..."
                    value={jsonInput}
                    onChange={(e) => handleJsonChange(e.target.value)}
                    rows={12}
                />

                {parseError && (
                    <div className="import-error">
                        ⚠️ {parseError}
                    </div>
                )}

                {parsedTasks.length > 0 && !importResult && (
                    <div className="import-preview">
                        <h4>Preview: {parsedTasks.length} task(s) to import</h4>
                        <ul className="task-preview-list">
                            {parsedTasks.slice(0, 5).map((task, i) => (
                                <li key={i}>
                                    <strong>{task.name}</strong> — {task.base_points} pts
                                    {task.assigned_role && ` (${task.assigned_role})`}
                                </li>
                            ))}
                            {parsedTasks.length > 5 && (
                                <li className="more-tasks">...and {parsedTasks.length - 5} more</li>
                            )}
                        </ul>

                        <label className="skip-duplicates-label">
                            <input
                                type="checkbox"
                                checked={skipDuplicates}
                                onChange={(e) => setSkipDuplicates(e.target.checked)}
                            />
                            Skip tasks with duplicate names
                        </label>
                    </div>
                )}

                {importResult && (
                    <div className={`import-result ${importResult.success ? 'success' : 'partial'}`}>
                        <h4>{importResult.success ? '✅ Import Complete' : '⚠️ Import Complete with Issues'}</h4>
                        <p>{importResult.summary}</p>
                        {importResult.created.length > 0 && (
                            <details>
                                <summary>Created ({importResult.created.length})</summary>
                                <ul>{importResult.created.map((n, i) => <li key={i}>{n}</li>)}</ul>
                            </details>
                        )}
                        {importResult.skipped.length > 0 && (
                            <details>
                                <summary>Skipped ({importResult.skipped.length})</summary>
                                <ul>{importResult.skipped.map((n, i) => <li key={i}>{n}</li>)}</ul>
                            </details>
                        )}
                        {importResult.errors.length > 0 && (
                            <details open>
                                <summary>Errors ({importResult.errors.length})</summary>
                                <ul className="error-list">{importResult.errors.map((e, i) => <li key={i}>{e}</li>)}</ul>
                            </details>
                        )}
                    </div>
                )}

                <div className="modal-actions">
                    <button type="button" className="btn btn-secondary" onClick={handleClose}>
                        {importResult ? 'Close' : 'Cancel'}
                    </button>
                    {!importResult && (
                        <button
                            type="button"
                            className="btn btn-primary"
                            onClick={handleImport}
                            disabled={parsedTasks.length === 0 || isImporting}
                        >
                            {isImporting ? 'Importing...' : `Import ${parsedTasks.length} Task(s)`}
                        </button>
                    )}
                </div>
            </div>

            <style>{`
                .import-tasks-modal {
                    display: flex;
                    flex-direction: column;
                    gap: 1rem;
                }
                .import-description {
                    color: var(--text-secondary, #aaa);
                    margin: 0;
                }
                .import-actions {
                    display: flex;
                    gap: 0.5rem;
                }
                .import-textarea {
                    width: 100%;
                    font-family: monospace;
                    font-size: 0.875rem;
                    padding: 0.75rem;
                    border: 1px solid var(--border-color, #444);
                    border-radius: 8px;
                    resize: vertical;
                    background: rgba(0, 0, 0, 0.2);
                    color: var(--text-primary, #fff);
                }
                .import-error {
                    color: #ef4444;
                    padding: 0.75rem;
                    background: rgba(239, 68, 68, 0.1);
                    border: 1px solid rgba(239, 68, 68, 0.2);
                    border-radius: 8px;
                    white-space: pre-wrap;
                }
                .import-preview {
                    padding: 1rem;
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 8px;
                    border: 1px solid var(--border-color, #444);
                }
                .import-preview h4 {
                    margin: 0 0 0.5rem 0;
                    color: var(--text-primary, #fff);
                }
                .task-preview-list {
                    margin: 0;
                    padding-left: 1.5rem;
                    color: var(--text-secondary, #ccc);
                }
                .task-preview-list li {
                    margin-bottom: 0.25rem;
                }
                .task-preview-list strong {
                    color: var(--text-primary, #fff);
                }
                .more-tasks {
                    color: var(--text-muted, #888);
                    font-style: italic;
                }
                .skip-duplicates-label {
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                    margin-top: 0.75rem;
                    cursor: pointer;
                    color: var(--text-secondary, #ccc);
                }
                .import-result {
                    padding: 1rem;
                    border-radius: 8px;
                }
                .import-result.success {
                    background: rgba(16, 185, 129, 0.1);
                    border: 1px solid rgba(16, 185, 129, 0.2);
                    color: #d1fae5;
                }
                .import-result.partial {
                    background: rgba(245, 158, 11, 0.1);
                    border: 1px solid rgba(245, 158, 11, 0.2);
                    color: #fef3c7;
                }
                .import-result h4 {
                    margin: 0 0 0.5rem 0;
                }
                .import-result details {
                    margin-top: 0.5rem;
                }
                .import-result summary {
                    cursor: pointer;
                    font-weight: 500;
                }
                .import-result ul {
                    margin: 0.25rem 0 0 0;
                    padding-left: 1.5rem;
                    max-height: 100px;
                    overflow-y: auto;
                }
                .error-list li {
                    color: #ef4444;
                }
                .modal-actions {
                    display: flex;
                    justify-content: flex-end;
                    gap: 0.75rem;
                    margin-top: 0.5rem;
                }
                .schema-container {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 1rem;
                    background: rgba(0, 0, 0, 0.2);
                    padding: 1rem;
                    border-radius: 8px;
                    margin-bottom: 0.5rem;
                    border: 1px solid var(--border-color, #444);
                }
                .schema-block {
                    display: flex;
                    flex-direction: column;
                }
                .schema-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 0.5rem;
                }
                .schema-header h5 {
                    margin: 0;
                    color: var(--text-primary, #fff);
                }
                .schema-block pre {
                    background: rgba(0, 0, 0, 0.3);
                    color: #e2e8f0;
                    padding: 0.75rem;
                    border-radius: 6px;
                    border: 1px solid var(--border-color, #334155);
                    overflow-x: auto;
                    font-size: 0.75rem;
                    margin: 0;
                    height: 200px;
                }
                .btn-text {
                    background: none;
                    border: none;
                    cursor: pointer;
                    font-size: 1.25rem;
                    padding: 0.25rem;
                    opacity: 0.8;
                    transition: opacity 0.2s;
                    color: inherit;
                }
                .btn-text:hover {
                    opacity: 1;
                    transform: scale(1.1);
                }
            `}</style>
        </Modal>
    );
};

export default ImportTasksModal;
