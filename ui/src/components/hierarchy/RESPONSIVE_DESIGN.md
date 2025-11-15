# Responsive Design Implementation for Hierarchy Components

## Overview

The hierarchy navigation components have been optimized for responsive design with a mobile-first approach. The implementation ensures optimal real estate usage across all device sizes while maintaining usability and accessibility.

## Breakpoints

### Device Categories
- **Mobile**: ≤ 767px
- **Tablet**: 768px - 1023px
- **Desktop**: ≥ 1024px

### Layout Strategies

#### Desktop (≥ 1024px)
- **Three-column layout**: Parent | Current | Children
- Grid columns: `minmax(250px, 1fr) minmax(400px, 2fr) minmax(250px, 1fr)`
- All panes visible simultaneously
- Optimal for multitasking and context awareness

#### Tablet (768px - 1023px)
- **Two-column layout**: Current | Children
- Grid columns: `minmax(300px, 2fr) minmax(250px, 1fr)`
- Parent pane hidden to maximize space
- Breadcrumb provides parent context
- Suitable for focused work with some context

#### Mobile (≤ 767px)
- **Single-column layout with tabs**
- Tab-based navigation between Parent, Current, and Children
- Full-screen panes for maximum content visibility
- Swipe gestures for navigation (optional)
- Optimized for one-handed use

## Key Features

### 1. Mobile Navigation Tabs
```tsx
<MobileNavigation
  onTabChange={(tab) => setActiveTab(tab)}
  hasParent={!!parentEntity}
  hasChildren={childEntities.length > 0}
  currentTab="current"
/>
```

**Features:**
- Dynamic tab visibility based on hierarchy position
- Active state indication
- Touch-optimized tap targets (min 48px height)
- Smooth transitions between views

### 2. Responsive Breadcrumb
- Horizontal scrolling on mobile
- Truncated text with ellipsis
- Thin scrollbar for better UX
- Touch-friendly scroll behavior

### 3. Touch-Optimized Components

#### Entity Cards
- Minimum height: 60px (mobile)
- Larger padding for easier tapping
- Active state feedback
- No hover transforms on mobile (performance)

#### Buttons and Interactive Elements
- Minimum touch target: 48x48px
- Adequate spacing between elements
- Visual feedback on tap
- No hover states on touch devices

### 4. Adaptive Tables (Phase Manager)
- Desktop: Standard table layout
- Mobile: Card-based layout
  - Hidden table headers
  - Each row becomes a card
  - Data labels shown inline
  - Easier to scan and interact

### 5. Collapsible Sections
```tsx
<div className="collapsible-section expanded">
  <div className="collapsible-header">
    <h4 className="collapsible-title">Statistics</h4>
    <span className="collapsible-icon">▼</span>
  </div>
  <div className="collapsible-content">
    {/* Content */}
  </div>
</div>
```

**Benefits:**
- Reduces initial content height
- User controls information density
- Smooth expand/collapse animations
- Remembers state during session

### 6. Floating Action Button (FAB)
- Fixed position: bottom-right
- Size: 56x56px (48x48px in landscape)
- Primary actions (e.g., "Add Child")
- Only visible on mobile
- Respects safe area insets

### 7. Bottom Sheet
- Modal-like component from bottom
- Touch-friendly handle for dragging
- Smooth slide-in animation
- Backdrop for focus
- Max height: 80vh
- Scrollable content

### 8. Skeleton Loading
```tsx
<SkeletonLoader type="card" count={3} />
<SkeletonLoader type="details" />
<SkeletonLoader type="statistics" />
```

**Benefits:**
- Improves perceived performance
- Reduces layout shift
- Provides visual feedback
- Matches actual content structure

## Responsive Hooks

### useResponsive
```tsx
const { isMobile, isTablet, isDesktop, isLandscape, width, height } = useResponsive()

if (isMobile) {
  // Render mobile layout
}
```

### usePrefersReducedMotion
```tsx
const prefersReducedMotion = usePrefersReducedMotion()

if (prefersReducedMotion) {
  // Disable animations
}
```

### useIsTouchDevice
```tsx
const isTouchDevice = useIsTouchDevice()

if (isTouchDevice) {
  // Enable touch-specific features
}
```

### useSafeAreaInsets
```tsx
const { top, right, bottom, left } = useSafeAreaInsets()

// Apply safe area padding for notched devices
```

## CSS Features

### 1. Grid Layout
- Flexible grid system
- Automatic column adjustment
- Gap management
- Overflow handling

### 2. Flexbox
- Flexible component layouts
- Alignment control
- Space distribution
- Order management

### 3. CSS Variables
- Theme-aware styling
- Consistent spacing
- Responsive font sizes
- Dynamic colors

### 4. Media Queries
- Breakpoint-based styles
- Orientation detection
- Preference queries (reduced motion, high contrast)
- Print styles

### 5. Safe Area Insets
```css
@supports (padding: max(0px)) {
  .hierarchy-navigator {
    padding-left: max(0px, env(safe-area-inset-left));
    padding-right: max(0px, env(safe-area-inset-right));
  }
}
```

**Supports:**
- iPhone X and newer (notch)
- Android devices with notches
- Foldable devices
- Landscape orientation

## Performance Optimizations

