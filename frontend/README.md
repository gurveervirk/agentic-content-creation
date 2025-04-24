# Render Chat Flow - Frontend

## Overview

This is the frontend application for Render Chat Flow, a modern chat interface designed to interact with AI-powered backend services. Built with React, TypeScript, and Vite, it provides a responsive and intuitive user experience.

## Technology Stack

- **React 18**: For building the component-based UI
- **TypeScript**: For type safety and better developer experience
- **Vite**: For fast development and optimized builds
- **TailwindCSS**: For utility-first styling
- **shadcn/ui**: For consistent, accessible UI components
- **React Router**: For client-side routing
- **React Query**: For data fetching, caching, and state management
- **React Markdown**: For rendering markdown content from AI responses

## Project Structure

```
frontend/
│
├── public/              # Static files
│
├── src/
│   ├── components/      # UI components
│   │   ├── ui/          # shadcn UI components
│   │   ├── Chat.tsx     # Main chat interface
│   │   └── ChatMessage.tsx # Individual message component
│   │
│   ├── hooks/           # Custom React hooks
│   │   └── use-toast.ts # Toast notification hook
│   │
│   ├── lib/             # Utility functions
│   │   └── utils.ts     # Common utility functions
│   │
│   ├── pages/           # Route components
│   │   ├── Index.tsx    # Main application page
│   │   └── NotFound.tsx # 404 page
│   │
│   ├── App.tsx          # Root application component
│   ├── index.css        # Global styles and Tailwind imports
│   ├── main.tsx         # Application entry point
│   └── vite-env.d.ts    # TypeScript declarations
│
├── .eslintrc.js         # ESLint configuration
├── index.html           # HTML template
├── package.json         # Dependencies and scripts
├── postcss.config.js    # PostCSS configuration
├── tailwind.config.ts   # Tailwind configuration
├── tsconfig.json        # TypeScript configuration
└── vite.config.ts       # Vite configuration
```

## Component Breakdown

### Chat Component

The `Chat.tsx` component is the core of the application, featuring:

- State management for chat messages using React hooks
- Form handling for user input
- API integration with the backend server
- Loading states and error handling
- Responsive design for different screen sizes

```tsx
// Simplified excerpt from Chat.tsx
const Chat = () => {
  const [messages, setMessages] =
    useState < Array<{ sender: string; content: string }>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // Send message to API and handle response
    // ...
  };

  return (
    <div className="flex flex-col h-full">
      {/* Chat interface components */}
    </div>
  );
};
```

### ChatMessage Component

The `ChatMessage.tsx` component renders individual messages with:

- Different styling based on sender (user vs. agent)
- Markdown rendering for agent responses
- Loading indicators
- Hover effects and animations

## Theming

The application uses a custom theme built on TailwindCSS with:

- CSS variables for color tokens
- Deep purple accent color scheme
- Responsive design considerations
- Dark/light mode support (prepared but not fully implemented)

## API Integration

The frontend communicates with the backend API using fetch:

- Sends user messages to `/api/chat` endpoint
- Resets conversation with `/api/reset` endpoint
- Handles loading states and errors gracefully

## Development Workflow

1. **Installation**:

   ```bash
   npm install
   ```

2. **Development Server**:

   ```bash
   npm run dev
   ```

3. **Building for Production**:
   ```bash
   npm run build
   ```

## Future Enhancements

- Implement real-time message streaming
- Add user authentication
- Develop conversation history/storage
- Create theme switching capability
- Add accessibility improvements

## Contributing

Please refer to the main project README for contribution guidelines.
