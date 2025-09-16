# V0.dev Prompt: DT Roofing Blueprint Upload Interface

Create a React component for a professional roofing estimation application with the following specifications:

## Component Requirements

### **File Upload Interface**
- Drag & drop area for PDF files only (max 100MB)
- Visual feedback for drag states (hover, dragging, error states)
- File validation with clear error messages for:
  - File type restrictions (PDF only)
  - File size limits (100MB max)
  - Corrupt or invalid files
- Progress bar during upload with percentage and file name
- Upload queue showing multiple files if needed

### **Processing Status Dashboard**
- Real-time status updates for uploaded documents:
  - "Queued for Processing" (blue)
  - "Processing OCR..." (yellow/orange)
  - "Extracting Measurements..." (orange)
  - "Completed" (green)
  - "Failed" (red with error details)
- Estimated time remaining for each processing stage
- Cancel processing button for queued items

### **Document Preview Section**
- Thumbnail preview of uploaded PDF (first page)
- Document metadata display:
  - File name, size, upload time
  - Number of pages detected
  - Processing confidence score (when available)
- Download original document button

### **Measurement Results Display**
- Table showing extracted measurements:
  - Area (square feet)
  - Confidence score (color-coded: >90% green, 70-90% yellow, <70% red)
  - Source location (page number, coordinates)
  - Measurement type (roof area, wall area, etc.)
- Edit functionality for manual corrections
- Add manual measurements button

### **Estimation Summary Panel**
- Total roof area calculation
- Material quantities breakdown
- Labor estimates
- Total project cost estimate
- Export to PDF button
- Save estimate button

## Design Requirements

### **Visual Style**
- Professional construction industry aesthetic
- Color scheme: Navy blue (#1e3a8a), construction orange (#ea580c), neutral grays
- Clean, modern layout with plenty of white space
- Construction-themed icons (hard hat, blueprints, tools)

### **Layout**
- Two-column layout on desktop
- Left column: Upload interface and processing status
- Right column: Preview and results
- Responsive design for tablet and mobile
- Sticky header with company branding

### **Interactive Elements**
- Smooth transitions and animations
- Loading spinners for processing states
- Toast notifications for success/error messages
- Hover effects on buttons and cards
- Expandable sections for detailed information

## Technical Specifications

### **State Management**
- File upload state with progress tracking
- Processing status polling (every 2 seconds)
- Form validation state
- Error handling state

### **API Integration Hooks**
```typescript
// Expected API calls (implement as placeholder functions)
const uploadDocument = async (file: File) => {
  // POST /api/v1/upload
  // Returns: { document_id, status, message }
}

const getProcessingStatus = async (documentId: string) => {
  // GET /api/v1/documents/{id}/status
  // Returns: { status, progress, measurements, errors }
}

const updateMeasurement = async (measurementId: string, newValue: number) => {
  // PATCH /api/v1/measurements/{id}
  // Returns: { updated_measurement }
}
```

### **Component Props Interface**
```typescript
interface UploadInterfaceProps {
  onDocumentUploaded?: (documentId: string) => void;
  onEstimateComplete?: (estimate: EstimateData) => void;
  maxFileSize?: number; // bytes
  allowedFormats?: string[];
  projectId?: string;
}
```

## Accessibility Requirements
- ARIA labels for all interactive elements
- Keyboard navigation support
- Screen reader compatibility
- Color contrast compliance (WCAG AA)
- Focus management for file upload

## Sample Data Structure
Use this for demonstration:
```json
{
  "document": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "filename": "roof-blueprint-2024.pdf",
    "size": 2048576,
    "pages": 3,
    "status": "completed"
  },
  "measurements": [
    {
      "id": "measurement-1",
      "area_sf": 2340.5,
      "confidence": 0.92,
      "type": "roof_area",
      "page": 1,
      "coordinates": [120, 340, 890, 650]
    }
  ],
  "estimate": {
    "total_area": 2340.5,
    "material_cost": 12500,
    "labor_cost": 8750,
    "total_cost": 21250
  }
}
```

Build this as a single, self-contained React component with TypeScript, using Tailwind CSS for styling and modern React patterns (hooks, functional components). Include realistic placeholder data and interactive states to demonstrate all functionality.
