"""
Download AI 2027 PDF from source
"""
import requests
from pathlib import Path
from src.config import AI_2027_PDF_PATH, AI_2027_URL


def download_pdf():
    """Download AI 2027 PDF if not already present"""
    if AI_2027_PDF_PATH.exists():
        print(f"✅ PDF already exists at {AI_2027_PDF_PATH}")
        return
    
    print(f"📥 Downloading AI 2027 PDF from {AI_2027_URL}...")
    
    try:
        response = requests.get(AI_2027_URL, stream=True, timeout=30)
        response.raise_for_status()
        
        # Save to file
        AI_2027_PDF_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(AI_2027_PDF_PATH, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✅ Downloaded successfully to {AI_2027_PDF_PATH}")
        print(f"📊 File size: {AI_2027_PDF_PATH.stat().st_size / 1024 / 1024:.2f} MB")
    
    except Exception as e:
        print(f"❌ Download failed: {e}")
        print(f"\n💡 Manual download:")
        print(f"   1. Visit: {AI_2027_URL}")
        print(f"   2. Save as: {AI_2027_PDF_PATH}")


if __name__ == "__main__":
    download_pdf()
