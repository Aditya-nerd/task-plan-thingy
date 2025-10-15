import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

load_dotenv()


class LLMService:
    """Service for interacting with Language Learning Models."""
    
    def __init__(self):
        self.provider = os.getenv("DEFAULT_LLM_PROVIDER", "openai")
        self.openai_client = None
        self.anthropic_client = None
        self.gemini_configured = False
        
        if self.provider == "openai" and OPENAI_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key and self._is_valid_api_key(api_key, "openai"):
                self.openai_client = openai.OpenAI(api_key=api_key)
                self.openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        
        if self.provider == "anthropic" and ANTHROPIC_AVAILABLE:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key and self._is_valid_api_key(api_key, "anthropic"):
                self.anthropic_client = anthropic.Anthropic(api_key=api_key)
                self.anthropic_model = os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")
        
        if self.provider == "gemini" and GEMINI_AVAILABLE:
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key and self._is_valid_api_key(api_key, "gemini"):
                genai.configure(api_key=api_key)
                self.gemini_configured = True
                self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-pro")
    
    def _is_valid_api_key(self, api_key: str, provider: str) -> bool:
        """Check if an API key looks valid (basic format validation)."""
        if not api_key or api_key.startswith("your_") or api_key == "":
            return False
        
        # Basic format validation
        if provider == "openai":
            return api_key.startswith("sk-") and len(api_key) > 20
        elif provider == "anthropic":
            return api_key.startswith("sk-ant-") and len(api_key) > 20
        elif provider == "gemini":
            return len(api_key) > 20  # Gemini keys don't have a specific prefix
        
        return False

    async def generate_task_breakdown(self, goal: str) -> Dict[str, Any]:
        """
        Generate a task breakdown for a given goal using LLM.
        
        Args:
            goal: The goal description to break down
            
        Returns:
            Dict containing the task plan structure
        """
        prompt = self._create_task_breakdown_prompt(goal)
        
        if self.provider == "openai" and OPENAI_AVAILABLE and self.openai_client:
            return await self._generate_with_openai(prompt)
        elif self.provider == "anthropic" and ANTHROPIC_AVAILABLE and self.anthropic_client:
            return await self._generate_with_anthropic(prompt)
        elif self.provider == "gemini" and GEMINI_AVAILABLE and self.gemini_configured:
            return await self._generate_with_gemini(prompt)
        else:
            # Fallback to mock response if no LLM is available
            print(f"Using mock response for goal: {goal} (No valid API key found)")
            return self._create_mock_response(goal)

    # Backwards-compatible alias
    async def generate_plan_breakdown(self, goal: str) -> Dict[str, Any]:
        """Alias for generate_task_breakdown to support refactored callers."""
        return await self.generate_task_breakdown(goal)
    
    def _create_task_breakdown_prompt(self, goal: str) -> str:
        """Create a structured prompt for task breakdown."""
        return f"""
Break down this goal into actionable tasks with suggested deadlines and dependencies.

Goal: {goal}

Please provide a response in the following JSON format:
{{
    "title": "Short title for the project",
    "description": "Brief description of the project plan",
    "estimated_duration_days": 14,
    "tasks": [
        {{
            "title": "Task title",
            "description": "Detailed description of what needs to be done, including specific deliverables and outcomes",
            "estimated_hours": 8.0,
            "priority": "high|medium|low|critical",
            "dependencies": [],
            "deadline_days_from_start": 3,
            "category": "research|design|development|testing|marketing|deployment|planning",
            "skills_required": ["skill1", "skill2"],
            "deliverables": ["deliverable1", "deliverable2"]
        }}
    ]
}}

Guidelines:
- Break the goal into 5-10 specific, actionable tasks
- Estimate realistic time requirements in hours (0.5 to 40 hours per task)
- Set priorities (critical, high, medium, low) based on importance and dependencies
- Include dependencies as task indices (e.g., [0, 1] means this task depends on tasks 0 and 1)
- Set deadlines as days from project start
- Ensure tasks are specific and measurable with clear deliverables
- Categorize tasks appropriately (research, design, development, etc.)
- List required skills for each task
- Define concrete deliverables for each task
- Consider logical sequencing and parallelization opportunities

Respond with only the JSON object, no additional text.
"""
    
    async def _generate_with_openai(self, prompt: str) -> Dict[str, Any]:
        """Generate response using OpenAI API."""
        try:
            response = self.openai_client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "You are an expert project manager who excels at breaking down complex goals into actionable tasks with realistic timelines."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            print(f"Error with OpenAI API: {e}")
            return self._create_mock_response(prompt.split("Goal: ")[1].split("\n")[0])
    
    async def _generate_with_anthropic(self, prompt: str) -> Dict[str, Any]:
        """Generate response using Anthropic API."""
        try:
            response = self.anthropic_client.messages.create(
                model=self.anthropic_model,
                max_tokens=2000,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = response.content[0].text
            return json.loads(content)
            
        except Exception as e:
            print(f"Error with Anthropic API: {e}")
            return self._create_mock_response(prompt.split("Goal: ")[1].split("\n")[0])
    
    async def _generate_with_gemini(self, prompt: str) -> Dict[str, Any]:
        """Generate response using Google Gemini API."""
        try:
            model = genai.GenerativeModel(self.gemini_model)
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=2000,
                )
            )
            
            content = response.text
            return json.loads(content)
            
        except Exception as e:
            print(f"Error with Gemini API: {e}")
            return self._create_mock_response(prompt.split("Goal: ")[1].split("\n")[0])
    
    def _create_mock_response(self, goal: str) -> Dict[str, Any]:
        """Create a mock response when LLM is not available."""
        return {
            "title": f"Plan for: {goal[:50]}...",
            "description": f"A structured plan to achieve: {goal}",
            "estimated_duration_days": 14,
            "tasks": [
                {
                    "title": "Research and Planning",
                    "description": "Conduct thorough research and create detailed project plan with clear objectives and scope",
                    "estimated_hours": 8.0,
                    "priority": "high",
                    "dependencies": [],
                    "deadline_days_from_start": 2,
                    "category": "research",
                    "skills_required": ["research", "planning", "analysis"],
                    "deliverables": ["project plan", "research report", "requirements document"]
                },
                {
                    "title": "Setup and Preparation",
                    "description": "Set up necessary tools, development environment, and gather resources",
                    "estimated_hours": 4.0,
                    "priority": "high",
                    "dependencies": [0],
                    "deadline_days_from_start": 3,
                    "category": "planning",
                    "skills_required": ["technical setup", "tool configuration"],
                    "deliverables": ["configured environment", "resource list", "setup documentation"]
                },
                {
                    "title": "Core Implementation",
                    "description": "Implement the main components, features, and core functionality",
                    "estimated_hours": 24.0,
                    "priority": "high",
                    "dependencies": [1],
                    "deadline_days_from_start": 10,
                    "category": "development",
                    "skills_required": ["programming", "system design", "problem solving"],
                    "deliverables": ["working prototype", "core features", "technical documentation"]
                },
                {
                    "title": "Testing and Quality Assurance",
                    "description": "Test all components thoroughly and ensure quality standards are met",
                    "estimated_hours": 8.0,
                    "priority": "medium",
                    "dependencies": [2],
                    "deadline_days_from_start": 12,
                    "category": "testing",
                    "skills_required": ["testing", "debugging", "quality assurance"],
                    "deliverables": ["test reports", "bug fixes", "quality documentation"]
                },
                {
                    "title": "Final Review and Deployment",
                    "description": "Final review, documentation, and deployment to production environment",
                    "estimated_hours": 4.0,
                    "priority": "medium",
                    "dependencies": [3],
                    "deadline_days_from_start": 14,
                    "category": "deployment",
                    "skills_required": ["deployment", "documentation", "project management"],
                    "deliverables": ["deployed solution", "user documentation", "maintenance guide"]
                }
            ]
        }