### 1. Hardware Acceleration
```css
.entity-card {
  transform: translateY(-2px);
  will-change: transform;
}
```

### 2. Smooth Scrolling
```css
.smooth-scroll {
  scroll-behavior: smooth;
  -webkit-overflow-scrolling: touch;
}
```

### 3. Reduced Repaints
- Use `transform` instead of `top/left`
- Use `opacity` for fade effects
- Avoid layout-triggering properties

### 4. Lazy Loading
- Load content on demand
- Skeleton loaders for placeholders
- Progressive enhancement

## Accessibility Features

### 1. Touch Targets
- Minimum size: 48x48px
- Adequate spacing: 8px minimum
- Visual feedback on interaction

### 2. Keyboard Navigation
- Tab order preserved
- Focus indicators
- Keyboard shortcuts

### 3. Screen Reader Support
- Semantic HTML
- ARIA labels
- Descriptive text

### 4. High Contrast Mode
```css
@media (prefers-contrast: high) {
  .entity-card {
    border-width: 2px;
  }
}
```

### 5. Reduced Motion
```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

## Testing Checklist

### Mobile Testing
- [ ] Test on iPhone SE (375px)
- [ ] Test on iPhone 12/13/14 (390px)
- [ ] Test on iPhone 14 Pro Max (430px)
- [ ] Test on Android (360px, 412px)
- [ ] Test in landscape mode
- [ ] Test with safe area insets
- [ ] Test touch interactions
- [ ] Test swipe gestures

### Tablet Testing
- [ ] Test on iPad Mini (768px)
- [ ] Test on iPad (810px)
- [ ] Test on iPad Pro (1024px)
- [ ] Test in portrait mode
- [ ] Test in landscape mode
- [ ] Test split-screen mode

### Desktop Testing
- [ ] Test at 1280px
- [ ] Test at 1440px
- [ ] Test at 1920px
- [ ] Test at 2560px (4K)
- [ ] Test with browser zoom (50%, 75%, 125%, 150%)

### Cross-Browser Testing
- [ ] Chrome (mobile & desktop)
- [ ] Safari (iOS & macOS)
- [ ] Firefox (mobile & desktop)
- [ ] Edge (desktop)
- [ ] Samsung Internet (mobile)

### Accessibility Testing
- [ ] Test with screen reader (VoiceOver, TalkBack)
- [ ] Test keyboard navigation
- [ ] Test with high contrast mode
- [ ] Test with reduced motion
- [ ] Test with large text (200%)
- [ ] Test color contrast ratios

## Best Practices

### 1. Mobile-First Approach
- Start with mobile styles
- Add complexity for larger screens
- Progressive enhancement

### 2. Touch-Friendly Design
- Large tap targets (min 48px)
- Adequate spacing (min 8px)
- Visual feedback
- No hover-dependent features

### 3. Performance
- Minimize reflows
- Use CSS transforms
- Lazy load content
- Optimize images

### 4. Content Priority
- Most important content first
- Progressive disclosure
- Collapsible sections
- Clear hierarchy

### 5. Consistent Patterns
- Reusable components
- Consistent spacing
- Predictable behavior
- Familiar interactions

## Common Patterns

### 1. Responsive Grid
```css
.stat-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: var(--spacing-sm);
}
```

### 2. Responsive Typography
```css
.entity-details h2 {
  font-size: clamp(var(--font-size-lg), 5vw, var(--font-size-xl));
}
```

### 3. Responsive Spacing
```css
.entity-card {
  padding: clamp(var(--spacing-sm), 2vw, var(--spacing-md));
}
```

### 4. Responsive Images
```css
img {
  max-width: 100%;
  height: auto;
}
```

## Troubleshooting

### Issue: Layout breaks on small screens
**Solution:** Check minimum widths and use `min-width: 0` on flex children

### Issue: Touch targets too small
**Solution:** Ensure minimum 48x48px size with adequate spacing

### Issue: Horizontal scrolling
**Solution:** Use `overflow-x: hidden` on container and `max-width: 100%` on children

### Issue: Content cut off by notch
**Solution:** Use safe area insets with `env()` function

### Issue: Animations janky on mobile
**Solution:** Use `transform` and `opacity` only, add `will-change` sparingly

## Future Enhancements

1. **Gesture Support**
   - Swipe to navigate between panes
   - Pull to refresh
   - Long press for context menu

2. **Adaptive Loading**
   - Load less data on mobile
   - Progressive image loading
   - Infinite scroll for lists

3. **Offline Support**
   - Cache critical data
   - Offline indicators
   - Sync when online

4. **PWA Features**
   - Install prompt
   - Push notifications
   - Background sync

5. **Advanced Interactions**
   - Drag and drop (touch-friendly)
   - Multi-select
   - Bulk actions

## Resources

- [MDN: Responsive Design](https://developer.mozilla.org/en-US/docs/Learn/CSS/CSS_layout/Responsive_Design)
- [Web.dev: Responsive Web Design Basics](https://web.dev/responsive-web-design-basics/)
- [Material Design: Layout](https://material.io/design/layout/responsive-layout-grid.html)
- [Apple: Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Android: Material Design](https://material.io/design)

---

**Last Updated:** 2025-01-13
**Version:** 1.0.0
**Maintainer:** Worky Development Team
