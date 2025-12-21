// Simple toast implementation
let toastContainer: HTMLDivElement | null = null;

const createToastContainer = () => {
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.className = 'fixed top-4 right-4 z-50 space-y-2';
    document.body.appendChild(toastContainer);
  }
  return toastContainer;
};

const showToast = (message: string, type: 'success' | 'error' | 'info' = 'info') => {
  const container = createToastContainer();
  
  const toast = document.createElement('div');
  toast.className = `px-4 py-2 rounded-md shadow-lg text-white max-w-sm ${
    type === 'success' ? 'bg-green-600' :
    type === 'error' ? 'bg-red-600' :
    'bg-blue-600'
  }`;
  toast.textContent = message;
  
  container.appendChild(toast);
  
  // Auto remove after 3 seconds
  setTimeout(() => {
    if (toast.parentNode) {
      toast.parentNode.removeChild(toast);
    }
  }, 3000);
};

export const toast = {
  success: (message: string) => showToast(message, 'success'),
  error: (message: string) => showToast(message, 'error'),
  info: (message: string) => showToast(message, 'info'),
};