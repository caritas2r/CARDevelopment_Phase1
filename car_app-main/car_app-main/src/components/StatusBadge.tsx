interface StatusBadgeProps {
  status: string;
  type?: 'default' | 'success' | 'warning' | 'error';
}

export function StatusBadge({ status, type = 'default' }: StatusBadgeProps) {
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
      case 'complete':
      case 'delivered':
      case 'succeeded':
        return 'bg-green-900/50 text-green-400 border-green-400/30';
      case 'pending':
      case 'intake':
      case 'scheduled':
      case 'researching':
        return 'bg-yellow-900/50 text-yellow-400 border-yellow-400/30';
      case 'suspended':
      case 'canceled':
      case 'failed':
        return 'bg-red-900/50 text-red-400 border-red-400/30';
      case 'in_progress':
      case 'build':
      case 'sourcing':
        return 'bg-brand-green/50 text-brand-green-light border-brand-green-light/30';
      default:
        return 'bg-gray-900/50 text-gray-400 border-gray-400/30';
    }
  };

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getStatusColor(status)}`}
    >
      {status.replace('_', ' ').toUpperCase()}
    </span>
  );
}