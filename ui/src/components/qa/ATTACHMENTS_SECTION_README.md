# AttachmentsSection Component

## Overview

The `AttachmentsSection` component provides a comprehensive interface for managing file attachments on bugs and test cases. It displays a list of attachments with file details, supports uploading multiple files, and provides download and delete actions.

## Features

### Display Attachments
- **Grid Layout**: Displays attachments in a responsive grid (1 column on mobile, 2 on tablet, 3 on desktop)
- **File Information**: Shows file name, type, size, uploader, and upload timestamp
- **File Type Icons**: Visual icons for different file types (images, videos, PDFs, text files)
- **Image Previews**: Thumbnail previews for image attachments
- **File Type Badges**: Color-coded badges showing file extensions

### Upload Files
- **Multi-file Upload**: Upload multiple files at once
- **Drag-and-Drop Support**: (Can be added in future enhancement)
- **Progress Indicator**: Shows upload progress with percentage
- **File Type Validation**: Accepts images, videos, PDFs, and log files
- **Size Limit**: 10 MB per file (configurable)

### Download Files
- **One-Click Download**: Download attachments with a single click
- **Preview Images**: Click on image thumbnails to view full size

### Delete Files
- **Permission-Based**: Only the uploader or admins can delete attachments
- **Confirmation Dialog**: Requires confirmation before deletion
- **Soft Delete**: Attachments are marked as deleted but not removed from database

## Usage

```tsx
import AttachmentsSection from '../qa/AttachmentsSection'

// In your component
<AttachmentsSection
  entityType="bug"
  entityId={bugId}
  onAttachmentAdded={() => {
    console.log('Attachment added')
    // Optional: refresh data or show notification
  }}
/>
```

## Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `entityType` | `'bug' \| 'test_case'` | Yes | Type of entity the attachments belong to |
| `entityId` | `string` | Yes | ID of the entity (bug or test case) |
| `onAttachmentAdded` | `() => void` | No | Callback function called after successful upload |

## API Endpoints

The component expects the following API endpoints to be available:

### Get Attachments
```
GET /bugs/{bug_id}/attachments
GET /test-cases/{test_case_id}/attachments
```

Response:
```json
[
  {
    "id": "att-123",
    "file_name": "screenshot.png",
    "file_path": "/uploads/bugs/bug-456/screenshot.png",
    "file_type": "image/png",
    "file_size": 245678,
    "uploaded_by": "user-789",
    "uploader_name": "John Doe",
    "uploaded_at": "2025-01-15T10:30:00Z",
    "is_deleted": false
  }
]
```

### Upload Attachment
```
POST /bugs/{bug_id}/attachments
POST /test-cases/{test_case_id}/attachments
```

Request: `multipart/form-data` with file field

Response:
```json
{
  "id": "att-123",
  "file_name": "screenshot.png",
  "file_path": "/uploads/bugs/bug-456/screenshot.png",
  "file_type": "image/png",
  "file_size": 245678,
  "uploaded_by": "user-789",
  "uploaded_at": "2025-01-15T10:30:00Z"
}
```

### Delete Attachment
```
DELETE /attachments/{attachment_id}
```

Response: `204 No Content`

## Supported File Types

- **Images**: PNG, JPG, JPEG, GIF, SVG
- **Videos**: MP4, MOV, AVI, WEBM
- **Documents**: PDF
- **Logs**: TXT, LOG, JSON, XML

## File Size Limits

- Maximum file size: 10 MB per file
- No limit on number of files (subject to server storage)

## Permissions

- **View**: All authenticated users can view attachments
- **Upload**: All authenticated users can upload attachments
- **Delete**: Only the uploader or users with Admin role can delete attachments

## Styling

The component uses Tailwind CSS for styling and follows the application's design system:

- **Colors**: Blue for primary actions, red for delete actions
- **Spacing**: Consistent padding and margins
- **Responsive**: Mobile-first design with responsive grid
- **Hover Effects**: Smooth transitions on interactive elements

## Future Enhancements

1. **Drag-and-Drop Upload**: Allow users to drag files directly onto the component
2. **Bulk Delete**: Select multiple attachments and delete them at once
3. **File Preview Modal**: View images and PDFs in a modal without downloading
4. **Attachment Comments**: Add comments or notes to specific attachments
5. **Version History**: Track multiple versions of the same file
6. **Compression**: Automatically compress large images before upload
7. **Cloud Storage Integration**: Store files in S3 or similar cloud storage

## Error Handling

The component handles the following error scenarios:

- **Upload Failures**: Shows error message if upload fails
- **Network Errors**: Displays user-friendly error messages
- **Permission Errors**: Informs user if they lack permission to delete
- **File Size Errors**: Validates file size before upload (to be implemented)
- **File Type Errors**: Validates file type before upload (to be implemented)

## Accessibility

- **Keyboard Navigation**: All interactive elements are keyboard accessible
- **Screen Reader Support**: Proper ARIA labels and semantic HTML
- **Focus Indicators**: Clear focus states for keyboard users
- **Alt Text**: Images have descriptive alt text

## Integration Example

Here's a complete example of integrating the AttachmentsSection into a bug details page:

```tsx
import { useState, useEffect } from 'react'
import AttachmentsSection from '../qa/AttachmentsSection'
import CommentsSection from '../qa/CommentsSection'

export default function BugDetails({ bugId }: { bugId: string }) {
  const [bug, setBug] = useState(null)
  
  useEffect(() => {
    loadBug()
  }, [bugId])
  
  const loadBug = async () => {
    const data = await api.getBug(bugId)
    setBug(data)
  }
  
  return (
    <div className="space-y-6">
      {/* Bug information */}
      <div>
        <h1>{bug?.title}</h1>
        <p>{bug?.description}</p>
      </div>
      
      {/* Comments */}
      <CommentsSection
        entityType="bug"
        entityId={bugId}
        showSystemNotes={true}
      />
      
      {/* Attachments */}
      <AttachmentsSection
        entityType="bug"
        entityId={bugId}
        onAttachmentAdded={() => {
          // Optionally show a success notification
          console.log('Attachment uploaded successfully')
        }}
      />
    </div>
  )
}
```

## Testing

To test the AttachmentsSection component:

1. **Upload Test**: Upload various file types and sizes
2. **Download Test**: Verify files can be downloaded correctly
3. **Delete Test**: Test deletion with different user permissions
4. **Error Test**: Test error handling for failed uploads
5. **Responsive Test**: Test on different screen sizes
6. **Permission Test**: Verify only authorized users can delete

## Requirements Satisfied

This component satisfies the following requirements from the QA Testing and Bug Management spec:

- **Requirement 6.12**: Support attaching files or images to comments
- **Task 14.4**: Create AttachmentsSection component
  - Display list of attachments (screenshots, logs, videos)
  - Add upload button
  - Show file name, type, size, uploader
  - Add download and delete actions
