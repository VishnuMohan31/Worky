import React, { useState } from 'react';

interface SelectProps {
  children: React.ReactNode;
  value?: string;
  onValueChange?: (value: string) => void;
}

interface SelectTriggerProps {
  children: React.ReactNode;
  className?: string;
}

interface SelectContentProps {
  children: React.ReactNode;
  className?: string;
}

interface SelectItemProps {
  children: React.ReactNode;
  value: string;
  className?: string;
}

interface SelectValueProps {
  placeholder?: string;
  className?: string;
}

const SelectContext = React.createContext<{
  open: boolean;
  setOpen: (open: boolean) => void;
  value?: string;
  onValueChange?: (value: string) => void;
}>({
  open: false,
  setOpen: () => {},
  value: undefined,
  onValueChange: () => {}
});

export const Select: React.FC<SelectProps> = ({ children, value, onValueChange }) => {
  const [open, setOpen] = useState(false);
  
  return (
    <SelectContext.Provider value={{ open, setOpen, value, onValueChange }}>
      <div className="relative">
        {children}
      </div>
    </SelectContext.Provider>
  );
};

export const SelectTrigger: React.FC<SelectTriggerProps> = ({ children, className = '' }) => {
  const { open, setOpen } = React.useContext(SelectContext);
  
  return (
    <button
      type="button"
      onClick={() => setOpen(!open)}
      className={`flex h-10 w-full items-center justify-between rounded-md border border-gray-300 bg-white px-3 py-2 text-sm placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:cursor-not-allowed disabled:opacity-50 ${className}`}
    >
      {children}
      <svg className="h-4 w-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
      </svg>
    </button>
  );
};

export const SelectValue: React.FC<SelectValueProps> = ({ placeholder, className = '' }) => {
  const { value } = React.useContext(SelectContext);
  
  return (
    <span className={className}>
      {value || placeholder}
    </span>
  );
};

export const SelectContent: React.FC<SelectContentProps> = ({ children, className = '' }) => {
  const { open, setOpen } = React.useContext(SelectContext);
  
  if (!open) return null;
  
  return (
    <>
      <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
      <div className={`absolute top-full left-0 z-50 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg ${className}`}>
        {children}
      </div>
    </>
  );
};

export const SelectItem: React.FC<SelectItemProps> = ({ children, value, className = '' }) => {
  const { onValueChange, setOpen } = React.useContext(SelectContext);
  
  const handleClick = () => {
    onValueChange?.(value);
    setOpen(false);
  };
  
  return (
    <div
      onClick={handleClick}
      className={`px-3 py-2 text-sm cursor-pointer hover:bg-gray-100 ${className}`}
    >
      {children}
    </div>
  );
};