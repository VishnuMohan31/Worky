import React from 'react';

interface DecisionBadgeProps {
  status: string;
  className?: string;
}

const DecisionBadge: React.FC<DecisionBadgeProps> = ({ status, className = '' }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Active':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'Canceled':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'Postponed':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'On-Hold':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'Closed':
        return 'bg-gray-100 text-gray-800 border-gray-200';
      default:
        return 'bg-blue-100 text-blue-800 border-blue-200';
    }
  };

  return (
    <span
      className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(
        status
      )} ${className}`}
    >
      <svg
        className="w-3 h-3 mr-1"
        fill="currentColor"
        viewBox="0 0 20 20"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          fillRule="evenodd"
          d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
          clipRule="evenodd"
        />
      </svg>
      {status}
    </span>
  );
};

export default DecisionBadge;