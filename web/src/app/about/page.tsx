import Link from "next/link";

const ABOUT_IMG =
  "https://lh3.googleusercontent.com/aida-public/AB6AXuA5FgdbHZsVJcLc6U63HIwsKrzDJ3unzrLW7s89-pgHCICRfwVa9FiEMA9gMfaTczPPdxd99RXQPAuL2U9zo-ITpft4DIcUbWpO_pMexJtYVQbb0lpUTrWrbe0jn6Xf3CMq3ImgkGvGmhL99-z3kR1jVwWddbxf-n2Dppi8Aq6om1Zwb7z0P1euZZMamXhHND_nESHsFrgfBmxvgwtSUNH39H13VX7p8QQ7Hh8tIs2A";

export default function AboutPage() {
  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-10">
      <div className="relative h-56 overflow-hidden rounded-xl border border-surface-variant bg-surface-container-low shadow-xl sm:h-64">
        <div
          className="absolute inset-0 bg-cover bg-center transition-transform duration-700 hover:scale-[1.02]"
          style={{ backgroundImage: `url('${ABOUT_IMG}')` }}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-surface via-surface/60 to-transparent" />
        <div className="absolute bottom-6 left-6 right-6">
          <div className="flex flex-col gap-1.5">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-primary">
              About BiteRank
            </span>
            <span className="font-headline text-xl font-semibold text-on-surface">
              Find restaurants that fit you
            </span>
          </div>
        </div>
      </div>

      <header className="flex flex-col gap-3">
        <h1 className="font-headline text-3xl font-bold tracking-tight text-on-surface sm:text-4xl">
          How BiteRank works
        </h1>
        <p className="max-w-2xl text-base leading-relaxed text-secondary">
          Tell us what you want, we narrow the real restaurant list, then we
          rank the best matches and explain why each one fits.
        </p>
      </header>

      <div className="flex flex-col gap-4 rounded-xl bg-surface-container-low p-6 shadow-md">
        <span className="text-xs font-medium uppercase tracking-wider text-secondary">
          Three simple stages
        </span>
        <div className="grid grid-cols-3 gap-2 pt-1 text-center">
          <div>
            <div className="font-headline text-sm font-semibold text-on-surface">
              1. Your picks
            </div>
            <div className="mt-1 text-[11px] text-secondary">
              Location, budget, cuisine
            </div>
          </div>
          <div>
            <div className="font-headline text-sm font-semibold text-on-surface">
              2. We filter
            </div>
            <div className="mt-1 text-[11px] text-secondary">
              Real Zomato places only
            </div>
          </div>
          <div>
            <div className="font-headline text-sm font-semibold text-on-surface">
              3. We rank
            </div>
            <div className="mt-1 text-[11px] text-secondary">
              Best fits + reasons
            </div>
          </div>
        </div>
      </div>

      <section className="flex flex-col gap-6" aria-label="How BiteRank works">
        <Step
          num="01"
          stage="STAGE I"
          title="You tell us what you need"
          badge="Your filters"
          body="Choose a location, budget (Low, Medium, or High), cuisine, and a minimum rating. You can also add a short note — like family-friendly, quiet, or date night — so the ranking can match the vibe you want."
        >
          <div className="flex flex-wrap gap-2 pt-2">
            {["Location", "Budget", "Cuisine", "Minimum rating"].map((t) => (
              <span
                key={t}
                className="rounded bg-surface-container-lowest px-2.5 py-1 text-xs font-medium text-secondary"
              >
                {t}
              </span>
            ))}
          </div>
        </Step>

        <Step
          num="02"
          stage="STAGE II"
          title="We filter real restaurants first"
          badge="Real places only"
          body="BiteRank looks through verified Zomato restaurant records and keeps only the ones that match your filters. Places that don’t exist in the data never show up."
        >
          <div className="mt-3 rounded-lg bg-surface-container-lowest p-3.5">
            <p className="text-[13px] leading-relaxed text-secondary">
              Example: if you pick Bangalore, medium budget, Italian, and 4.0+
              rating, we only keep restaurants that match those rules — before
              any ranking happens.
            </p>
          </div>
        </Step>

        <Step
          num="03"
          stage="STAGE III"
          title="We rank the shortlist and explain why"
          badge="Clear reasons"
          accent
          body="From that shortlist, BiteRank ranks the best options for you and writes a short reason for each pick — so you can see why it fits your preferences."
        >
          <div className="mt-3 flex items-start gap-3 rounded bg-surface-container-lowest p-3.5">
            <span className="mt-0.5 text-primary" aria-hidden>
              “
            </span>
            <div className="flex flex-col gap-1">
              <span className="text-[13px] italic text-on-surface">
                Strong rating and casual setting that fits a family outing on a
                medium budget.
              </span>
              <span className="text-xs text-secondary">
                Example of a short explanation you’ll see on a card
              </span>
            </div>
          </div>
        </Step>
      </section>

      <div className="relative flex flex-col items-center gap-5 overflow-hidden rounded-xl bg-surface-container-high p-6 shadow-lg sm:flex-row sm:items-start sm:p-8">
        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-primary text-xl text-on-primary">
          ✓
        </div>
        <div className="flex flex-1 flex-col gap-1.5 text-center sm:text-left">
          <span className="font-headline text-base font-semibold text-on-surface">
            Only real restaurants
          </span>
          <p className="text-sm font-medium text-on-surface">
            Every recommendation comes from the Zomato dataset — never made-up
            places.
          </p>
          <p className="text-[13px] leading-relaxed text-secondary">
            Names, ratings, and costs come from the data. If something doesn’t
            match a real restaurant, it won’t appear in your shortlist.
          </p>
        </div>
      </div>

      <div className="flex flex-col items-center justify-between gap-4 rounded-xl bg-surface-container-low p-6 sm:flex-row">
        <p className="text-sm text-secondary">Ready to find your next table?</p>
        <Link
          href="/"
          className="inline-flex w-full items-center justify-center gap-2 rounded bg-primary-container px-6 py-3 text-xs font-semibold tracking-wide text-on-primary-container shadow-md transition hover:bg-primary hover:text-on-primary sm:w-auto"
        >
          Go to Recommend →
        </Link>
      </div>
    </div>
  );
}

