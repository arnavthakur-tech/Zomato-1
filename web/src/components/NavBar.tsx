"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export function NavBar() {
  const pathname = usePathname();
  const recommendActive = pathname === "/";
  const aboutActive = pathname === "/about";

  return (
    <header className="fixed left-0 right-0 top-0 z-50 border-b border-surface-variant bg-surface-container-lowest/85 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-shell items-center justify-between px-4 sm:px-6">
        <Link href="/" className="group flex items-center gap-3">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-primary-container to-primary text-sm font-bold text-on-primary-container">
            BR
          </span>
          <span className="font-headline text-base font-semibold tracking-tight text-on-surface transition-colors group-hover:text-primary">
            BiteRank
          </span>
        </Link>

        <div className="flex items-center gap-3 sm:gap-6">
          <nav className="flex items-center gap-1 sm:gap-2">
            <Link
              href="/about"
              className={`rounded-t px-3 py-1.5 text-xs font-medium tracking-wide transition-all ${
                aboutActive
                  ? "border-b-2 border-primary-container bg-surface-container-high text-primary"
                  : "text-on-surface-variant hover:bg-surface-container hover:text-on-surface"
              }`}
            >
              About
            </Link>
            <Link
              href="/"
              className={`rounded-t px-3 py-1.5 text-xs font-medium tracking-wide transition-all ${
                recommendActive
                  ? "border-b-2 border-primary-container bg-surface-container-high text-primary"
                  : "text-on-surface-variant hover:bg-surface-container hover:text-on-surface"
              }`}
            >
              Recommend
            </Link>
          </nav>
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-sm font-bold text-on-primary">
            ◆
          </div>
        </div>
      </div>
    </header>
  );
}
