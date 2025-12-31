import { QueryClient } from '@tanstack/react-query'

/**
 * Safely check if we're in development mode
 * This ensures the app works even if import.meta.env.MODE is undefined
 * 
 * The issue: On first load (especially on new devices), import.meta.env.MODE
 * might be undefined, causing QueryClient initialization to fail.
 * 
 * Solution: Use a safe check with a fallback to ensure the app always works.
 */
const isDevelopment = (): boolean => {
  try {
    // Safely access import.meta.env.MODE with fallback
    // Handle cases where MODE might be undefined, null, or empty string
    const mode = import.meta.env?.MODE
    // Only return true if mode is explicitly 'development'
    // This prevents errors when MODE is undefined or empty
    return typeof mode === 'string' && mode === 'development'
  } catch (error) {
    // If there's any error accessing the environment, default to false
    // This ensures the app works even if environment variables aren't available
    // Production behavior (refetchOnWindowFocus: false) is safer for unknown states
    return false
  }
}

/**
 * React Query client configuration
 * This is a singleton instance used throughout the application
 * 
 * This configuration is designed to work reliably even when:
 * - The app is first loaded on a new device
 * - Environment variables are not yet initialized
 * - The build process hasn't fully processed import.meta.env
 */
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Retry failed requests 1 time
      retry: 1,
      // Refetch on window focus in development, but not in production
      // Using a safe function call to prevent initialization errors
      refetchOnWindowFocus: isDevelopment(),
      // Stale time: data is considered fresh for 5 minutes
      staleTime: 5 * 60 * 1000,
      // Cache time: unused data is kept in cache for 10 minutes
      gcTime: 10 * 60 * 1000,
    },
    mutations: {
      // Retry failed mutations 0 times (mutations should not retry by default)
      retry: 0,
    },
  },
})

