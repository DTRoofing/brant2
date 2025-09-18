from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Create a simple test PDF
c = canvas.Canvas("test_roofing.pdf", pagesize=letter)
c.drawString(100, 750, "Test Roofing Document")
c.drawString(100, 700, "Roof Area: 2500 sq ft")
c.drawString(100, 650, "Material: Asphalt Shingles")
c.drawString(100, 600, "Estimated Cost: $15,000")
c.save()

print("Test PDF created: test_roofing.pdf")