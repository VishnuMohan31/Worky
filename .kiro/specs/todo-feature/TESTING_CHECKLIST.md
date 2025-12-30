# TODO Feature - Final Integration Testing Checklist

This document provides a comprehensive checklist for manually testing the TODO feature across all requirements.

## Test Environment Setup

- [ ] Backend API is running on http://localhost:8000
- [ ] Frontend UI is running on http://localhost:5173
- [ ] Database is populated with test data
- [ ] At least 2 test users are available
- [ ] Test tasks and subtasks exist in the hierarchy

## 1. Navigation and Access (Requirement 7.2)

### Test: Access TODO Dashboard from Navigation
- [ ] Log in to the application
- [ ] Locate TODO item in left navigation sidebar
- [ ] Click on TODO navigation item
- [ ] Verify TODO dashboard loads within 2 seconds
- [ ] Verify URL changes to `/todos`
- [ ] Verify page title shows "TODO Dashboard" or similar

### Test: Navigation Badge
- [ ] Create TODO items for today's date
- [ ] Navigate away from TODO page
- [ ] Verify badge on TODO nav item shows count of today's items
- [ ] Delete a today TODO item
- [ ] Verify badge count decreases

## 2. TODO Item Lifecycle (Requirements 1.1, 1.4, 2.2, 2.3)

### Test: Create TODO Item
- [ ] Click "Add TODO" or "+" button
- [ ] Fill in title: "Review PR #123"
- [ ] Fill in description: "Check code quality and tests"
- [ ] Select target date: Today
- [ ] Select visibility: Private
- [ ] Click Save
- [ ] Verify TODO appears in Today pane
- [ ] Verify success notification appears

### Test: Update TODO Item
- [ ] Click edit button on existing TODO
- [ ] Change title to "Review PR #123 - UPDATED"
- [ ] Change description
- [ ] Click Save
- [ ] Verify changes are reflected immediately
- [ ] Verify success notification appears

### Test: Delete TODO Item
- [ ] Click delete button on a TODO item
- [ ] Confirm deletion in modal
- [ ] Verify item disappears from pane
- [ ] Verify success notification appears
- [ ] Refresh page
- [ ] Verify item is still gone (soft deleted)

## 3. Time Panes Organization (Requirements 4.1, 4.2, 4.4, 4.5)

### Test: Four Panes Display
- [ ] Verify "Yesterday" pane is displayed with correct date
- [ ] Verify "Today" pane is displayed with current date
- [ ] Verify "Tomorrow" pane is displayed with correct date
- [ ] Verify "Day After Tomorrow" pane is displayed with correct date
- [ ] Verify dates update correctly when page is refreshed

### Test: TODO Items in Correct Panes
- [ ] Create TODO for yesterday's date
- [ ] Verify it appears in Yesterday pane
- [ ] Create TODO for today's date
- [ ] Verify it appears in Today pane
- [ ] Create TODO for tomorrow's date
- [ ] Verify it appears in Tomorrow pane
- [ ] Create TODO for day after tomorrow
- [ ] Verify it appears in Day After Tomorrow pane

### Test: Drag and Drop Between Panes
- [ ] Drag a TODO from Today pane
- [ ] Drop it in Tomorrow pane
- [ ] Verify item moves to Tomorrow pane
- [ ] Verify item's target_date updates to tomorrow
- [ ] Verify smooth animation during drag
- [ ] Verify drop zone highlights when dragging over
- [ ] Refresh page
- [ ] Verify item is still in Tomorrow pane

### Test: Drag and Drop Visual Feedback
- [ ] Start dragging a TODO item
- [ ] Verify item scales up slightly (1.05x)
- [ ] Verify shadow increases
- [ ] Verify cursor changes to grab/grabbing
- [ ] Hover over different panes
- [ ] Verify panes highlight when valid drop target
- [ ] Drop item
- [ ] Verify smooth transition animation (300ms)

## 4. Visibility Controls (Requirements 2.1, 2.2, 2.3, 2.5)

### Test: Private TODO Items
- [ ] Create TODO with visibility: Private
- [ ] Verify "Private" badge is displayed
- [ ] Verify badge has blue color
- [ ] Log in as different user
- [ ] Navigate to TODO page
- [ ] Verify private TODO is NOT visible
- [ ] Verify private TODO is NOT in public filter

