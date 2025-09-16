# Context
File name: Plan).\n    -   `SelectivePageExtractor`: Creates a smaller, temporary PDF containing only the relevant pages to save processing time.\n    -   `ContentExtractor`: Uses Google Document AI and OCR (Tesseract) to extract all text and layout information from the temporary PDF.\n    -   `AIInterpreter`: Sends the extracted content to Claude AI with a specialized prompt to analyze and structure the data.\n    -   `DataValidator`: Cleans the AI-generated data and calculates preliminary costs.\n5.  **Persistence**: The worker saves the final, structured data into the `processing_results` table and updates the `documents` table status to `COMPLETED`.\n6.  **Redirection to Results**: The `/processing` page sees the `COMPLETED` status and automatically redirects the user to `/estimate?source=pipeline&documentId={docId}`.\n7.  **Display**: The estimate page fetches the final data from `/api/v1/pipeline/results/{docId}` and displays it.\n\n### Workflow B: The Synchronous "Claude Test" Utility\n\nThis is a developer utility for quick, direct-to-AI analysis, bypassing the main pipeline.\n\n1.  **Upload**: A user uploads a PDF via the `/claude-test` page.\n2.  **Synchronous Processing**: The frontend calls `/api/proxy/claude-process/process-with-claude`.\n3.  **Direct-to-Claude**: This backend endpoint (`claude_process.py`) does the following in a single, synchronous request:\n    -   Reads the entire PDF file.\n    -   Encodes it to a **base64 string**.\n    -   Sends the base64 PDF directly to the Claude API with a standardized prompt from `prompts/roofing_estimation_prompt.txt`.\n    -   Saves the structured JSON response to the `processing_results` table.\n4.  **Redirection to Results**: Upon a successful response from the backend, the frontend redirects the user *directly* to `/estimate?document_id={docId}&source=claude-direct`.\n\n---\n\n## 3. Agent Instructions & Coding Guidelines\n\nAs an AI agent, you must adhere to these patterns to maintain code quality and consistency.\n\n### General\n-   **Distinguish Between Workflows**: Always be clear about which workflow you are modifying. A change for the main pipeline will likely involve the `app/services/processing_stages/` directory, while a change for the test utility will involve `app/api/v1/endpoints/claude_process.py`.\n-   **Modularity**: The main pipeline is designed to be modular. When modifying a stage (e.g., `ContentExtractor`), ensure its inputs and outputs remain consistent to avoid breaking the chain.\n-   **Configuration over Code**: Use environment variables (`.env`) for API keys, model names, and other configuration. Do not hardcode these values.\n\n### Backend (Python/FastAPI)\n-   **Asynchronicity**: The FastAPI application is fully `async`. All database calls within API endpoints must use `await`.\n-   **Celery Sync/Async Bridge**: The Celery worker runs in a synchronous process. To call `async` functions (like the pipeline services) from a synchronous Celery task, you **must** use `asyncio.run()`.\n-   **Database Sessions**:\n    -   In FastAPI endpoints, get the session via `db: AsyncSession = Depends(get_db)`.\n    -   In Celery tasks, you must create a new session within the task.\n-   **Data Validation**: Use Pydantic models (`app/schemas/`) for all API request and response bodies to ensure type safety and validation.\n-   **Error Handling**: Use `try...except` blocks to catch potential errors and raise appropriate `HTTPException`s with clear details.\n\n### Frontend (TypeScript/Next.js)\n-   **State Management**: Use React Query (`useQuery`, `useMutation`) for managing all server state (fetching, creating, updating data).\n-   **API Client**: Use the existing `apiClient` in `lib/api.ts` for making type-safe requests to the backend.\n-   **Component Structure**: Follow the existing component-based architecture. Use `shadcn/ui` components for consistency.\n-   **User Feedback**: Always provide clear loading, error, and success states for any asynchronous operation. The `/processing` page is a good example of this.\n\n### Example Scenario: Adding a New Metadata Field\n\n1.  **Database**: Add the new field to the `ProcessingResults` model in `app/models/results.py`.\n2.  **Pipeline**: Modify the relevant pipeline stage (e.g., `AIInterpreter`) to extract or generate this new field.\n3.  **Persistence**: Ensure the Celery task (`new_pdf_processing.py`) correctly saves this new field to the `ProcessingResults` table.\n4.  **API Endpoint**: Update the `/api/v1/pipeline/results/{document_id}` endpoint to include the new field in its response.\n5.  **Frontend**: Update the `estimate/page.tsx` component and its sub-components to display the new field.\n\nBy following this guide, you will be able to make accurate, high-quality contributions to the Brant Roofing System.\n\n⚠️ WARNING: NEVER MODIFY THIS SECTION ⚠️\n[START OF EXECUTION PROTOCOL]
# Execution Protocol:
...
[END OF EXECUTION PROTOCOL]\n⚠️ WARNING: NEVER MODIFY THIS SECTION ⚠️\n\n# Analysis\n[Code investigation results]\n\n# Proposed Solution\n[Action plan]\n\n# Current execution step: "3. Analysis"\n- Eg. "2. Create the task file"\n\n# Task Progress\n[Change history with timestamps]\n\n# Final Review:\n[Post-completion summary]\n
Created at: 2025-09-15_1
Created by: 2025-09-15_23:35:39
Main branch: ubuntu
Task Branch: main
Yolo Mode: On

