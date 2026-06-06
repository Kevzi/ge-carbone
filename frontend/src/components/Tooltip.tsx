import type { ReactNode } from 'react'

interface TooltipProps {
    content: ReactNode
    position?: 'top' | 'bottom' | 'left' | 'right'
    children: ReactNode
    className?: string
}

export default function Tooltip({ content, position = 'top', children, className = '' }: TooltipProps) {
    if (!content && content !== 0) return <>{children}</>

    const positionClasses = {
        top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
        bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
        left: 'right-full top-1/2 -translate-y-1/2 mr-2',
        right: 'left-full top-1/2 -translate-y-1/2 ml-2',
    }

    const arrowClasses = {
        top: 'top-full left-1/2 -translate-x-1/2 border-t-[var(--text-main)]',
        bottom: 'bottom-full left-1/2 -translate-x-1/2 border-b-[var(--text-main)]',
        left: 'left-full top-1/2 -translate-y-1/2 border-l-[var(--text-main)]',
        right: 'right-full top-1/2 -translate-y-1/2 border-r-[var(--text-main)]',
    }

    return (
        <span className={`relative group inline-block ${className}`} tabIndex={0}>
            {children}
            <div 
                role="tooltip"
                className={`absolute ${positionClasses[position]} w-max max-w-xs px-3 py-2 text-sm rounded-md shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible group-focus-within:opacity-100 group-focus-within:visible transition-all duration-200 break-words whitespace-normal`}
                style={{ 
                    backgroundColor: 'var(--text-main, #1e293b)', 
                    color: 'var(--bg-primary, #ffffff)',
                    zIndex: 'var(--z-tooltip, 50)'
                }}
            >
                {content}
                <div 
                    className={`absolute w-0 h-0 border-4 border-transparent ${arrowClasses[position]}`}
                />
            </div>
        </span>
    )
}
