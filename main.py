from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
import os
from dotenv import load_dotenv

from app.database import get_db, engine, Base
from app.models import TaskPlan, Task
from app.schemas import GoalInput, TaskPlanResponse, TaskPlanCreate
from app.services.task_planner import TaskPlannerService
from app.services.llm_service import LLMService

# Load environment variables
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Smart Task Planner",
    description="AI-powered task planner that breaks down goals into actionable tasks with timelines",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
llm_service = LLMService()
task_planner_service = TaskPlannerService(llm_service)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Smart Task Planner API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.post("/plan", response_model=TaskPlanResponse)
async def create_task_plan(
    goal_input: GoalInput,
    db: Session = Depends(get_db)
):
    """
    Create a task plan from a goal description.
    
    Args:
        goal_input: The goal description and optional parameters
        db: Database session
        
    Returns:
        TaskPlanResponse: The generated task plan with tasks and dependencies
    """
    try:
        # Generate task plan using AI
        plan_data = await task_planner_service.create_plan(goal_input.goal)
        
        # Save to database
        db_plan = TaskPlan(
            goal=goal_input.goal,
            title=plan_data["title"],
            description=plan_data["description"],
            estimated_duration_days=plan_data["estimated_duration_days"]
        )
        db.add(db_plan)
        db.commit()
        db.refresh(db_plan)
        
        # Save tasks
        tasks = []
        for task_data in plan_data["tasks"]:
            db_task = Task(
                plan_id=db_plan.id,
                title=task_data["title"],
                description=task_data["description"],
                estimated_hours=task_data["estimated_hours"],
                priority=task_data["priority"],
                dependencies=task_data["dependencies"],
                deadline_days_from_start=task_data["deadline_days_from_start"],
                category=task_data.get("category"),
                skills_required=task_data.get("skills_required", []),
                deliverables=task_data.get("deliverables", [])
            )
            db.add(db_task)
            tasks.append(db_task)
        
        db.commit()
        
        return TaskPlanResponse(
            id=db_plan.id,
            goal=db_plan.goal,
            title=db_plan.title,
            description=db_plan.description,
            estimated_duration_days=db_plan.estimated_duration_days,
            tasks=[
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "estimated_hours": task.estimated_hours,
                    "priority": task.priority,
                    "dependencies": task.dependencies,
                    "deadline_days_from_start": task.deadline_days_from_start,
                    "status": task.status,
                    "category": task.category,
                    "skills_required": task.skills_required,
                    "deliverables": task.deliverables
                }
                for task in tasks
            ],
            created_at=db_plan.created_at
        )
        
    except Exception as e:
        # Log the error for debugging
        print(f"Error creating task plan: {str(e)}")
        
        # Check if it's an API key error
        if "API key" in str(e) or "invalid_request_error" in str(e):
            # For API key errors, still try to return a mock response
            try:
                llm_service = LLMService()
                plan_data = await llm_service.generate_task_breakdown(goal_input.goal)
                
                # Create plan in database
                db_plan = TaskPlan(
                    goal=goal_input.goal,
                    title=plan_data["title"],
                    description=plan_data["description"],
                    estimated_duration_days=plan_data["estimated_duration_days"]
                )
                db.add(db_plan)
                db.flush()
                
                # Save tasks
                tasks = []
                for task_data in plan_data["tasks"]:
                    db_task = Task(
                        plan_id=db_plan.id,
                        title=task_data["title"],
                        description=task_data["description"],
                        estimated_hours=task_data["estimated_hours"],
                        priority=task_data["priority"],
                        dependencies=task_data["dependencies"],
                        deadline_days_from_start=task_data["deadline_days_from_start"],
                        category=task_data.get("category"),
                        skills_required=task_data.get("skills_required", []),
                        deliverables=task_data.get("deliverables", [])
                    )
                    db.add(db_task)
                    tasks.append(db_task)
                
                db.commit()
                
                return TaskPlanResponse(
                    id=db_plan.id,
                    goal=db_plan.goal,
                    title=db_plan.title,
                    description=db_plan.description,
                    estimated_duration_days=db_plan.estimated_duration_days,
                    tasks=[
                        {
                            "id": task.id,
                            "title": task.title,
                            "description": task.description,
                            "estimated_hours": task.estimated_hours,
                            "priority": task.priority,
                            "dependencies": task.dependencies,
                            "deadline_days_from_start": task.deadline_days_from_start,
                            "status": task.status,
                            "category": task.category,
                            "skills_required": task.skills_required,
                            "deliverables": task.deliverables
                        }
                        for task in tasks
                    ],
                    created_at=db_plan.created_at
                )
            except Exception as fallback_error:
                print(f"Fallback also failed: {str(fallback_error)}")
                raise HTTPException(status_code=500, detail="Task planning service temporarily unavailable. Please check your API configuration or try again later.")
        else:
            raise HTTPException(status_code=500, detail=f"Failed to create task plan: {str(e)}")


@app.get("/plans/{plan_id}", response_model=TaskPlanResponse)
async def get_task_plan(plan_id: int, db: Session = Depends(get_db)):
    """Get a specific task plan by ID."""
    plan = db.query(TaskPlan).filter(TaskPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Task plan not found")
    
    tasks = db.query(Task).filter(Task.plan_id == plan_id).all()
    
    return TaskPlanResponse(
        id=plan.id,
        goal=plan.goal,
        title=plan.title,
        description=plan.description,
        estimated_duration_days=plan.estimated_duration_days,
        tasks=[
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "estimated_hours": task.estimated_hours,
                "priority": task.priority,
                "dependencies": task.dependencies,
                "deadline_days_from_start": task.deadline_days_from_start,
                "status": task.status,
                "category": task.category,
                "skills_required": task.skills_required,
                "deliverables": task.deliverables
            }
            for task in tasks
        ],
        created_at=plan.created_at
    )


@app.get("/plans")
async def list_task_plans(db: Session = Depends(get_db)):
    """List all task plans."""
    plans = db.query(TaskPlan).all()
    return [
        {
            "id": plan.id,
            "goal": plan.goal,
            "title": plan.title,
            "estimated_duration_days": plan.estimated_duration_days,
            "created_at": plan.created_at
        }
        for plan in plans
    ]


@app.put("/tasks/{task_id}/status")
async def update_task_status(
    task_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    """Update task status."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if status not in ["pending", "in_progress", "completed"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    task.status = status
    db.commit()
    
    return {"message": "Task status updated", "task_id": task_id, "status": status}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST", "localhost"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=os.getenv("DEBUG", "False").lower() == "true"
    )