### Test: Public TODO Items
- [ ] Create TODO with visibility: Public
- [ ] Verify "Public" badge is displayed
- [ ] Verify badge has green color
- [ ] Log in as different user (same organization)
- [ ] Navigate to TODO page
- [ ] Enable "Show Public Items" filter
- [ ] Verify public TODO IS visible
- [ ] Verify owner's name is displayed

### Test: Toggle Visibility
- [ ] Create private TODO item
- [ ] Click visibility toggle button
- [ ] Verify visibility changes to Public
- [ ] Verify badge updates immediately
- [ ] Click toggle again
- [ ] Verify visibility changes back to Private
- [ ] Verify badge updates

## 5. Task Linking (Requirements 3.2, 3.3, 3.5, 3.6)

### Test: Link TODO to Task
- [ ] Create or edit a TODO item
- [ ] Click "Link to Task" button
- [ ] Search for existing task by ID or title
- [ ] Select a task from dropdown
- [ ] Save TODO
- [ ] Verify link indicator appears on TODO card
- [ ] Verify task ID is displayed (e.g., "TSK-001")

### Test: View Linked Task Information
- [ ] Click on TODO with linked task
- [ ] Expand task info panel
- [ ] Verify task title is displayed
- [ ] Verify task status is displayed with color
- [ ] Verify task due date is displayed (if available)
- [ ] Verify assigned user is displayed (if available)
- [ ] Verify "View in Hierarchy" link is present
- [ ] Verify read-only lock icon is displayed

### Test: Link TODO to Subtask
- [ ] Create or edit a TODO item
- [ ] Click "Link to Subtask" button
- [ ] Search for existing subtask
- [ ] Select a subtask from dropdown
- [ ] Save TODO
- [ ] Verify subtask link indicator appears
- [ ] Expand subtask info panel
- [ ] Verify subtask information is displayed

### Test: Unlink TODO from Task
- [ ] Click on TODO with linked task
- [ ] Click "Unlink" button
- [ ] Confirm unlinking
- [ ] Verify link indicator disappears
- [ ] Verify task info panel is removed
- [ ] Verify TODO item remains (not deleted)

### Test: Read-Only Task Access
- [ ] Link TODO to a task
- [ ] Expand task info panel
- [ ] Verify NO edit buttons are present
- [ ] Verify NO delete buttons are present
- [ ] Verify task title is not editable
- [ ] Verify task status is not editable
- [ ] Click "View in Hierarchy" link
- [ ] Verify navigates to task in hierarchy view
- [ ] Verify task CAN be edited in hierarchy view

### Test: Task Summary Endpoint
- [ ] Open browser dev tools (Network tab)
- [ ] Link TODO to task
- [ ] Verify GET request to `/api/v1/tasks/{id}/summary`
- [ ] Verify response contains only summary fields
- [ ] Verify response does NOT contain full task details
- [ ] Attempt PUT/PATCH/DELETE to summary endpoint
- [ ] Verify 405 Method Not Allowed or 404 response

## 6. ADHOC Notes (Requirements 5.1, 5.2, 5.3, 5.4, 5.5)

### Test: ADHOC Pane Display
- [ ] Verify ADHOC pane is visible on right side (desktop)
- [ ] Verify ADHOC pane has sticky note styling
- [ ] Verify "Add Note" button is present
- [ ] Verify pane has yellow/warm background

### Test: Create ADHOC Note
- [ ] Click "Add Note" button
- [ ] Fill in title: "Remember to..."
- [ ] Fill in content: "Call client about requirements"
- [ ] Select color (yellow, pink, blue, etc.)
- [ ] Click Save
- [ ] Verify note appears in ADHOC pane
- [ ] Verify note has sticky note appearance
- [ ] Verify note has slight rotation effect
- [ ] Verify selected color is applied

### Test: Update ADHOC Note
- [ ] Click edit button on ADHOC note
- [ ] Change title and content
- [ ] Change color
- [ ] Click Save
- [ ] Verify changes are reflected
- [ ] Verify color updates

### Test: Delete ADHOC Note
- [ ] Click delete button on ADHOC note
- [ ] Confirm deletion
- [ ] Verify note disappears with animation
- [ ] Refresh page
- [ ] Verify note is still gone

