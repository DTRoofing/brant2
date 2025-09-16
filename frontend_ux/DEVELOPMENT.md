# Development Guide

## Getting Started with Cursor IDE

### 1. Initial Setup

After cloning the repository, Cursor IDE will automatically:
- Suggest installing recommended extensions
- Load workspace settings for optimal development
- Configure TypeScript and Tailwind CSS IntelliSense

### 2. Recommended Extensions

The project includes a `.vscode/extensions.json` file with recommended extensions:
- **TypeScript**: Enhanced TypeScript support
- **Prettier**: Code formatting
- **ESLint**: Code linting
- **Tailwind CSS IntelliSense**: Tailwind class suggestions
- **Prisma**: Database schema support
- **Docker**: Container management
- **GitHub Copilot**: AI-powered code completion

### 3. Development Workflow

#### Quick Start
\`\`\`bash
# 1. Copy environment file
cp .env.example .env.development

# 2. Start development environment
npm run docker:dev

# 3. Open in browser
open http://localhost:3000
\`\`\`

#### Database Development
\`\`\`bash
# View database in Prisma Studio
npm run db:studio

# Reset database with fresh data
npm run db:reset

# Run migrations
npm run db:migrate
\`\`\`

#### Debugging

**Server-Side Debugging:**
1. Use the "Next.js: debug server-side" launch configuration
2. Set breakpoints in API routes or server components
3. Start debugging with F5

**Client-Side Debugging:**
1. Use the "Next.js: debug client-side" launch configuration
2. Set breakpoints in client components
3. Debug in Chrome DevTools

**Full Stack Debugging:**
1. Use the "Next.js: debug full stack" configuration
2. Debug both server and client simultaneously

### 4. Code Organization

#### Component Structure
\`\`\`
components/
├── auth/           # Authentication components
├── dashboard/      # Dashboard-specific components
├── estimate/       # Estimate page components
├── export/         # Export functionality
├── processing/     # AI processing components
└── ui/            # Reusable UI components (shadcn/ui)
\`\`\`

#### API Routes
\`\`\`
app/api/
├── estimates/      # Estimate CRUD operations
├── processing/     # AI processing endpoints
└── export/         # Export functionality
\`\`\`

### 5. Environment Variables

Create `.env.development` with:
\`\`\`bash
# Google Cloud
GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"
GOOGLE_CLOUD_PROJECT_ID="your-project-id"
DOCUMENT_AI_PROCESSOR_ID="your-processor-id"
DOCUMENT_AI_LOCATION="us"
ENABLE_DOCUMENT_AI=true

# Anthropic Claude
ANTHROPIC_API_KEY="your-api-key"

# Database (Docker)
DATABASE_URL="postgresql://roofing_user:roofing_pass@localhost:5432/roofing_db"
\`\`\`

### 6. Testing

\`\`\`bash
# Run all tests
npm run test

# Run tests in watch mode
npm run test:watch

# Generate coverage report
npm run test:coverage
\`\`\`

### 7. Code Quality

The project uses:
- **ESLint**: Code linting with Next.js rules
- **Prettier**: Code formatting
- **TypeScript**: Type checking
- **Husky**: Git hooks for pre-commit checks

### 8. Docker Development

#### Services
- **app**: Next.js application (port 3000)
- **db**: PostgreSQL database (port 5432)
- **redis**: Redis cache (port 6379)
- **adminer**: Database admin UI (port 8080)
- **mailhog**: Email testing (port 8025)

#### Useful Commands
\`\`\`bash
# View logs
docker-compose logs -f app

# Execute commands in container
docker-compose exec app npm run db:migrate

# Rebuild containers
docker-compose up --build

# Clean up
docker-compose down -v
docker system prune -f
\`\`\`

### 9. AI Integration

#### Google Document AI
- Processes PDF documents for text extraction
- Configured via `DOCUMENT_AI_PROCESSOR_ID`
- Results stored in database with confidence scores

#### Claude AI
- Provides expert roofing analysis
- Uses detailed prompts for comprehensive estimates
- Displays results in separate tab

### 10. Troubleshooting

#### Common Issues

**TypeScript Errors:**
- Restart TypeScript server: Cmd+Shift+P → "TypeScript: Restart TS Server"
- Check `tsconfig.json` configuration

**Docker Issues:**
\`\`\`bash
# Reset Docker environment
docker-compose down -v
docker system prune -f
npm run docker:dev
\`\`\`

**Database Issues:**
\`\`\`bash
# Reset database
npm run db:reset
npm run db:seed
\`\`\`

**Hot Reload Not Working:**
- Check file watchers in Docker
- Restart development server
- Clear Next.js cache: `rm -rf .next`

#### Performance Tips

1. **Use TypeScript strict mode** for better error catching
2. **Enable Prettier on save** for consistent formatting
3. **Use Tailwind CSS IntelliSense** for class suggestions
4. **Leverage Copilot** for faster development
5. **Use Prisma Studio** for database inspection

### 11. Deployment

#### Development
\`\`\`bash
npm run docker:dev
\`\`\`

#### Production
\`\`\`bash
npm run docker:prod
\`\`\`

#### Environment-Specific Configs
- Development: `docker-compose.dev.yml`
- Production: `docker-compose.prod.yml`
