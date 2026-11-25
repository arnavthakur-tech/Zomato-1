import { NavBar } from "./NavBar";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col bg-surface">
      <NavBar />
      <main className="mx-auto w-full max-w-shell flex-1 px-4 pb-10 pt-20 sm:px-6">
        {children}
      </main>
      <footer className="w-full border-t border-surface-variant bg-surface-container-lowest py-8">
        <div className="mx-auto flex max-w-shell flex-col items-center justify-between gap-4 px-4 text-center sm:flex-row sm:px-6 sm:text-left">
          <p className="flex items-center gap-2 text-sm text-secondary">
            <span className="text-primary" aria-hidden>
              ✓
            </span>
            Recommendations are grounded in dataset restaurants — never invented.
          </p>
          <p className="font-mono text-xs text-secondary">
            © 2024 BiteRank Intelligence · Powered by Zomato dataset corpus
          </p>
        </div>
      </footer>
    </div>
  );
}
