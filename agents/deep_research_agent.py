import json
from pathlib import Path
from typing import Dict
from llm.gemini_llm import GeminiLLM


class DeepResearchAgent:
    """Agent responsible for competitor research and analysis."""
    
    def __init__(self, llm: GeminiLLM):
        self.llm = llm
        self.output_dir = Path(__file__).parent.parent / "pipeline_outputs"
        self.output_dir.mkdir(exist_ok=True)
    
    def execute(self, user_context: Dict) -> Path:
        """
        Execute competitor research and generate report.
        
        Args:
            user_context: User_Business_Context JSON object
            
        Returns:
            Path to competitor_analysis_report.md
        """
        print("[Deep_Research_Agent] Starting competitor research...")
        
        # Build research prompt
        research_prompt = f"""You are a market research expert. Your task is to find and analyze competitors for a new business.

BUSINESS CONTEXT:
- Problem: {user_context.get('problem', 'N/A')}
- Target Users: {user_context.get('target_users', 'N/A')}
- Value Proposition: {user_context.get('value_proposition', 'N/A')}
- Offer: {user_context.get('offer', 'N/A')}
- Industry: {user_context.get('industry', 'N/A')}

TASK:
Based on the business context above, identify the TOP 10 competitors in this space. For each competitor, provide:

1. Company Name
2. Tagline / Value Proposition
3. Key Features (list 3-5 main features)
4. Pricing Model (if visible/known)
5. Brand Tone (describe their communication style: friendly, professional, technical, etc.)
6. Design Style (describe their visual style: modern, minimalist, bold, etc.)

IMPORTANT:
- Be realistic and research actual competitors that exist in this market
- If you don't know specific details, make reasonable inferences based on the business type
- Focus on direct competitors (solving similar problems for similar audiences)
- Format your response as a structured markdown report

OUTPUT FORMAT:
Create a markdown report with the following structure:

# Competitor Analysis Report

## Overview
[Brief overview of the competitive landscape]

## Top 10 Competitors

### 1. [Competitor Name]
- **Tagline/Value Proposition:** [Their tagline]
- **Key Features:**
  - Feature 1
  - Feature 2
  - Feature 3
- **Pricing Model:** [Pricing information]
- **Brand Tone:** [Description]
- **Design Style:** [Description]

[Repeat for all 10 competitors]

## Competitive Landscape Summary
[Summary of common patterns, gaps, and opportunities]
"""
        
        # Get research results from LLM
        print("[Deep_Research_Agent] Querying LLM for competitor analysis...")
        try:
            research_results = self.llm.call(research_prompt)
            
            # Validate response
            if not research_results or len(research_results.strip()) < 50:
                raise ValueError(f"LLM returned insufficient content: {len(research_results) if research_results else 0} characters")
            
            print(f"[Deep_Research_Agent] Received {len(research_results)} characters from LLM")
            
            # Save to markdown file
            output_file = self.output_dir / "competitor_analysis_report.md"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(research_results)
            
            # Verify file was created
            if output_file.exists() and output_file.stat().st_size > 0:
                print(f"[Deep_Research_Agent] ✅ Report saved successfully to {output_file}")
                print(f"[Deep_Research_Agent] File size: {output_file.stat().st_size} bytes")
                return output_file
            else:
                raise FileNotFoundError(f"Failed to create report file at {output_file}")
                
        except Exception as e:
            print(f"[Deep_Research_Agent] ❌ ERROR during execution: {e}")
            import traceback
            traceback.print_exc()
            raise
