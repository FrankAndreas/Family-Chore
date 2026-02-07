import React, { useState, useRef } from 'react';
import Modal from './Modal';
import type { TaskImportItem, ImportResult } from '../api';
import { importTasks } from '../api';
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
                onSuccess();
            }
        } catch (e) {
            setParseError(e instanceof Error ? e.message : 'Import failed');
        } finally {
            setIsImporting(false);
        }
    };

    const handleClose = () => {
        setJsonInput('');
        setParsedTasks([]);
        setParseError(null);
        setImportResult(null);
        setSkipDuplicates(false);
        onClose();
    };

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
                </div>

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
                    color: var(--text-secondary, #666);
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
                    border: 1px solid var(--border-color, #ddd);
                    border-radius: 8px;
                    resize: vertical;
                    background: var(--input-bg, #f9f9f9);
                }
                .import-error {
                    color: var(--color-error, #dc2626);
                    padding: 0.75rem;
                    background: #fee2e2;
                    border-radius: 8px;
                }
                .import-preview {
                    padding: 1rem;
                    background: var(--bg-secondary, #f5f5f5);
                    border-radius: 8px;
                }
                .import-preview h4 {
                    margin: 0 0 0.5rem 0;
                }
                .task-preview-list {
                    margin: 0;
                    padding-left: 1.5rem;
                }
                .task-preview-list li {
                    margin-bottom: 0.25rem;
                }
                .more-tasks {
                    color: var(--text-secondary, #666);
                    font-style: italic;
                }
                .skip-duplicates-label {
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                    margin-top: 0.75rem;
                    cursor: pointer;
                }
                .import-result {
                    padding: 1rem;
                    border-radius: 8px;
                }
                .import-result.success {
                    background: #d1fae5;
                }
                .import-result.partial {
                    background: #fef3c7;
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
                    color: var(--color-error, #dc2626);
                }
                .modal-actions {
                    display: flex;
                    justify-content: flex-end;
                    gap: 0.75rem;
                    margin-top: 0.5rem;
                }
            `}</style>
        </Modal>
    );
};

export default ImportTasksModal;
