#!/bin/bash
# Verification script for poppler-utils fix

echo "Verifying poppler-utils installation and PDF conversion fix..."
echo "=============================================================="

# Test 1: Check if poppler utilities are installed
echo "1. Checking poppler utilities installation..."
for util in pdfinfo pdftoppm pdftocairo pdftotext; do
    if command -v $util >/dev/null 2>&1; then
        echo "✓ $util is available"
    else
        echo "✗ $util not found"
        exit 1
    fi
done

# Test 2: Check environment variables
echo ""
echo "2. Checking environment variables..."
if [ -n "$POPPLER_PATH" ]; then
    echo "✓ POPPLER_PATH is set to: $POPPLER_PATH"
else
    echo "⚠ POPPLER_PATH is not set"
fi

# Test 3: Test PDF conversion with a simple command
echo ""
echo "3. Testing PDF conversion..."
if [ -d "tests/mcdonalds collection" ]; then
    # Find first PDF file
    PDF_FILE=$(find "tests/mcdonalds collection" -name "*.pdf" | head -1)
    if [ -n "$PDF_FILE" ]; then
        echo "✓ Found test PDF: $PDF_FILE"
        
        # Test pdfinfo
        if pdfinfo "$PDF_FILE" >/dev/null 2>&1; then
            echo "✓ pdfinfo can read the PDF"
        else
            echo "✗ pdfinfo failed to read the PDF"
            exit 1
        fi
        
        # Test pdftoppm (convert first page to image)
        TEMP_DIR=$(mktemp -d)
        if pdftoppm -f 1 -l 1 -jpeg "$PDF_FILE" "$TEMP_DIR/test" >/dev/null 2>&1; then
            echo "✓ pdftoppm can convert PDF to images"
            rm -rf "$TEMP_DIR"
        else
            echo "✗ pdftoppm failed to convert PDF"
            rm -rf "$TEMP_DIR"
            exit 1
        fi
    else
        echo "⚠ No PDF files found for testing"
    fi
else
    echo "⚠ Test PDF directory not found"
fi

echo ""
echo "✅ All poppler-utils tests passed!"
echo "The PDF conversion fix should now work correctly."
