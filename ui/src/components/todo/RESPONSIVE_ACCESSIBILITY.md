# TODO Feature - Responsive Design & Accessibility Guide

## Overview

This document describes the responsive design and accessibility features implemented for the TODO feature, ensuring WCAG AA compliance and optimal user experience across all devices.

## Responsive Breakpoints

### Desktop (> 1024px)
- **Layout**: Four time panes displayed side-by-side with ADHOC pane on the right
- **Grid**: 4 columns for time panes + fixed 320px width for ADHOC pane
- **Interaction**: Full drag-and-drop support with mouse
- **Typography**: Standard font sizes for optimal readability

### Tablet (769px - 1024px)
- **Layout**: Two time panes per row (2x2 grid) with ADHOC pane below
- **Grid**: 2 columns for time panes, full width for ADHOC pane
- **Interaction**: Touch-optimized drag-and-drop
- **Typography**: Slightly reduced font sizes

### Mobile (≤ 768px)
- **Layout**: Tab-based navigation showing one pane at a time
- **Tabs**: 5 tabs (Yesterday, Today, Tomorrow, Day After Tomorrow, ADHOC)
- **Interaction**: Touch-optimized with larger touch targets (min 44x44px)
- **Typography**: Mobile-optimized font sizes (min 16px to prevent zoom)
- **Default Tab**: "Today" (index 1)

### Small Mobile (≤ 480px)
- **Layout**: Same as mobile but with further optimized spacing
- **Typography**: Further reduced font sizes while maintaining readability
- **Touch Targets**: Maintained at 44x44px minimum

## Accessibility Features

### WCAG AA Compliance

#### Color Contrast
- **Text on Light Backgrounds**: Minimum 4.5:1 contrast ratio
  - Primary text: #111827 on white (#FFFFFF)
  - Secondary text: #4B5563 on white (#FFFFFF)
- **Text on Dark Backgrounds**: Minimum 4.5:1 contrast ratio
  - Light text: #F9FAFB on dark backgrounds