# Task Description: Brant Roofing System AI Agent

## 1. Project Overview

**Your primary objective is to assist in developing and maintaining the Brant Roofing System.**

This is an AI-powered, full-stack application designed to automate the creation of commercial roofing estimates. It processes large PDF documents (like architectural blueprints), extracts key information using a hybrid of computer vision and large language models, and presents the data in a structured estimate format.

### Core Technologies
-   **Backend**: Python with FastAPI for the API, SQLAlchemy (async) for the ORM, and Pydantic for data validation.
-   **Asynchronous Tasks**: Celery with a Redis broker for handling long-running PDF processing jobs in the background.
-   **Database**: PostgreSQL, with key models including `Document` and `ProcessingResults`.
-   **AI & OCR**: A multi-stage pipeline using Google Document AI for OCR and Claude AI for interpretation and analysis.
-   **Frontend**: Next.js with TypeScript and the App Router. It uses React Query for server state management and shadcn/ui for components.
-   **Containerization**: The entire application is orchestrated with Docker Compose, defining the `api`, `worker`, and `redis` services.

---

## 2. System Architecture & Key Workflows

It is critical to understand that there are **two distinct processing workflows** in this application.

### Workflow A: The Standard Asynchronous Pipeline (Main User Flow)

This is the primary, production-intended workflow for processing documents.