function Step({
  num,
  stage,
  title,
  badge,
  body,
  children,
  accent,
}: {
  num: string;
  stage: string;
  title: string;
  badge: string;
  body: string;
  children?: React.ReactNode;
  accent?: boolean;
}) {
  return (
    <article className="group flex flex-col items-start gap-6 rounded-xl bg-surface-container-low p-6 shadow-sm transition-colors duration-200 hover:bg-surface-container sm:p-8 md:flex-row">
      <div className="flex w-full items-center justify-between gap-3 md:w-auto md:shrink-0 md:flex-col">
        <div
          className={`rounded bg-surface-container-lowest px-3 py-2 font-mono text-[28px] font-bold ${
            accent ? "text-primary" : "text-primary-container"
          }`}
        >
          {num}
        </div>
        <span className="text-[11px] font-semibold uppercase tracking-widest text-secondary md:[writing-mode:vertical-rl] md:rotate-180">
          {stage}
        </span>
      </div>
      <div className="flex flex-1 flex-col gap-4">
        <div className="flex flex-col justify-between gap-2 sm:flex-row sm:items-center">
          <h2 className="font-headline text-xl font-semibold text-on-surface">
            {title}
          </h2>
          <div className="inline-flex items-center gap-1.5 self-start rounded bg-surface-container-highest px-2.5 py-1">
            <span className="text-xs text-on-surface">{badge}</span>
          </div>
        </div>
        <p className="text-sm leading-relaxed text-secondary">{body}</p>
        {children}
      </div>
    </article>
  );
}
