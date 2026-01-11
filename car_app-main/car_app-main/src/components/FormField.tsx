import { forwardRef, ReactNode } from 'react';

interface FormFieldProps {
  label: string;
  error?: string;
  required?: boolean;
  children: ReactNode;
  description?: string;
}

export const FormField = forwardRef<HTMLDivElement, FormFieldProps>(
  ({ label, error, required, children, description }, ref) => {
    return (
      <div ref={ref} className="space-y-2">
        <label className="block text-sm font-medium text-white">
          {label}
          {required && <span className="text-brand-gold ml-1">*</span>}
        </label>
        {description && (
          <p className="text-xs text-gray-400">{description}</p>
        )}
        {children}
        {error && (
          <p className="text-red-400 text-xs mt-1">{error}</p>
        )}
      </div>
    );
  }
);