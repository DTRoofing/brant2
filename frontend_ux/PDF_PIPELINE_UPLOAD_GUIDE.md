# PDF Pipeline Upload Form Guide

## Overview

The new PDF Pipeline Upload form is a comprehensive, user-friendly interface for uploading and processing roofing documents through our hybrid AI pipeline. It combines computer vision and AI processing to extract measurements, detect roof features, and generate accurate estimates.

## Features

### 🚀 **Core Functionality**
- **Drag & Drop Upload**: Intuitive file selection with visual feedback
- **Multi-file Support**: Process multiple PDFs simultaneously
- **Real-time Progress**: Live updates on processing status
- **Hybrid Processing**: Computer vision + AI analysis
- **Feature Detection**: Automatic identification of roof features
- **Cost Estimation**: AI-powered pricing calculations

### 🎯 **Processing Stages**
1. **Document Upload & Validation** - Secure file handling and validation
2. **Document Type Analysis** - Classify document type and processing strategy
3. **Hybrid Content Extraction** - Computer vision + AI text/image extraction
4. **Roof Measurement** - Scale detection and roof feature identification
5. **AI Interpretation** - Claude AI analysis and cost estimation
6. **Estimate Generation** - Comprehensive roofing estimate creation

## Components

### 1. PDFPipelineUpload Component
**Location**: `frontend_ux/components/dashboard/pdf-pipeline-upload.tsx`

**Key Features**:
- Drag and drop file upload
- Real-time progress tracking
- Processing stage visualization
- Error handling and recovery
- Results preview and redirection

**Props**: None (self-contained component)

**State Management**:
```typescript
interface UploadedFile {
  file: File
  id: string
  status: "uploading" | "processing" | "completed" | "error"
  progress: number
  result?: any
  error?: string
}
```

### 2. Upload Page
**Location**: `frontend_ux/app/upload/page.tsx`

**Features**:
- Dedicated upload interface
- Feature showcase
- Processing stage explanation
- Benefits and capabilities overview

### 3. Dashboard Integration
**Location**: `frontend_ux/app/dashboard/page.tsx`

**Integration**:
- Replaces original UploadZone component
- Enhanced AI features description
- Updated feature badges

## API Integration

### Backend Endpoints
The upload form integrates with the following API endpoints:

```typescript
// Upload document
POST /api/v1/documents/upload
Response: { document_id: string, filename: string, size: number }

// Start pipeline processing
POST /api/v1/pipeline/process/{document_id}
Response: { task_id: string, status: string }

// Get pipeline status
GET /api/v1/pipeline/status/{document_id}
Response: { status: string, error?: string }

// Get pipeline results
GET /api/v1/pipeline/results/{document_id}
Response: { results: PipelineResults }
```

### Pipeline Results Structure
```typescript
interface PipelineResults {
  roof_area_sqft: number
  materials: string[]
  estimated_cost: number
  confidence: number
  roof_features: RoofFeature[]
  complexity_factors: string[]
  verification: VerificationResult
}

interface RoofFeature {
  type: string
  count: number
  impact: "low" | "medium" | "high"
  description: string
}
```

## Usage

### 1. Basic Upload
```tsx
import { PDFPipelineUpload } from "@/components/dashboard/pdf-pipeline-upload"

export default function MyPage() {
  return (
    <div>
      <PDFPipelineUpload />
    </div>
  )
}
```

### 2. Dashboard Integration
The component is already integrated into the dashboard at `/dashboard`

### 3. Dedicated Upload Page
Access the full-featured upload page at `/upload`

## User Experience

### Upload Flow
1. **File Selection**: Drag & drop or click to browse
2. **File Validation**: Automatic PDF validation
3. **Processing Start**: Click "Process with Hybrid Pipeline"
4. **Real-time Updates**: Watch processing stages progress
5. **Results Display**: View extracted data and features
6. **Estimate Redirect**: Automatic redirect to estimate page

### Visual Feedback
- **Drag States**: Visual feedback during drag operations
- **Progress Bars**: Individual file progress tracking
- **Status Badges**: Clear status indicators (uploading, processing, completed, error)
- **Stage Icons**: Visual representation of processing stages
- **Loading States**: Spinners and progress indicators

## Error Handling

### File Validation
- **File Type**: Only PDF files accepted
- **File Size**: Configurable size limits
- **Multiple Files**: Batch processing support

### Processing Errors
- **Network Issues**: Automatic retry with exponential backoff
- **API Errors**: User-friendly error messages
- **Timeout Handling**: Graceful timeout management
- **Recovery Options**: Retry failed uploads

## Styling and Theming

### Design System
- **Shadcn/ui Components**: Consistent with app design system
- **Responsive Design**: Mobile-first approach
- **Accessibility**: ARIA labels and keyboard navigation
- **Dark Mode**: Automatic theme adaptation

### Customization
```css
/* Custom upload zone styling */
.upload-zone {
  border: 2px dashed theme('colors.border');
  border-radius: theme('borderRadius.lg');
  transition: all 0.2s ease;
}

.upload-zone:hover {
  border-color: theme('colors.primary');
  background: theme('colors.primary/5');
}
```

## Testing

### Manual Testing
1. Open `/upload` page
2. Drag and drop a PDF file
3. Click "Process with Hybrid Pipeline"
4. Watch processing stages progress
5. Verify results display and redirect

### Test File
Use `frontend_ux/test-upload-form.html` for isolated testing without React dependencies.

## Performance

### Optimization
- **Lazy Loading**: API client imported only when needed
- **Debounced Updates**: Efficient state updates
- **Memory Management**: Proper cleanup of file objects
- **Batch Processing**: Efficient multi-file handling

### Monitoring
- **Progress Tracking**: Real-time progress updates
- **Error Logging**: Comprehensive error tracking
- **Performance Metrics**: Upload and processing times

## Security

### File Handling
- **Client-side Validation**: File type and size checks
- **Secure Upload**: HTTPS-only file transmission
- **Input Sanitization**: Safe file name handling
- **Error Boundaries**: Graceful error containment

## Future Enhancements

### Planned Features
- **Batch Processing**: Process multiple files in parallel
- **Progress Persistence**: Resume interrupted uploads
- **File Preview**: Thumbnail generation for PDFs
- **Advanced Filtering**: File type and size filtering
- **Upload History**: Track previous uploads
- **Real-time Collaboration**: Multi-user upload support

### API Improvements
- **WebSocket Updates**: Real-time processing updates
- **Chunked Upload**: Large file support
- **Resume Capability**: Resume failed uploads
- **Progress Streaming**: Live progress updates

## Troubleshooting

### Common Issues
1. **Upload Stuck at 0%**: Check API server status
2. **File Not Accepted**: Ensure file is PDF format
3. **Processing Timeout**: Check network connection
4. **Results Not Loading**: Verify API endpoints

### Debug Mode
Enable debug logging by setting `localStorage.setItem('debug', 'true')` in browser console.

## Support

For technical support or feature requests, please contact the development team or create an issue in the project repository.