### Test: Reorder ADHOC Notes
- [ ] Create 3+ ADHOC notes
- [ ] Drag a note from bottom
- [ ] Drop it at the top
- [ ] Verify note moves to new position
- [ ] Verify other notes adjust positions
- [ ] Refresh page
- [ ] Verify order is persisted

## 7. UI/UX and Styling (Requirements 6.1, 6.2, 6.3, 6.4)

### Test: Visual Design
- [ ] Verify clean, minimalistic design
- [ ] Verify vibrant colors are used
- [ ] Verify cards have subtle shadows
- [ ] Verify proper spacing between elements
- [ ] Verify consistent typography
- [ ] Verify icons are clear and intuitive

### Test: Hover Effects
- [ ] Hover over TODO card
- [ ] Verify shadow elevation increases
- [ ] Verify subtle scale or highlight effect
- [ ] Hover over buttons
- [ ] Verify button color changes
- [ ] Verify cursor changes to pointer

### Test: Animations
- [ ] Drag TODO item
- [ ] Verify smooth drag animation
- [ ] Drop TODO item
- [ ] Verify smooth drop animation (300ms)
- [ ] Open modal
- [ ] Verify fade-in animation (250ms)
- [ ] Close modal
- [ ] Verify fade-out animation
- [ ] Delete item
- [ ] Verify fade-out + slide animation

### Test: Color Coding
- [ ] Verify Private TODO has blue border/badge
- [ ] Verify Public TODO has green border/badge
- [ ] Verify linked TODO has indicator icon
- [ ] Verify task status colors (In Progress, Done, etc.)
- [ ] Verify ADHOC notes have customizable colors

## 8. Responsive Design (Requirements 6.5, 6.6)

### Test: Desktop View (>1024px)
- [ ] Open on desktop browser
- [ ] Verify four panes displayed side-by-side
- [ ] Verify ADHOC pane on right side
- [ ] Verify all content is readable
- [ ] Verify no horizontal scrolling needed

### Test: Tablet View (768-1024px)
- [ ] Resize browser to tablet width
- [ ] Verify panes stack in 2x2 grid
- [ ] Verify ADHOC pane moves below time panes
- [ ] Verify touch-friendly button sizes
- [ ] Verify drag and drop still works

### Test: Mobile View (<768px)
- [ ] Resize browser to mobile width
- [ ] Verify tabs for different panes
- [ ] Verify one pane visible at a time
- [ ] Verify ADHOC notes in separate tab
- [ ] Verify navigation is accessible
- [ ] Verify forms are usable
- [ ] Verify buttons are touch-friendly (44px min)

## 9. Accessibility (Requirement 6.6)

### Test: Keyboard Navigation
- [ ] Tab through all interactive elements
- [ ] Verify focus indicators are visible
- [ ] Verify logical tab order
- [ ] Press Enter on buttons
- [ ] Verify buttons activate
- [ ] Press Escape in modal
- [ ] Verify modal closes
- [ ] Use arrow keys in dropdowns
- [ ] Verify navigation works

### Test: Screen Reader Support
- [ ] Enable screen reader (NVDA, JAWS, VoiceOver)
- [ ] Navigate to TODO page
- [ ] Verify page title is announced
- [ ] Tab through TODO items
- [ ] Verify item details are announced
- [ ] Verify button purposes are announced
- [ ] Verify form labels are announced
- [ ] Verify error messages are announced

### Test: Color Contrast
- [ ] Use browser dev tools (Lighthouse)
- [ ] Run accessibility audit
- [ ] Verify WCAG AA compliance (4.5:1 for text)
- [ ] Verify all text is readable
- [ ] Verify focus indicators are visible

### Test: Alt Text and ARIA Labels
- [ ] Inspect icon buttons
- [ ] Verify aria-label attributes
- [ ] Verify meaningful labels (not "button" or "icon")
- [ ] Inspect images
- [ ] Verify alt text is present
- [ ] Verify alt text is descriptive

## 10. Error Handling (Requirement 8.8)

### Test: Network Errors
- [ ] Disconnect network
- [ ] Try to create TODO
- [ ] Verify error message appears
- [ ] Verify error message is user-friendly
- [ ] Verify retry button is available
- [ ] Reconnect network
- [ ] Click retry
- [ ] Verify operation succeeds

