interface BadgeProps {
  label: string;
  className?: string;
}

export function Badge({ label, className = "bg-gray-100 text-gray-700" }: BadgeProps) {
  return <span className={`badge ${className}`}>{label}</span>;
}
