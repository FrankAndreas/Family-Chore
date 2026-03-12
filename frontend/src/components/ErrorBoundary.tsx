import { Component, type ErrorInfo, type ReactNode } from 'react';

interface Props {
    children: ReactNode;
}

interface State {
    hasError: boolean;
    error: Error | null;
}

class ErrorBoundary extends Component<Props, State> {
    public state: State = {
        hasError: false,
        error: null
    };

    public static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error };
    }

    public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error('Uncaught error:', error, errorInfo);
    }

    private handleTryAgain = () => {
        this.setState({ hasError: false, error: null });
    };

    private handleGoBack = () => {
        this.setState({ hasError: false, error: null });
        window.history.back();
    };

    public render() {
        if (this.state.hasError) {
            return (
                <div className="error-boundary-container flex-col-center p-4 mx-auto mt-5 text-center" style={{ maxWidth: '480px' }}>
                    <div className="glass-card" style={{ padding: 'var(--spacing-xl)', width: '100%' }}>
                        <div style={{ fontSize: '3rem', marginBottom: 'var(--spacing-md)' }} aria-hidden="true">😵</div>
                        <h1 style={{ fontSize: 'var(--font-size-xl)', fontWeight: 700, marginBottom: 'var(--spacing-xs)' }}>
                            Oops! Something went wrong
                        </h1>
                        <p className="text-secondary" style={{ marginBottom: 'var(--spacing-md)' }}>
                            We&apos;re sorry, but an unexpected error occurred. You can try again, go back, or reload the page.
                        </p>
                        {this.state.error && (
                            <details style={{ marginBottom: 'var(--spacing-md)', textAlign: 'left' }}>
                                <summary className="text-secondary" style={{ cursor: 'pointer', fontSize: 'var(--font-size-sm)' }}>
                                    Show error details
                                </summary>
                                <div
                                    className="bg-secondary rounded-md text-sm"
                                    style={{
                                        padding: 'var(--spacing-sm)',
                                        marginTop: 'var(--spacing-xs)',
                                        fontFamily: 'monospace',
                                        maxHeight: '8rem',
                                        overflowY: 'auto',
                                        borderTop: '1px solid var(--border-color)',
                                        color: '#ff4d4f',
                                        wordBreak: 'break-word'
                                    }}
                                >
                                    {this.state.error.toString()}
                                </div>
                            </details>
                        )}
                        <div style={{ display: 'flex', gap: 'var(--spacing-xs)', flexDirection: 'column' }}>
                            <button
                                onClick={this.handleTryAgain}
                                className="btn btn-primary w-full"
                            >
                                🔄 Try Again
                            </button>
                            <button
                                onClick={this.handleGoBack}
                                className="btn btn-secondary w-full"
                            >
                                ← Go Back
                            </button>
                            <button
                                onClick={() => window.location.reload()}
                                className="btn btn-secondary w-full"
                            >
                                🔃 Reload Page
                            </button>
                        </div>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
