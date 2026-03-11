import type { ReactNode } from 'react';

interface DataCardProps {
  title: string;
  children: ReactNode;
  className?: string;
}

export function DataCard({ title, children, className = '' }: DataCardProps) {
  return (
    <div className={`data-card ${className}`}>
      <h3 className="text-xs font-medium text-pitwall-text-dim uppercase tracking-wider mb-3">
        {title}
      </h3>
      {children}
    </div>
  );
}
