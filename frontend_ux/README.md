# DT Commercial Roofing - AI-Powered Estimation Platform

A modern, cutting-edge web application for commercial roofing estimators that automates roofing installation and repair estimates using Google Document AI and Claude AI.

## 🏗️ Features

- **AI-Powered PDF Processing**: Upload roofing documents and extract comprehensive data using Google Document AI and Claude AI
- **Comprehensive Estimates**: Generate detailed estimates with materials, labor, permits, and edge cases
- **Source Citations**: All AI-extracted data includes citations linking back to source PDF pages
- **Dual AI Analysis**: Compare Google Document AI and Claude AI results in separate tabs
- **Export Capabilities**: Export estimates in PDF, Excel, and CSV formats
- **User Management**: Authentication system with user and admin roles
- **Real-time Processing**: Animated loading screens with live extraction previews

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Git

### 1. Clone and Setup

\`\`\`bash
git clone <repository-url>
cd roofing-dashboard
cp .env.example .env.development
\`\`\`

### 2. Configure Environment Variables

Edit `.env.development` with your Google Cloud and Anthropic API credentials:

\`\`\`bash
# Google Cloud Configuration
GOOGLE_APPLICATION_CREDENTIALS="path/to/your/credentials.json"
GOOGLE_CLOUD_PROJECT_ID="your-project-id"
DOCUMENT_AI_PROCESSOR_ID="your-processor-id"
DOCUMENT_AI_LOCATION="us"
ENABLE_DOCUMENT_AI=true

# Anthropic Claude AI
ANTHROPIC_API_KEY="your-anthropic-api-key"

# Database (automatically configured for Docker)
DATABASE_URL="postgresql://roofing_user:roofing_pass@db:5432/roofing_db"
\`\`\`

### 3. Start Development Environment

\`\`\`bash
# Start all services with Docker
npm run docker:dev

# Or use the setup script
chmod +x scripts/dev-setup.sh
./scripts/dev-setup.sh
\`\`\`

### 4. Access the Application

- **Application**: http://localhost:3000
- **Database Admin**: http://localhost:8080 (Adminer)
- **Email Testing**: http://localhost:8025 (Mailhog)

## 🛠️ Development

### Available Scripts

\`\`\`bash
npm run dev              # Start Next.js development server
npm run build            # Build for production
npm run start            # Start production server
npm run lint             # Run ESLint
npm run type-check       # Run TypeScript checks

# Docker Commands
npm run docker:dev       # Start development environment
npm run docker:prod      # Start production environment
npm run docker:build     # Build Docker images
npm run docker:down      # Stop all containers

# Database Commands
npm run db:migrate       # Run Prisma migrations
npm run db:seed          # Seed development data
npm run db:studio        # Open Prisma Studio
npm run db:reset         # Reset database
\`\`\`

### Project Structure

\`\`\`
├── app/                    # Next.js App Router pages
├── components/             # React components
│   ├── auth/              # Authentication components
│   ├── dashboard/         # Dashboard components
│   ├── estimate/          # Estimate page components
│   ├── export/            # Export functionality
│   ├── processing/        # AI processing components
│   └── ui/                # shadcn/ui components
├── lib/                   # Utility functions
├── prisma/                # Database schema and migrations
├── scripts/               # Setup and deployment scripts
├── database/              # Docker database configuration
├── nginx/                 # Nginx configuration
└── monitoring/            # Prometheus monitoring config
\`\`\`

## 🔧 Configuration

### Google Cloud Services Setup

1. **Document AI**: Create a form parser processor in Google Cloud Console
2. **Cloud Storage**: Create a bucket for PDF storage
3. **Service Account**: Create with Document AI, Vision API, and Storage permissions

### Database Schema

The application uses PostgreSQL with Prisma ORM. Key models:
- `Customer`: Client information
- `Estimate`: Roofing estimates with AI analysis
- `Measurement`: Extracted measurements from PDFs
- `LineItem`: Individual estimate line items
- `Document`: Uploaded PDF documents
- `AuditTrail`: Processing history and changes

## 🚢 Deployment

### Development
\`\`\`bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
\`\`\`

### Production
\`\`\`bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
\`\`\`

## 🔍 API Endpoints

- `POST /api/processing` - Process uploaded PDFs with AI
- `GET /api/estimates` - List estimates
- `GET /api/estimates/[id]` - Get specific estimate
- `PUT /api/estimates/[id]` - Update estimate
- `POST /api/export/pdf` - Export PDF report
- `POST /api/export/excel` - Export Excel workbook
- `POST /api/export/csv` - Export CSV data

## 🧪 Testing

\`\`\`bash
npm run test             # Run tests
npm run test:watch       # Run tests in watch mode
npm run test:coverage    # Generate coverage report
\`\`\`

## 📝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 🔒 Security

- All API endpoints require authentication
- PDF uploads are validated and sanitized
- Environment variables for sensitive data
- Rate limiting on API endpoints
- HTTPS in production with SSL certificates

## 📄 License

This project is proprietary software owned by DT Commercial Roofing.

## 🆘 Support

For technical support or questions:
- Create an issue in the repository
- Contact the development team
- Check the troubleshooting guide below

## 🔧 Troubleshooting

### Common Issues

**Docker containers won't start:**
\`\`\`bash
docker-compose down -v
docker system prune -f
npm run docker:dev
\`\`\`

**Database connection issues:**
\`\`\`bash
npm run db:reset
npm run db:migrate
npm run db:seed
\`\`\`

**Google Cloud authentication:**
- Verify `GOOGLE_APPLICATION_CREDENTIALS` path
- Check service account permissions
- Ensure Document AI processor is active

**Missing environment variables:**
- Copy `.env.example` to `.env.development`
- Fill in all required API keys and credentials
- Restart Docker containers after changes