1.  **Upload**: A user uploads a PDF via the main dashboard. The frontend hits `/api/proxy/uploads/upload`.
2.  **Queueing**: The backend saves the file, creates a `Document` record in the database, and queues a Celery background task (`process_pdf_with_pipeline`) to process it.
3.  **Monitoring UI**: The user is redirected to the `/processing?documents={docId}` page. This page polls the `/api/v1/pipeline/status/{docId}` endpoint every few seconds to check the status.
4.  **Background Processing (Celery Worker)**: The worker executes a sophisticated, multi-stage pipeline:
    -   `IndexPageAnalyzer`: Scans the first page to find a table of contents and identify relevant pages (e.g., Roof# Context
File name: task/brant-roofing-system-ai-agent_2025-09-15_1
Created at: 
Created by: 
Main branch: 
Task Branch: 
Yolo Mode: On

# Task Description: Brant Roofing System AI Agent

## 1. Project Overview

**Your primary objective is to assist in developing and maintaining the Brant Roofing System.**

This is an AI-powered, full-stack application designed to automate the creation of commercial roofing estimates. It processes large PDF documents (like architectural blueprints), extracts key information using a hybrid of computer vision and large language models, and presents the data in a structured estimate format.

### Core Technologies
-   **Backend**: Python with FastAPI for the API, SQLAlchemy (async) for the ORM, and Pydantic for data validation.
-   **Asynchronous Tasks**: Celery with a Redis broker for handling long-running PDF processing jobs in the background.
-   **Database**: PostgreSQL, with key models including `Document` and `ProcessingResults`.
-   **AI & OCR**: A multi-stage pipeline using Google Document AI for OCR and Claude AI for interpretation and analysis.
-   **Frontend**: Next.js with TypeScript and the App Router. It uses React Query for server state management and shadcn/ui for components.
-   **Containerization**: The entire application is orchestrated with Docker Compose, defining the `api`, `worker`, and `redis` services.

---

## 2. System Architecture & Key Workflows

It is critical to understand that there are **two distinct processing workflows** in this application.

### Workflow A: The Standard Asynchronous Pipeline (Main User Flow)

This is the primary, production-intended workflow for processing documents.

1.  **Upload**: A user uploads a PDF via the main dashboard. The frontend hits `/api/proxy/uploads/upload`.
2.  **Queueing**: The backend saves the file, creates a `Document` record in the database, and queues a Celery background task (`process_pdf_with_pipeline`) to process it.
3.  **Monitoring UI**: The user is redirected to the `/processing?documents={docId}` page. This page polls the `/api/v1/pipeline/status/{docId}` endpoint every few seconds to check the status.
4.  **Background Processing (Celery Worker)**: The worker executes a sophisticated, multi-stage pipeline:
    -   `IndexPageAnalyzer`: Scans the first page to find a table of contents and identify relevant pages (e.g., Roof[START OF EXECUTION PROTOCOL]\n# Execution Protocol:\n\n## 1. Create feature branch\n1. Create a new task branch from [MAIN_BRANCH]:\n  \n2. Add the branch name to the [TASK_FILE] under "Task Branch."\n3. Verify the branch is active:\n  \n4. Update "Current execution step" in [TASK_FILE] to next step\n\n## 2. Create the task file\n1. Execute command to generate [TASK_FILE_NAME]:\n   \n2. Create [TASK_FILE] with strict naming:\n   \n3. Verify file creation:\n   \n4. Copy ENTIRE Task File Template into new file\n5. Insert Execution Protocol EXACTLY, in verbatim, by:\n-   - Copying text between "-- [START OF EXECUTION PROTOCOL]" and "-- [END OF EXECUTION PROTOCOL]"\n-   - Adding "⚠️ WARNING: NEVER MODIFY THIS SECTION ⚠️" both as header and a footer\n+   a. Find the protocol content between [START OF EXECUTION PROTOCOL] and [END OF EXECUTION PROTOCOL] markers above\n+   b. In the task file:\n+      1. Replace "[START OF EXECUTION PROTOCOL]
# Execution Protocol:
...
[END OF EXECUTION PROTOCOL]" with the ENTIRE protocol content from step 5a\n+      2. Keep the warning header and footer: "⚠️ WARNING: NEVER MODIFY THIS SECTION ⚠️"\n6. Systematically populate ALL placeholders:\n   a. Run commands for dynamic values:\n      \n   b. Fill [PROJECT_OVERVIEW] by recursively analyzing mentioned files:\n      \n7. Cross-verify completion:\n   - Check ALL template sections exist\n   - Confirm NO existing task files were modified\n8. Set the "Current execution step" tp the name and number of the next planned step of the exectution protocol\n9. Print full task file contents for verification\n\n<<< HALT IF NOT [YOLO_MODE]: Confirm [TASK_FILE] with user before proceeding >>>\n\n## 3. Analysis\n1. Analyze code related to [TASK]:\n  - Identify core files/functions\n  - Trace code flow\n2. Document findings in "Analysis" section\n3. Set the "Current execution step" tp the name and number of the next planned step of the exectution protocol\n\n<<< HALT IF NOT [YOLO_MODE]: Wait for analysis confirmation >>>\n\n## 4. Proposed Solution\n1. Create plan based on analysis:\n  - Research dependencies\n  - Add to "Proposed Solution"\n2. NO code changes yet\n3. Set the "Current execution step" tp the name and number of the next planned step of the exectution protocol\n\n<<< HALT IF NOT [YOLO_MODE]: Get solution approval >>>\n\n## 5. Iterate on the task\n1. Review "Task Progress" history\n2. Plan next changes\n3. Present for approval:\n  \n4. If approved:\n  - Implement changes\n  - Append to "Task Progress":\n    \n5. Ask user: "Status: SUCCESSFUL/UNSUCCESSFUL?"\n6. If UNSUCCESSFUL: Repeat from 5.1\n7. If SUCCESSFUL:\n  a. Commit? → \n  b. More changes? → Repeat step 5\n  c. Continue? → Proceed\n8. Set the "Current execution step" tp the name and number of the next planned step of the exectution protocol\n\n## 6. Task Completion\n1. Stage changes (exclude task files):\n  \n2. Commit with message:\n  \n3. Set the "Current execution step" tp the name and number of the next planned step of the exectution protocol\n\n<<< HALT IF NOT [YOLO_MODE]: Confirm merge with [MAIN_BRANCH] >>>\n\n## 7. Merge Task Branch\n1. Merge explicitly:\n  \n2. Verify merge:\n  \n3. Set the "Current execution step" tp the name and number of the next planned step of the exectution protocol\n\n## 8. Delete Task Branch\n1. Delete if approved:\n  \n2. Set the "Current execution step" tp the name and number of the next planned step of the exectution protocol\n\n## 9. Final Review\n1. Complete "Final Review" after user confirmation\n2. Set step to "All done!"\n\n[END OF EXECUTION PROTOCOL]\n