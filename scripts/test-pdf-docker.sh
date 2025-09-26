#!/bin/bash
# Test script to verify PDF conversion works in Docker container

echo "Testing PDF conversion in Docker container..."
echo "=============================================="

# Build the backend image
echo "Building backend image..."
docker build -f backend.Dockerfile -t brant-backend-test .

if [ $? -ne 0 ]; then
    echo "❌ Failed to build backend image"
    exit 1
fi

echo "✅ Backend image built successfully"

# Run the test in the container
echo "Running PDF conversion test in container..."
docker run --rm -v "$(pwd)/tests:/app/tests" brant-backend-test python -c "
import os
import tempfile
from pathlib import Path
from pdf2image import convert_from_path

print('Testing PDF to image conversion...')

# Find a test PDF
test_pdf = None
for pdf_file in Path('/app/tests/mcdonalds collection').glob('*.pdf'):
    test_pdf = str(pdf_file)
    break

if not test_pdf:
    print('❌ No test PDF found')
    exit(1)

print(f'✅ Found test PDF: {test_pdf}')

# Test conversion
try:
    with tempfile.TemporaryDirectory() as temp_dir:
        images = convert_from_path(
            test_pdf,
            output_folder=temp_dir,
            first_page=1,
            last_page=1,
            fmt='jpeg'
        )
        
        print(f'✅ Successfully converted PDF to {len(images)} image(s)')
        
        # Check if images were created
        image_files = list(Path(temp_dir).glob('*.jpg'))
        if image_files:
            print(f'✅ Image files created: {[f.name for f in image_files]}')
            for img_file in image_files:
                size_mb = img_file.stat().st_size / (1024 * 1024)
                print(f'  - {img_file.name}: {size_mb:.2f} MB')
        else:
            print('❌ No image files were created')
            exit(1)
            
except Exception as e:
    print(f'❌ PDF conversion failed: {e}')
    exit(1)

print('✅ All tests passed! PDF conversion is working.')
"

if [ $? -eq 0 ]; then
    echo "✅ PDF conversion test passed!"
else
    echo "❌ PDF conversion test failed!"
    exit 1
fi
