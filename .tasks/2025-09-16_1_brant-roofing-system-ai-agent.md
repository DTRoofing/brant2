# Context
File name: 2025-09-16_1
Created at: 2025-09-16_01:05:19
Created by: ubuntu
Main branch: main
Task Branch: task/brant-roofing-system-ai-agent_2025-09-16_1
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
    -   `IndexPageAnalyzer`: Scans the first page to find a table of contents and identify relevant pages (e.g., "Roof Plan").
    -   `SelectivePageExtractor`: Creates a smaller, temporary PDF containing only the relevant pages to save processing time.
    -   `ContentExtractor`: Uses Google Document AI and OCR (Tesseract) to extract all text and layout information from the temporary PDF.
    -   `AIInterpreter`: Sends the extracted content to Claude AI with a specialized prompt to analyze and structure the data. It is aware of special document types like "McDonald's" blueprints.
    -   `DataValidator`: Cleans the AI-generated data and calculates preliminary costs.
5.  **Persistence**: The worker saves the final, structured data into the `processing_results` table and updates the `documents` table status to `COMPLETED`.
6.  **Redirection to Results**: The `/processing` page sees the `COMPLETED` status and automatically redirects the user to `/estimate?source=pipeline&documentId={docId}`.
7.  **Display**: The estimate page fetches the final data from `/api/v1/pipeline/results/{docId}` and displays it.

### Workflow B: The Synchronous "Claude Test" Utility

This is a developer utility for quick, direct-to-AI analysis, bypassing the main pipeline.

1.  **Upload**: A user uploads a PDF via the `/claude-test` page.
2.  **Synchronous Processing**: The frontend calls `/api/proxy/claude-process/process-with-claude`.
3.  **Direct-to-Claude**: This backend endpoint (`claude_process.py`) does the following in a single, synchronous request:
    -   Reads the entire PDF file.
    -   Encodes it to a **base64 string**.
    -   Sends the base64 PDF directly to the Claude API with a standardized prompt from `prompts/roofing_estimation_prompt.txt`.
    -   Saves the structured JSON response to the `processing_results` table.
4.  **Redirection to Results**: Upon a successful response from the backend, the frontend redirects the user *directly* to `/estimate?document_id={docId}&source=claude-direct`.

---

## 3. Agent Instructions & Coding Guidelines

As an AI agent, you must adhere to these patterns to maintain code quality and consistency.

### General
-   **Distinguish Between Workflows**: Always be clear about which workflow you are modifying. A change for the main pipeline will likely involve the `app/services/processing_stages/` directory, while a change for the test utility will involve `app/api/v1/endpoints/claude_process.py`.
-   **Modularity**: The main pipeline is designed to be modular. When modifying a stage (e.g., `ContentExtractor`), ensure its inputs and outputs remain consistent to avoid breaking the chain.
-   **Configuration over Code**: Use environment variables (`.env`) for API keys, model names, and other configuration. Do not hardcode these values.

### Backend (Python/FastAPI)
-   **Asynchronicity**: The FastAPI application is fully `async`. All database calls within API endpoints must use `await`.
-   **Celery Sync/Async Bridge**: The Celery worker runs in a synchronous process. To call `async` functions (like the pipeline services) from a synchronous Celery task, you **must** use `asyncio.run()`.
-   **Database Sessions**:
    -   In FastAPI endpoints, get the session via `db: AsyncSession = Depends(get_db)`.
    -   In Celery tasks, you must create a new session within the task.
-   **Data Validation**: Use Pydantic models (`app/schemas/`) for all API request and response bodies to ensure type safety and validation.
-   **Error Handling**: Use `try...except` blocks to catch potential errors and raise appropriate `HTTPException`s with clear details.

### Frontend (TypeScript/Next.js)
-   **State Management**: Use React Query (`useQuery`, `useMutation`) for managing all server state (fetching, creating, updating data).
-   **API Client**: Use the existing `apiClient` in `lib/api.ts` for making type-safe requests to the backend.
-   **Component Structure**: Follow the existing component-based architecture. Use `shadcn/ui` components for consistency.
-   **User Feedback**: Always provide clear loading, error, and success states for any asynchronous operation. The `/processing` page is a good example of this.

### Example Scenario: Adding a New Metadata Field

1.  **Database**: Add the new field to the `ProcessingResults` model in `app/models/results.py`.
2.  **Pipeline**: Modify the relevant pipeline stage (e.g., `AIInterpreter`) to extract or generate this new field.
3.  **Persistence**: Ensure the Celery task (`new_pdf_processing.py`) correctly saves this new field to the `ProcessingResults` table.
4.  **API Endpoint**: Update the `/api/v1/pipeline/results/{document_id}` endpoint to include the new field in its response.
5.  **Frontend**: Update the `estimate/page.tsx` component and its sub-components to display the new field.

By following this guide, you will be able to make accurate, high-quality contributions to the Brant Roofing System.

⚠️ WARNING: NEVER MODIFY THIS SECTION ⚠️
[START OF EXECUTION PROTOCOL]
# Execution Protocol:

## 1. Create feature branch
1. Create a new task branch from [MAIN_BRANCH]:
  ```
  git checkout -b task/[TASK_IDENTIFIER]_[TASK_DATE_AND_NUMBER]
  ```
2. Add the branch name to the [TASK_FILE] under "Task Branch."
3. Verify the branch is active:
  ```
  git branch --show-current
  ```
4. Update "Current execution step" in [TASK_FILE] to next step

