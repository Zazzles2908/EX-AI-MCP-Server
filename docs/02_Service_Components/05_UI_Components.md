# UI Components

## Purpose & Responsibility

This component provides a React-based UI component library with a consistent design system for building user interfaces across the EXAI MCP Server platform.

## Architecture

### Component Structure

```
src/components/
├── ui/               # Base UI primitives
│   ├── Button.tsx
│   ├── Input.tsx
│   ├── Modal.tsx
│   └── index.ts
├── forms/            # Form-specific components
│   ├── FormField.tsx
│   ├── FormSelect.tsx
│   └── FormToggle.tsx
├── layout/           # Layout components
│   ├── Header.tsx
│   ├── Sidebar.tsx
│   └── Panel.tsx
└── features/         # Feature-specific components
    ├── ChatInterface/
    ├── ModelSelector/
    └── FileManager/
```

## Core Components

### Button Component

```typescript
// components/ui/Button.tsx
import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', isLoading, children, ...props }, ref) => {
    const baseStyles = 'inline-flex items-center justify-center rounded-md font-medium transition-colors';
    
    const variantStyles = {
      primary: 'bg-blue-600 text-white hover:bg-blue-700',
      secondary: 'bg-gray-600 text-white hover:bg-gray-700',
      outline: 'border border-gray-300 bg-white hover:bg-gray-50',
      ghost: 'hover:bg-gray-100',
    };
    
    const sizeStyles = {
      sm: 'h-9 px-3 text-sm',
      md: 'h-10 px-4 py-2',
      lg: 'h-11 px-8 text-lg',
    };
    
    return (
      <button
        className={`${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${className || ''}`}
        ref={ref}
        disabled={isLoading}
        {...props}
      >
        {isLoading && <span className="mr-2">⏳</span>}
        {children}
      </button>
    );
  }
);
```

### Input Component

```typescript
// components/ui/Input.tsx
import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: string;
  label?: string;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, error, label, ...props }, ref) => {
    return (
      <div className="space-y-2">
        {label && (
          <label className="text-sm font-medium text-gray-700">
            {label}
          </label>
        )}
        <input
          className={`
            w-full px-3 py-2 border rounded-md
            focus:outline-none focus:ring-2 focus:ring-blue-500
            ${error ? 'border-red-500' : 'border-gray-300'}
            ${className || ''}
          `}
          ref={ref}
          {...props}
        />
        {error && (
          <p className="text-sm text-red-600">{error}</p>
        )}
      </div>
    );
  }
);
```

### Modal Component

```typescript
// components/ui/Modal.tsx
import React from 'react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
}

export const Modal: React.FC<ModalProps> = ({ isOpen, onClose, title, children }) => {
  if (!isOpen) return null;
  
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black bg-opacity-50"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="relative bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
        {title && (
          <h2 className="text-xl font-semibold mb-4">{title}</h2>
        )}
        {children}
      </div>
    </div>
  );
};
```

## Theme System

### Theme Provider

```typescript
// providers/ThemeProvider.tsx
import React, { createContext, useContext, useState } from 'react';

interface Theme {
  colors: {
    primary: string;
    secondary: string;
    background: string;
    text: string;
  };
  spacing: {
    sm: string;
    md: string;
    lg: string;
  };
}

const lightTheme: Theme = {
  colors: {
    primary: '#3b82f6',
    secondary: '#6366f1',
    background: '#ffffff',
    text: '#1f2937',
  },
  spacing: {
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
  },
};

const darkTheme: Theme = {
  colors: {
    primary: '#60a5fa',
    secondary: '#818cf8',
    background: '#1f2937',
    text: '#f9fafb',
  },
  spacing: {
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
  },
};

const ThemeContext = createContext({
  theme: lightTheme,
  isDark: false,
  toggleTheme: () => {},
});

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isDark, setIsDark] = useState(false);
  
  const toggleTheme = () => setIsDark(!isDark);
  
  return (
    <ThemeContext.Provider value={{ 
      theme: isDark ? darkTheme : lightTheme, 
      isDark,
      toggleTheme 
    }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => useContext(ThemeContext);
```

## Feature Components

### Chat Interface

```typescript
// components/features/ChatInterface/ChatWindow.tsx
import React, { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
}

export const ChatWindow: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const handleSend = async () => {
    if (!input.trim()) return;
    
    const userMessage: Message = {
      id: Date.now().toString(),
      content: input,
      role: 'user',
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    
    try {
      // Call API
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input }),
      });
      
      const data = await response.json();
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: data.response,
        role: 'assistant',
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map(message => (
          <div
            key={message.id}
            className={`p-3 rounded-lg ${
              message.role === 'user' 
                ? 'bg-blue-100 ml-auto max-w-[80%]' 
                : 'bg-gray-100 mr-auto max-w-[80%]'
            }`}
          >
            {message.content}
          </div>
        ))}
      </div>
      
      <div className="border-t p-4">
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type a message..."
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          />
          <Button onClick={handleSend} isLoading={isLoading}>
            Send
          </Button>
        </div>
      </div>
    </div>
  );
};
```

## Configuration

### Tailwind Configuration

```javascript
// tailwind.config.js
module.exports = {
  content: [
    './src/**/*.{js,jsx,ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#3b82f6',
        secondary: '#6366f1',
      },
    },
  },
  plugins: [],
};
```

## Best Practices

1. **Component Composition**: Build complex components from simple primitives
2. **Accessibility**: Use proper ARIA attributes and keyboard navigation
3. **Performance**: Use React.memo for expensive components
4. **Testing**: Write tests for all components
5. **Documentation**: Document props with TypeScript interfaces

## Integration Points

- **API Layer**: Connects to backend via fetch/axios
- **State Management**: Uses React hooks for local state
- **Theme System**: Provides consistent styling
- **Routing**: Integrates with React Router

