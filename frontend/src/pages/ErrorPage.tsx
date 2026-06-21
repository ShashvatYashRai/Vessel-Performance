import { useRouteError, isRouteErrorResponse, Link } from "react-router-dom";
import { AlertTriangle } from "lucide-react";

export default function ErrorPage() {
  const error = useRouteError();

  let title = "Unexpected Error";
  let message = "Something went wrong. Please try again.";

  if (isRouteErrorResponse(error)) {
    title = error.status === 404 ? "Page Not Found" : `Error ${error.status}`;
    message = error.statusText || message;
  } else if (error instanceof Error) {
    message = error.message;
  }

  return (
    <div className="dark min-h-screen bg-background text-foreground flex items-center justify-center px-4">
      <div className="text-center max-w-md">
        <div className="inline-flex items-center justify-center h-16 w-16 rounded-2xl bg-destructive/10 border border-destructive/20 mb-6 mx-auto">
          <AlertTriangle className="h-8 w-8 text-destructive" />
        </div>
        <h1 className="text-2xl font-bold tracking-tight mb-2">{title}</h1>
        <p className="text-sm text-muted-foreground mb-8">{message}</p>
        <Link
          to="/"
          className="inline-flex items-center gap-2 bg-[hsl(210,70%,50%)] hover:bg-[hsl(210,70%,55%)] text-white text-sm font-semibold py-2.5 px-5 rounded-lg transition-all duration-200 shadow-[0_4px_12px_hsl(210,70%,50%/0.2)]"
        >
          Return Home
        </Link>
      </div>
    </div>
  );
}
