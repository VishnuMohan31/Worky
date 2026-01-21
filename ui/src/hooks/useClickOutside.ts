import { useEffect, useRef } from 'react'

/**
 * Custom hook to detect clicks outside of a referenced element
 * @param handler - Function to call when clicking outside
 * @returns ref - Ref to attach to the element you want to detect outside clicks for
 */
export function useClickOutside<T extends HTMLElement>(
  handler: () => void
) {
  const ref = useRef<T>(null)

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (ref.current && !ref.current.contains(event.target as Node)) {
        handler()
      }
    }

    // Add event listener when component mounts
    document.addEventListener('mousedown', handleClickOutside)
    
    // Cleanup event listener when component unmounts
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [handler])

  return ref
}