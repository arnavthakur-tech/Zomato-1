const HERO_IMG =
  "https://lh3.googleusercontent.com/aida-public/AB6AXuD1A1WsPA8dHmDKWG_aOLXbdl6vig6ElXIdTgTNum7_qTwA8zo4-F2FSadxDmBBN_44x_vz5NECm0nm34R3d5WSA9rCyu6yyGPOuUaf8NOiOYcdYdTPSWVZn9LMvBHHRd8QXlBZ_3W8aVgs7owqZsAHn4b3qn93ar55X9c9fFcd2ZZI_cJl53rst1KK3vbAWzqU81FtE1wLsZ65vx1uGpW6Qom_7e2WQxRzReA2XlsJ";

export function HeroBanner({ rowCount }: { rowCount: number }) {
  return (
    <div className="relative mb-6 overflow-hidden rounded-xl border border-surface-variant bg-surface-container-lowest shadow-xl">
      <div
        className="pointer-events-none absolute inset-0 bg-cover bg-center opacity-20 mix-blend-luminosity saturate-50"
        style={{ backgroundImage: `url('${HERO_IMG}')` }}
      />
      <div className="relative z-10 flex flex-col justify-between gap-6 bg-gradient-to-r from-surface-container-lowest via-surface-container-lowest/90 to-transparent px-6 py-8 sm:px-8 sm:py-10 md:flex-row md:items-end">
        <div className="max-w-2xl">
          <div className="mb-2 flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center gap-1.5 rounded bg-primary-container/15 px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wider text-primary">
              <span className="h-1.5 w-1.5 animate-br-pulse rounded-full bg-primary-container" />
              Ready to search
            </span>
          </div>
          <h1 className="font-headline text-3xl font-bold tracking-tight text-on-surface sm:text-4xl">
            Find your next table
          </h1>
          <p className="mt-1 max-w-xl text-base leading-relaxed text-secondary">
            Set your preferences, get a shortlist of real restaurants, and see
            why each pick fits.
          </p>
        </div>
        <div className="flex items-center gap-4 self-start rounded-lg border border-surface-variant bg-surface-container/80 px-4 py-2.5 backdrop-blur-sm md:self-auto">
          <div className="flex flex-col">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-secondary">
              Restaurants
            </span>
            <span className="font-mono text-xs font-semibold text-on-surface">
              {rowCount.toLocaleString()} available
            </span>
          </div>
          <div className="h-6 w-px bg-surface-variant" />
          <span className="text-xl text-primary-container" aria-hidden>
            ✦
          </span>
        </div>
      </div>
    </div>
  );
}
