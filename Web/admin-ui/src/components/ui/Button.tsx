import React from 'react';
import { cn } from '../../lib/utils';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'outline' | 'ghost' | 'danger';
    size?: 'sm' | 'md' | 'lg';
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
    ({ className, variant = 'primary', size = 'md', ...props }, ref) => {
        return (
            <button
                ref={ref}
                className={cn(
                    "inline-flex items-center justify-center whitespace-nowrap text-sm font-sans font-medium transition-all cursor-pointer",
                    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-[var(--color-lucky-gold)] disabled:pointer-events-none disabled:opacity-50",
                    "rounded-md",
                    {
                        'bg-[var(--color-vietlott-red)] text-white border border-transparent hover:bg-[var(--color-vietlott-red-dark)] shadow-sm active:scale-[0.98]': variant === 'primary',
                        'bg-white text-[var(--color-text-main)] border border-gray-300 hover:bg-gray-50': variant === 'outline',
                        'border-transparent hover:bg-gray-100 text-[var(--color-text-main)]': variant === 'ghost',
                        'bg-red-600 text-white border-transparent hover:bg-red-700 active:scale-[0.98]': variant === 'danger',
                        'h-9 px-4 py-2': size === 'md',
                        'h-8 px-3 text-xs': size === 'sm',
                        'h-11 px-8 text-base': size === 'lg',
                    },
                    className
                )}
                {...props}
            />
        );
    }
);
Button.displayName = 'Button';