- **Status Badges**: Enhanced with bold font weight for better visibility
- **Links**: Underlined with sufficient contrast (#6366F1)

#### Keyboard Navigation
- **Tab Order**: Logical tab order through all interactive elements
- **Focus Indicators**: 
  - 3px solid outline in primary color (#6366F1)
  - 2px offset for visibility
  - Visible on all focusable elements
- **Keyboard Shortcuts**:
  - `Tab`: Navigate between elements
  - `Enter/Space`: Activate buttons and expand/collapse panels
  - `Delete`: Delete ADHOC notes (when focused)
  - `Arrow Keys`: Navigate between tabs on mobile

#### Screen Reader Support
- **ARIA Labels**: All interactive elements have descriptive labels
- **ARIA Roles**: Proper semantic roles (article, button, tab, tabpanel, etc.)
- **ARIA Live Regions**: Dynamic content updates announced
  - Item counts: `aria-live="polite"`
  - Error messages: `aria-live="assertive"`
- **ARIA States**: 
  - `aria-selected` for tabs
  - `aria-expanded` for expandable panels
  - `aria-disabled` for disabled buttons
  - `aria-label` for icon-only buttons

#### Semantic HTML
- **Headings**: Proper heading hierarchy (h1 → h2 → h3)
- **Lists**: TODO items and notes wrapped in `<ul>` with `<li>` elements
- **Navigation**: Wrapped in `<nav>` with `aria-label`
- **Regions**: Main content areas use `role="region"` with labels
- **Articles**: Individual items use `role="article"`

### Motion & Animation

#### Reduced Motion Support
- **Media Query**: `@media (prefers-reduced-motion: reduce)`
- **Behavior**: 
  - All animations disabled or reduced to 0.01ms
  - Transforms removed from hover states
  - Scroll behavior set to auto
  - Skeleton loaders use static background

#### Standard Animations
- **Drag & Drop**: Scale and shadow effects (0.2s ease)
- **Hover States**: Subtle elevation (0.2s ease)
- **Modal Open/Close**: Fade and slide (0.25s ease-out)
- **Loading Spinners**: Smooth rotation (1s linear infinite)

### Touch Device Optimizations

#### Touch Targets
- **Minimum Size**: 44x44px for all interactive elements
- **Spacing**: Adequate spacing between touch targets
- **Feedback**: Visual feedback on touch (opacity, scale)

#### Gestures
- **Drag & Drop**: Touch-optimized with visual feedback
- **Scroll**: Smooth scrolling with momentum (`-webkit-overflow-scrolling: touch`)
- **Swipe**: Horizontal swipe for tab navigation on mobile

#### Hover Behavior
- **Media Query**: `@media (hover: none) and (pointer: coarse)`
- **Behavior**: Hover effects disabled on touch devices
- **Alternative**: Active states provide feedback instead

## Mobile-Specific Features

### Tab Navigation
- **Implementation**: Horizontal scrollable tab bar
- **Active Indicator**: Highlighted tab with item count
- **Keyboard Support**: Arrow keys for navigation
- **Touch Support**: Swipe to scroll tabs

### Safe Area Insets
- **iOS Notch Support**: `env(safe-area-inset-bottom)`
- **Applied To**: Modal content, form containers
- **Fallback**: Standard padding for non-supporting browsers

### Viewport Optimization
- **Meta Tag**: `<meta name="viewport" content="width=device-width, initial-scale=1">`
- **Font Size**: Minimum 16px to prevent iOS zoom
- **Input Fields**: 16px font size to prevent zoom on focus

## High Contrast Mode

### Support
- **Media Query**: `@media (prefers-contrast: high)`
- **Enhancements**:
  - Increased border width (2px)
  - Border color set to currentColor
  - Enhanced button borders

## Dark Mode Support

### Implementation
- **Media Query**: `@media (prefers-color-scheme: dark)`
- **Color Adjustments**:
  - Background: #1f2937
  - Surface: #1f2937
  - Text: #F9FAFB
  - Secondary Text: #D1D5DB
  - Borders: #374151

## Print Styles

### Optimizations
- **Layout**: Block layout (no grid)
- **Colors**: Black text on white background
- **Hidden Elements**: Navigation, buttons, interactive elements
- **Page Breaks**: Avoid breaking inside panes
- **Borders**: 1px solid black for structure

## Testing Checklist

### Responsive Design
- [ ] Test on desktop (1920x1080, 1366x768)
- [ ] Test on tablet (iPad, 768x1024)
- [ ] Test on mobile (iPhone, 375x667)
- [ ] Test on small mobile (320x568)
- [ ] Test landscape orientation
- [ ] Test with browser zoom (100%, 150%, 200%)

### Keyboard Navigation
- [ ] Tab through all interactive elements
- [ ] Verify focus indicators are visible
- [ ] Test Enter/Space on buttons
- [ ] Test Delete key on ADHOC notes
- [ ] Test Escape to close modals
- [ ] Verify tab order is logical

### Screen Reader
- [ ] Test with VoiceOver (macOS/iOS)
- [ ] Test with NVDA (Windows)
- [ ] Test with JAWS (Windows)
- [ ] Verify all images have alt text
- [ ] Verify all buttons have labels
- [ ] Verify live regions announce updates

### Color Contrast
- [ ] Test with contrast checker tool
- [ ] Verify text meets 4.5:1 ratio
- [ ] Verify large text meets 3:1 ratio
- [ ] Test in high contrast mode
- [ ] Test in dark mode

### Touch Devices
- [ ] Test drag and drop on touch
- [ ] Verify touch targets are 44x44px
- [ ] Test swipe gestures
- [ ] Verify no hover-dependent functionality
- [ ] Test on iOS Safari
- [ ] Test on Android Chrome

### Motion
- [ ] Test with reduced motion enabled
- [ ] Verify animations are disabled/reduced
- [ ] Test with standard motion
- [ ] Verify animations are smooth

## Browser Support

### Minimum Versions
- **Chrome**: 90+
- **Firefox**: 88+
- **Safari**: 14+
- **Edge**: 90+
- **iOS Safari**: 14+
- **Android Chrome**: 90+

### Progressive Enhancement
- **CSS Grid**: Fallback to flexbox
- **CSS Custom Properties**: Fallback colors provided
- **Touch Events**: Fallback to mouse events
- **Safe Area Insets**: Fallback to standard padding

## Performance Considerations

### Mobile Optimization
- **Lazy Loading**: Images and heavy components
- **Code Splitting**: Mobile-specific code loaded separately
- **Touch Optimization**: Passive event listeners
- **Scroll Performance**: Hardware acceleration enabled

### Accessibility Performance
- **Focus Management**: Efficient focus trap in modals
- **Live Regions**: Debounced updates to prevent spam
- **ARIA Updates**: Batched to minimize reflows

## Future Enhancements

### Planned Features
- [ ] Voice control support
- [ ] Gesture customization
- [ ] Font size preferences
- [ ] Color theme customization
- [ ] Keyboard shortcut customization
- [ ] Offline support with service workers

### Accessibility Improvements
- [ ] WCAG AAA compliance
- [ ] Enhanced screen reader descriptions
- [ ] More keyboard shortcuts
- [ ] Better error recovery
- [ ] Improved form validation feedback

## Resources

### Tools
- **Contrast Checker**: https://webaim.org/resources/contrastchecker/
- **WAVE**: https://wave.webaim.org/
- **axe DevTools**: Browser extension for accessibility testing
- **Lighthouse**: Built into Chrome DevTools

### Guidelines
- **WCAG 2.1**: https://www.w3.org/WAI/WCAG21/quickref/
- **ARIA Practices**: https://www.w3.org/WAI/ARIA/apg/
- **Mobile Accessibility**: https://www.w3.org/WAI/mobile/

### Testing
- **Screen Readers**: VoiceOver, NVDA, JAWS
- **Browser DevTools**: Accessibility inspector
- **Mobile Testing**: BrowserStack, real devices
