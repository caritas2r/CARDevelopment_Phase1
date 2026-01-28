import { Toaster } from 'react-hot-toast';

export function Toast() {
  return (
    <Toaster
      position="top-right"
      toastOptions={{
        duration: 4000,
        style: {
          background: '#1f1f1f',
          color: '#fff',
          border: '1px solid #374151',
        },
        success: {
          iconTheme: {
            primary: '#B7852A',
            secondary: '#000',
          },
        },
        error: {
          iconTheme: {
            primary: '#ef4444',
            secondary: '#fff',
          },
        },
      }}
    />
  );
}