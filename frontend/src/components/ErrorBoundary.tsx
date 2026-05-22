import { Component, type ErrorInfo, type ReactNode } from 'react';
import { useTranslation } from 'react-i18next';
import './ErrorBoundary.css';

interface Props {
    children: ReactNode;
}

interface State {
    hasError: boolean;
    error: Error | null;
}

// Functional inner component to access useTranslation hook
function ErrorDisplay({ error, onTryAgain, onGoBack }: {
    error: Error | null;
    onTryAgain: () => void;
    onGoBack: () => void;
}) {
    const { t } = useTranslation();

    return (
        <div className="error-boundary-container">
            <div className="glass-card" style={{ padding: 'var(--spacing-xl)', width: '100%' }}>
                <div style={{ fontSize: '3rem', marginBottom: 'var(--spacing-md)' }} aria-hidden="true">😵</div>
                <h1 style={{ fontSize: 'var(--font-size-xl)', fontWeight: 700, marginBottom: 'var(--spacing-xs)' }}>
                    {t('errorBoundary.title', 'Oops! Something went wrong')}
                </h1>
                <p style={{ color: 'var(--text-secondary)', marginBottom: 'var(--spacing-md)' }}>
                    {t('errorBoundary.description', "We're sorry, but an unexpected error occurred. You can try again, go back, or reload the page.")}
                </p>
                {error && (
                    <details style={{ marginBottom: 'var(--spacing-md)', textAlign: 'left' }}>
                        <summary style={{ cursor: 'pointer', fontSize: 'var(--font-size-sm)', color: 'var(--text-secondary)' }}>
                            {t('errorBoundary.showDetails', 'Show error details')}
                        </summary>
                        <div className="error-boundary-detail">
                            {error.toString()}
                        </div>
                    </details>
                )}
                <div className="error-boundary-actions">
                    <button onClick={onTryAgain} className="btn btn-primary">
                        🔄 {t('errorBoundary.tryAgain', 'Try Again')}
                    </button>
                    <button onClick={onGoBack} className="btn btn-secondary">
                        ← {t('errorBoundary.goBack', 'Go Back')}
                    </button>
                    <button onClick={() => window.location.reload()} className="btn btn-secondary">
                        🔃 {t('errorBoundary.reloadPage', 'Reload Page')}
                    </button>
                </div>
            </div>
        </div>
    );
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
                <ErrorDisplay
                    error={this.state.error}
                    onTryAgain={this.handleTryAgain}
                    onGoBack={this.handleGoBack}
                />
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
