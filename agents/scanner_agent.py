import os
from typing import Dict, List, Optional
from llm.gemini_llm import GeminiLLM

try:
    from serper import SerperDevTool
    SERPER_AVAILABLE = True
except ImportError:
    SERPER_AVAILABLE = False
    SerperDevTool = None


class ScannerAgent:
    """Agent responsible for scanning the market for competitors."""
    
    def __init__(self, llm: GeminiLLM):
        self.llm = llm
        if not SERPER_AVAILABLE:
            print("[ScannerAgent] WARNING: SerperDevTool not available. Install with: pip install serper")
    
    def scan_market(self, industry: str, keywords: str, problem: str) -> Dict:
        """
        Scan the market for competitors.
        
        Args:
            industry: The industry/niche
            keywords: 3 keywords for searching
            problem: The problem being solved
            
        Returns:
            Dictionary with competitors list and top competitor info
        """
        print(f"[ScannerAgent] Scanning market for: {industry}")
        print(f"[ScannerAgent] Keywords: {keywords}")
        
        # If Serper is not available, use LLM to generate realistic competitors
        if not SERPER_AVAILABLE or not os.getenv("SERPER_API_KEY"):
            print("[ScannerAgent] Using LLM fallback for competitor research")
            return self._llm_fallback_scan(industry, keywords, problem)
        
        try:
            # Use SerperDevTool to search
            serper = SerperDevTool()
            
            # Build search query
            search_query = f"{industry} {keywords} {problem}"
            print(f"[ScannerAgent] Search query: {search_query}")
            
            # Search for competitors
            results = serper.search(search_query)
            
            # Extract competitors from search results
            competitors_raw = []
            if results and "organic" in results:
                for item in results["organic"][:5]:
                    competitors_raw.append({
                        "name": item.get("title", "Unknown"),
                        "url": item.get("link", ""),
                        "snippet": item.get("snippet", "")
                    })
            
            # Use LLM to analyze strengths and weaknesses from search results
            if competitors_raw:
                analysis_prompt = f"""You are a market research expert. Analyze these competitors in {industry}:

{chr(10).join([f"- {c['name']} ({c.get('url', 'N/A')}): {c.get('snippet', '')}" for c in competitors_raw])}

For EACH competitor, identify:
1. **Main Strength** - What they are good at (e.g., 'Low Price', 'Huge Community', 'Fast Delivery')
2. **Main Weakness** - What users complain about or what they lack (e.g., 'Buggy App', 'Slow Support', 'Expensive')

Provide a JSON response with this EXACT structure:
{{
  "competitors": [
    {{ "name": "{competitors_raw[0]['name']}", "url": "{competitors_raw[0].get('url', '')}", "strength": "...", "weakness": "..." }},
    {{ "name": "{competitors_raw[1]['name'] if len(competitors_raw) > 1 else 'Competitor 2'}", "url": "{competitors_raw[1].get('url', '') if len(competitors_raw) > 1 else ''}", "strength": "...", "weakness": "..." }},
    {{ "name": "{competitors_raw[2]['name'] if len(competitors_raw) > 2 else 'Competitor 3'}", "url": "{competitors_raw[2].get('url', '') if len(competitors_raw) > 2 else ''}", "strength": "...", "weakness": "..." }},
    {{ "name": "{competitors_raw[3]['name'] if len(competitors_raw) > 3 else 'Competitor 4'}", "url": "{competitors_raw[3].get('url', '') if len(competitors_raw) > 3 else ''}", "strength": "...", "weakness": "..." }},
    {{ "name": "{competitors_raw[4]['name'] if len(competitors_raw) > 4 else 'Competitor 5'}", "url": "{competitors_raw[4].get('url', '') if len(competitors_raw) > 4 else ''}", "strength": "...", "weakness": "..." }}
  ],
  "top_competitor": {{
    "name": "{competitors_raw[0]['name']}"
  }}
}}

IMPORTANT: Include the URL from the search results for each competitor. If URL is not available, use an empty string.

Return ONLY valid JSON, no markdown formatting."""
                
                try:
                    analysis_response = self.llm.call(analysis_prompt)
                    import json
                    analysis_response = analysis_response.strip()
                    if "```json" in analysis_response:
                        analysis_response = analysis_response.split("```json")[1].split("```")[0].strip()
                    elif "```" in analysis_response:
                        analysis_response = analysis_response.split("```")[1].split("```")[0].strip()
                    
                    result = json.loads(analysis_response)
                    
                    # Ensure structure and merge URLs from search results
                    if "competitors" not in result:
                        result["competitors"] = []
                    if "top_competitor" not in result:
                        result["top_competitor"] = {"name": competitors_raw[0]["name"] if competitors_raw else "Market Leader"}
                    
                    # Merge URLs from search results (in case LLM didn't include them)
                    for i, comp in enumerate(result.get("competitors", [])):
                        if i < len(competitors_raw) and isinstance(comp, dict):
                            if not comp.get("url") and competitors_raw[i].get("url"):
                                comp["url"] = competitors_raw[i]["url"]
                    
                    return result
                except Exception as e:
                    print(f"[ScannerAgent] Error analyzing competitors: {e}")
                    # Fallback to LLM-only scan
                    return self._llm_fallback_scan(industry, keywords, problem)
            
            # No competitors found, use LLM fallback
            return self._llm_fallback_scan(industry, keywords, problem)
            
        except Exception as e:
            print(f"[ScannerAgent] Error with Serper: {e}")
            return self._llm_fallback_scan(industry, keywords, problem)
    
    def _llm_fallback_scan(self, industry: str, keywords: str, problem: str) -> Dict:
        """Fallback to LLM for competitor research if Serper is unavailable."""
        prompt = f"""You are a market research expert. Search for the top 5 competitors in {industry} related to {keywords}.

For EACH competitor, identify:
1. **Name** - The company/product name
2. **Website URL** - Extract the main website URL (e.g., https://example.com). If you cannot find a real URL, use an empty string.
3. **Main Strength** - What they are good at (e.g., 'Low Price', 'Huge Community', 'Fast Delivery', 'Premium Quality')
4. **Main Weakness** - What users complain about or what they lack (e.g., 'Buggy App', 'Slow Support', 'Expensive', 'Limited Features')

Based on the problem: {problem}

Provide a JSON response with this EXACT structure:
{{
  "competitors": [
    {{ "name": "Competitor 1 Name", "url": "https://competitor1.com", "strength": "Their main strength", "weakness": "Their main weakness" }},
    {{ "name": "Competitor 2 Name", "url": "https://competitor2.com", "strength": "Their main strength", "weakness": "Their main weakness" }},
    {{ "name": "Competitor 3 Name", "url": "https://competitor3.com", "strength": "Their main strength", "weakness": "Their main weakness" }},
    {{ "name": "Competitor 4 Name", "url": "https://competitor4.com", "strength": "Their main strength", "weakness": "Their main weakness" }},
    {{ "name": "Competitor 5 Name", "url": "https://competitor5.com", "strength": "Their main strength", "weakness": "Their main weakness" }}
  ],
  "top_competitor": {{
    "name": "Competitor 1 Name"
  }}
}}

IMPORTANT:
- Be realistic and research actual competitors that exist in this market
- Include real website URLs if you can identify them, otherwise use empty strings
- Strengths should be what makes them successful or popular
- Weaknesses should be real pain points users experience
- Focus on direct competitors solving similar problems

Return ONLY valid JSON, no markdown formatting."""
        
        try:
            response = self.llm.call(prompt)
            
            # Clean and parse JSON
            import json
            response = response.strip()
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            result = json.loads(response)
            
            # Ensure structure
            if "competitors" not in result:
                result["competitors"] = []
            if "top_competitor" not in result:
                result["top_competitor"] = {"name": "Market Leader"}
            
            # Validate competitor structure - ensure each has name, url, strength, weakness
            validated_competitors = []
            for comp in result.get("competitors", []):
                if isinstance(comp, dict):
                    validated_competitors.append({
                        "name": comp.get("name", "Unknown Competitor"),
                        "url": comp.get("url", ""),  # URL may be empty
                        "strength": comp.get("strength", "Market presence"),
                        "weakness": comp.get("weakness", "Unknown weaknesses")
                    })
                elif isinstance(comp, str):
                    # Legacy format - convert to new format
                    validated_competitors.append({
                        "name": comp,
                        "url": "",
                        "strength": "Established in market",
                        "weakness": "Unknown weaknesses"
                    })
            
            result["competitors"] = validated_competitors
            
            return result
            
        except Exception as e:
            print(f"[ScannerAgent] LLM fallback error: {e}")
            # Return default structure with strengths/weaknesses and URLs
            return {
                "competitors": [
                    {"name": "Competitor 1", "url": "", "strength": "Market presence", "weakness": "Unknown weaknesses"},
                    {"name": "Competitor 2", "url": "", "strength": "Market presence", "weakness": "Unknown weaknesses"},
                    {"name": "Competitor 3", "url": "", "strength": "Market presence", "weakness": "Unknown weaknesses"},
                    {"name": "Competitor 4", "url": "", "strength": "Market presence", "weakness": "Unknown weaknesses"},
                    {"name": "Competitor 5", "url": "", "strength": "Market presence", "weakness": "Unknown weaknesses"}
                ],
                "top_competitor": {
                    "name": "Market Leader"
                }
            }
