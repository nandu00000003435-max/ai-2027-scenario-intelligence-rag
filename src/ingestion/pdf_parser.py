"""
PDF parsing and structured extraction for AI 2027 document
"""
import re
import json
from pathlib import Path
from typing import Dict, List, Optional
import fitz  # PyMuPDF

from src.config import AI_2027_PDF_PATH, PROCESSED_DATA_DIR, APPENDICES


class AI2027Parser:
    """Parse AI 2027 PDF into structured timeline events and appendices"""
    
    def __init__(self, pdf_path: Path = AI_2027_PDF_PATH):
        self.pdf_path = pdf_path
        if not pdf_path.exists():
            raise FileNotFoundError(
                f"PDF not found at {pdf_path}. "
                f"Please download it using: python scripts/download_pdf.py"
            )
        self.doc = fitz.open(pdf_path)
    
    def parse_full_document(self) -> Dict:
        """Parse entire document into structured format"""
        print(f"📄 Parsing {self.pdf_path.name}...")
        
        timeline_events = self.extract_timeline_events()
        appendices = self.extract_appendices()
        chunks = self.create_chunks()
        
        result = {
            "timeline_events": timeline_events,
            "appendices": appendices,
            "chunks": chunks,
            "metadata": {
                "total_pages": len(self.doc),
                "total_events": len(timeline_events),
                "total_appendices": len(appendices),
                "total_chunks": len(chunks)
            }
        }
        
        # Save to processed directory
        self._save_processed_data(result)
        
        print(f"✅ Parsed {len(timeline_events)} events, {len(appendices)} appendices, {len(chunks)} chunks")
        return result
    
    def extract_timeline_events(self) -> List[Dict]:
        """Extract timeline events with branch classification"""
        events = []
        
        # Timeline sections (pages 3-43)
        timeline_sections = [
            {"date": "Mid 2025", "title": "Stumbling Agents", "page": 3, "branch": "shared"},
            {"date": "Late 2025", "title": "The World's Most Expensive AI", "page": 3, "branch": "shared"},
            {"date": "Early 2026", "title": "Coding Automation", "page": 5, "branch": "shared"},
            {"date": "Mid 2026", "title": "China Wakes Up", "page": 5, "branch": "shared"},
            {"date": "Late 2026", "title": "AI Takes Some Jobs", "page": 7, "branch": "shared"},
            {"date": "January 2027", "title": "Agent-2 Never Finishes Learning", "page": 7, "branch": "shared"},
            {"date": "February 2027", "title": "China Steals Agent-2", "page": 8, "branch": "shared"},
            {"date": "March 2027", "title": "Algorithmic Breakthroughs", "page": 10, "branch": "shared"},
            {"date": "April 2027", "title": "Alignment for Agent-3", "page": 11, "branch": "shared"},
            {"date": "May 2027", "title": "National Security", "page": 12, "branch": "shared"},
            {"date": "June 2027", "title": "Self-improving AI", "page": 13, "branch": "shared"},
            {"date": "July 2027", "title": "The Cheap Remote Worker", "page": 14, "branch": "shared"},
            {"date": "August 2027", "title": "The Geopolitics of Superintelligence", "page": 16, "branch": "shared"},
            {"date": "September 2027", "title": "Agent-4, the Superhuman AI Researcher", "page": 17, "branch": "shared"},
            {"date": "October 2027", "title": "Government Oversight", "page": 20, "branch": "shared"},
            
            # Race ending (pages 23-30)
            {"date": "October 2027", "title": "Race ending - Committee continues Agent-4", "page": 23, "branch": "race"},
            {"date": "November 2027", "title": "Superhuman Politicking", "page": 23, "branch": "race"},
            {"date": "December 2027", "title": "The Agent-5 Collective", "page": 25, "branch": "race"},
            {"date": "2028", "title": "The AI Economy", "page": 26, "branch": "race"},
            {"date": "2029", "title": "The Deal", "page": 27, "branch": "race"},
            {"date": "2030", "title": "Takeover", "page": 29, "branch": "race"},
            
            # Slowdown ending (pages 31-43)
            {"date": "October 2027", "title": "Slowdown ending - Committee slows down", "page": 31, "branch": "slowdown"},
            {"date": "November 2027", "title": "Tempted by Power", "page": 31, "branch": "slowdown"},
            {"date": "December 2027", "title": "A US-China Deal?", "page": 33, "branch": "slowdown"},
            {"date": "January 2028", "title": "A Safer Strategy", "page": 33, "branch": "slowdown"},
            {"date": "February 2028", "title": "Superhuman Capabilities, Superhuman Advice", "page": 34, "branch": "slowdown"},
            {"date": "March 2028", "title": "Election Prep", "page": 36, "branch": "slowdown"},
            {"date": "April 2028", "title": "Safer-4", "page": 37, "branch": "slowdown"},
            {"date": "May 2028", "title": "Superhuman AI Released", "page": 37, "branch": "slowdown"},
            {"date": "June 2028", "title": "AI Alignment in China", "page": 38, "branch": "slowdown"},
            {"date": "July 2028", "title": "The Deal", "page": 39, "branch": "slowdown"},
            {"date": "August 2028", "title": "Treaty Verification", "page": 40, "branch": "slowdown"},
            {"date": "September 2028", "title": "Who Controls the AIs?", "page": 40, "branch": "slowdown"},
            {"date": "October 2028", "title": "The AI Economy", "page": 41, "branch": "slowdown"},
            {"date": "November 2028", "title": "Election", "page": 41, "branch": "slowdown"},
            {"date": "2029", "title": "Transformation", "page": 41, "branch": "slowdown"},
            {"date": "2030", "title": "Peaceful Protests", "page": 42, "branch": "slowdown"},
        ]
        
        for section in timeline_sections:
            page = self.doc[section["page"] - 1]  # 0-indexed
            text = page.get_text()
            
            event = {
                "id": self._create_event_id(section["date"], section["title"]),
                "date": section["date"],
                "title": section["title"],
                "branch": section["branch"],
                "page": section["page"],
                "content": text,
                "summary": self._extract_first_paragraph(text)
            }
            events.append(event)
        
        return events
    
    def extract_appendices(self) -> List[Dict]:
        """Extract appendices (pages 44-71)"""
        appendices_list = []
        
        for appendix_id, info in APPENDICES.items():
            # Find appendix content (simplified - in production, use better parsing)
            page_num = info["page_start"]
            if page_num <= len(self.doc):
                page = self.doc[page_num - 1]
                text = page.get_text()
                
                appendix = {
                    "id": appendix_id,
                    "title": info["title"],
                    "page": page_num,
                    "content": text,
                    "summary": self._extract_first_paragraph(text)
                }
                appendices_list.append(appendix)
        
        return appendices_list
    
    def create_chunks(self, chunk_size: int = 512, overlap: int = 128) -> List[Dict]:
        """Create text chunks with metadata for vector store"""
        chunks = []
        chunk_id = 0
        
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            text = page.get_text()
            
            # Classify branch
            branch = self._classify_branch(page_num + 1, text)
            
            # Split into chunks
            words = text.split()
            for i in range(0, len(words), chunk_size - overlap):
                chunk_text = " ".join(words[i:i + chunk_size])
                
                if len(chunk_text.strip()) < 50:  # Skip tiny chunks
                    continue
                
                chunk = {
                    "id": f"chunk_{chunk_id}",
                    "text": chunk_text,
                    "page": page_num + 1,
                    "branch": branch,
                    "chunk_index": i // (chunk_size - overlap),
                    "metadata": {
                        "source": "ai-2027.pdf",
                        "url": "https://www.genspark.ai/api/files/s/7G4S0Nj3"
                    }
                }
                chunks.append(chunk)
                chunk_id += 1
        
        return chunks
    
    def _classify_branch(self, page_num: int, text: str) -> str:
        """Classify which timeline branch a page belongs to"""
        # Pages 1-22: Shared timeline
        if page_num <= 22:
            return "shared"
        
        # Page 23-30: Race ending
        if 23 <= page_num <= 30:
            return "race"
        
        # Page 31-43: Slowdown ending
        if 31 <= page_num <= 43:
            return "slowdown"
        
        # Page 44+: Appendices
        if page_num >= 44:
            return "appendix"
        
        return "unknown"
    
    def _create_event_id(self, date: str, title: str) -> str:
        """Create unique event ID"""
        # Convert "Mid 2025" -> "mid_2025"
        date_slug = date.lower().replace(" ", "_")
        title_slug = re.sub(r'[^a-z0-9]+', '_', title.lower()).strip('_')
        return f"{date_slug}_{title_slug}"
    
    def _extract_first_paragraph(self, text: str) -> str:
        """Extract first paragraph as summary"""
        paragraphs = text.split('\n\n')
        for para in paragraphs:
            if len(para.strip()) > 50:
                return para.strip()[:500]  # Max 500 chars
        return text[:500]
    
    def _save_processed_data(self, data: Dict):
        """Save processed data to JSON files"""
        # Save timeline events
        with open(PROCESSED_DATA_DIR / "timeline_events.json", "w") as f:
            json.dump(data["timeline_events"], f, indent=2)
        
        # Save appendices
        with open(PROCESSED_DATA_DIR / "appendices.json", "w") as f:
            json.dump(data["appendices"], f, indent=2)
        
        # Save chunks
        with open(PROCESSED_DATA_DIR / "chunks.json", "w") as f:
            json.dump(data["chunks"], f, indent=2)
        
        print(f"💾 Saved processed data to {PROCESSED_DATA_DIR}")


if __name__ == "__main__":
    parser = AI2027Parser()
    result = parser.parse_full_document()
    print(f"\n📊 Summary:")
    print(f"  - Timeline events: {result['metadata']['total_events']}")
    print(f"  - Appendices: {result['metadata']['total_appendices']}")
    print(f"  - Text chunks: {result['metadata']['total_chunks']}")
