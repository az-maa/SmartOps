// src/components/common/Loading.jsx
import React from 'react';
import { Loader } from 'lucide-react';

const Loading = ({ size = 'md', text = 'Loading...' }) => {
  const sizes = {
    sm: 'w-6 h-6',
    md: 'w-10 h-10',
    lg: 'w-16 h-16'
  };

  return (
    <div className="flex flex-col items-center justify-center py-12">
      <Loader className={`${sizes[size]} animate-spin text-blue-600 mb-4`} />
      {text && <p className="text-gray-600">{text}</p>}
    </div>
  );
};

export default Loading;