## 2. Create the task file
1. Execute command to generate [TASK_FILE_NAME]:
   ```
   [TASK_FILE_NAME]="$(date +%Y-%m-%d)_$(($(ls -1q .tasks | grep -c $(date +%Y-%m-%d)) + 1))"
   ```
2. Create [TASK_FILE] with strict naming:
   ```
   mkdir -p .tasks && touch ".tasks/${TASK_FILE_NAME}_[TASK_IDENTIFIER].md"
   ```
3. Verify file creation:
   ```
   ls -la ".tasks/${TASK_FILE_NAME}_[TASK_IDENTIFIER].md"
   ```
4. Copy ENTIRE Task File Template into new file
5. Insert Execution Protocol EXACTLY, in verbatim, by:
-   - Copying text between "-- [START OF EXECUTION PROTOCOL]" and "-- [END OF EXECUTION PROTOCOL]"
-   - Adding "⚠️ WARNING: NEVER MODIFY THIS SECTION ⚠️" both as header and a footer
+   a. Find the protocol content between [START OF EXECUTION PROTOCOL] and [END OF EXECUTION PROTOCOL] markers above
+   b. In the task file:
+      1. Replace "[FULL EXECUTION PROTOCOL COPY]" with the ENTIRE protocol content from step 5a
+      2. Keep the warning header and footer: "⚠️ WARNING: NEVER MODIFY THIS SECTION ⚠️"
6. Systematically populate ALL placeholders:
   a. Run commands for dynamic values:
      ```
      [DATETIME]="$(date +'%Y-%m-%d_%H:%M:%S')"
      [USER_NAME]="$(whoami)"
      [TASK_BRANCH]="$(git branch --show-current)"
      ```
   b. Fill [PROJECT_OVERVIEW] by recursively analyzing mentioned files:
      ```
      find [PROJECT_ROOT] -type f -exec cat {} + | analyze_dependencies
      ```
7. Cross-verify completion:
   - Check ALL template sections exist
   - Confirm NO existing task files were modified
8. Set the "Current execution step" tp the name and number of the next planned step of the exectution protocol
9. Print full task file contents for verification

<<< HALT IF NOT [YOLO_MODE]: Confirm [TASK_FILE] with user before proceeding >>>

## 3. Analysis
1. Analyze code related to [TASK]:
  - Identify core files/functions
  - Trace code flow
2. Document findings in "Analysis" section
3. Set the "Current execution step" tp the name and number of the next planned step of the exectution protocol

<<< HALT IF NOT [YOLO_MODE]: Wait for analysis confirmation >>>

## 4. Proposed Solution
1. Create plan based on analysis:
  - Research dependencies
  - Add to "Proposed Solution"
2. NO code changes yet
3. Set the "Current execution step" tp the name and number of the next planned step of the exectution protocol

<<< HALT IF NOT [YOLO_MODE]: Get solution approval >>>

## 5. Iterate on the task
1. Review "Task Progress" history
2. Plan next changes
3. Present for approval:
  ```
  [CHANGE PLAN]
  - Files: [CHANGED_FILES]
  - Rationale: [EXPLANATION]
  ```
4. If approved:
  - Implement changes
  - Append to "Task Progress":
    ```
    [DATETIME]
    - Modified: [list of files and code changes]
    - Changes: [the changes made as a summary]
    - Reason: [reason for the changes]
    - Blockers: [list of blockers preventing this update from being successful]
    - Status: [UNCONFIRMED|SUCCESSFUL|UNSUCCESSFUL]
    ```
5. Ask user: "Status: SUCCESSFUL/UNSUCCESSFUL?"
6. If UNSUCCESSFUL: Repeat from 5.1
7. If SUCCESSFUL:
  a. Commit? → `git add [FILES] && git commit -m "[SHORT_MSG]"`
  b. More changes? → Repeat step 5
  c. Continue? → Proceed
8. Set the "Current execution step" tp the name and number of the next planned step of the exectution protocol

## 6. Task Completion
1. Stage changes (exclude task files):
  ```
  git add --all :!.tasks/*
  ```
2. Commit with message:
  ```
  git commit -m "[COMMIT_MESSAGE]"
  ```
3. Set the "Current execution step" tp the name and number of the next planned step of the exectution protocol

<<< HALT IF NOT [YOLO_MODE]: Confirm merge with [MAIN_BRANCH] >>>

## 7. Merge Task Branch
1. Merge explicitly:
  ```
  git checkout [MAIN_BRANCH]
  git merge task/[TASK_IDENTIFIER]_[TASK_DATE_AND_NUMBER]
  ```
2. Verify merge:
  ```
  git diff [MAIN_BRANCH] task/[TASK_IDENTIFIER]_[TASK_DATE_AND_NUMBER]
  ```
3. Set the "Current execution step" tp the name and number of the next planned step of the exectution protocol

## 8. Delete Task Branch
1. Delete if approved:
  ```
  git branch -d task/[TASK_IDENTIFIER]_[TASK_DATE_AND_NUMBER]
  ```
2. Set the "Current execution step" tp the name and number of the next planned step of the exectution protocol

## 9. Final Review
1. Complete "Final Review" after user confirmation
2. Set step to "All done!"

[END OF EXECUTION PROTOCOL]
⚠️ WARNING: NEVER MODIFY THIS SECTION ⚠️

# Analysis
[Code investigation results]

# Proposed Solution
[Action plan]

# Current execution step: "3. Analysis"
- Eg. "2. Create the task file"

# Task Progress
[Change history with timestamps]

# Final Review:
[Post-completion summary]