### Test: Validation Errors
- [ ] Try to create TODO without title
- [ ] Verify validation error appears
- [ ] Verify error message is clear
- [ ] Verify field is highlighted
- [ ] Enter title with 300 characters
- [ ] Verify max length validation
- [ ] Enter invalid date
- [ ] Verify date validation

### Test: Authorization Errors
- [ ] Log out
- [ ] Try to access TODO page
- [ ] Verify redirect to login
- [ ] Log in as different user
- [ ] Try to access another user's TODO (via URL)
- [ ] Verify 404 or unauthorized error

### Test: Loading States
- [ ] Refresh TODO page
- [ ] Verify loading skeleton appears
- [ ] Verify loading doesn't block UI
- [ ] Verify smooth transition when data loads

## 11. Performance (Requirement 7.5)

### Test: Page Load Time
- [ ] Clear browser cache
- [ ] Navigate to TODO page
- [ ] Measure load time (use Network tab)
- [ ] Verify page loads within 2 seconds
- [ ] Verify no unnecessary API calls

### Test: Large Data Sets
- [ ] Create 50+ TODO items
- [ ] Verify page remains responsive
- [ ] Verify drag and drop still smooth
- [ ] Verify no lag when scrolling
- [ ] Create 20+ ADHOC notes
- [ ] Verify ADHOC pane remains responsive

### Test: Concurrent Operations
- [ ] Open TODO page in two browser tabs
- [ ] Create TODO in tab 1
- [ ] Refresh tab 2
- [ ] Verify TODO appears in tab 2
- [ ] Update TODO in tab 2
- [ ] Refresh tab 1
- [ ] Verify update appears in tab 1

## 12. Cross-Browser Testing

### Test: Chrome/Chromium
- [ ] Run all core tests in Chrome
- [ ] Verify drag and drop works
- [ ] Verify animations are smooth
- [ ] Verify no console errors

### Test: Firefox
- [ ] Run all core tests in Firefox
- [ ] Verify drag and drop works
- [ ] Verify animations are smooth
- [ ] Verify no console errors

### Test: Safari (if available)
- [ ] Run all core tests in Safari
- [ ] Verify drag and drop works
- [ ] Verify animations are smooth
- [ ] Verify no console errors

### Test: Edge
- [ ] Run all core tests in Edge
- [ ] Verify drag and drop works
- [ ] Verify animations are smooth
- [ ] Verify no console errors

## 13. Data Integrity (Requirements 1.3, 9.5, 9.6)

### Test: Soft Delete
- [ ] Delete a TODO item
- [ ] Check database directly
- [ ] Verify is_deleted = true
- [ ] Verify record still exists
- [ ] Verify deleted item not in API response

### Test: Timestamps
- [ ] Create TODO item
- [ ] Check created_at timestamp
- [ ] Update TODO item
- [ ] Check updated_at timestamp
- [ ] Verify updated_at > created_at

### Test: Foreign Key Integrity
- [ ] Link TODO to task
- [ ] Delete task from hierarchy
- [ ] Verify TODO still exists
- [ ] Verify link is broken or handled gracefully

## 14. Security (Requirement 8.6)

### Test: Authentication Required
- [ ] Log out
- [ ] Try to access `/api/v1/todos` directly
- [ ] Verify 401 Unauthorized response
- [ ] Try to access TODO page
- [ ] Verify redirect to login

### Test: Authorization Checks
- [ ] Create TODO as User 1
- [ ] Note the TODO ID
- [ ] Log in as User 2
- [ ] Try to access User 1's TODO via API
- [ ] Verify 404 or 403 response
- [ ] Try to update User 1's TODO
- [ ] Verify 404 or 403 response

### Test: Input Sanitization
- [ ] Create TODO with title: `<script>alert('XSS')</script>`
- [ ] Verify script is escaped/sanitized
- [ ] Verify no alert appears
- [ ] Verify text is displayed safely

## Test Results Summary

### Passed Tests: _____ / _____
### Failed Tests: _____ / _____
### Blocked Tests: _____ / _____

### Critical Issues Found:
1. 
2. 
3. 

### Minor Issues Found:
1. 
2. 
3. 

### Notes:


### Sign-off:
- [ ] All critical functionality tested and working
- [ ] All requirements verified
- [ ] No blocking issues remain
- [ ] Feature ready for production

**Tester Name:** _______________
**Date:** _______________
**Signature:** _______________
