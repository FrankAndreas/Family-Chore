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

    public render() {
        if (this.state.hasError) {
            return (
                <div className="error-boundary-container flex-col-center border-2 border-dashed border-red-500 rounded-md p-4 bg-secondary max-w-sm w-full mx-auto mt-5 text-center">
                    <div className="glass-card error-card">
                        <div className="text-6xl mb-4">😵</div>
                        <h1 className="text-xl font-bold mb-2 text-danger">Oops! Something went wrong</h1>
                        <p className="text-secondary mb-3">
                            We're sorry, but an unexpected error occurred. Please try reloading the page.
                        </p>
                        {this.state.error && (
                            <div className="error-details bg-dark p-3 rounded-md text-sm font-mono mb-3 text-left overflow-auto max-h-32 text-danger border-t border-color">
                                {this.state.error.toString()}
                            </div>
                        )}
                        <button
                            onClick={() => window.location.reload()}
                            className="btn btn-primary w-full mt-3"
                        >
                            Reload Page
                        </button>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
