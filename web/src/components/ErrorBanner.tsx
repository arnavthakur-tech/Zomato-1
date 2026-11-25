interface ErrorBannerProps {
  title: string;
  message: string;
  errors?: string[];
}

export function ErrorBanner({ title, message, errors = [] }: ErrorBannerProps) {
  return (
    <div className="rounded-lg border border-[#f85149] bg-[rgba(248,81,73,0.08)] p-4">
      <p className="text-sm font-semibold text-[#f85149]">{title}</p>
      <p className="mt-1 text-sm text-on-surface">{message}</p>
      {errors.length > 0 && (
        <ul className="mt-2 list-inside list-disc text-sm text-secondary">
          {errors.map((err) => (
            <li key={err}>{err}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
