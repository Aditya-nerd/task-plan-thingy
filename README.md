# 🎯 Smart Task Planner

An AI-powered task planner that breaks down user goals into actionable tasks with timelines and dependencies using Large Language Models (LLMs).

## ✨ Features

- **Multi-LLM Support**: OpenAI GPT, Anthropic Claude, and Google Gemini integration
- **Smart Dependencies**: Automatically identifies and manages task dependencies
- **Timeline Estimation**: AI-powered realistic time estimates and deadlines  
- **Priority Management**: Intelligent task prioritization based on dependencies
- **RESTful API**: Clean, documented API for integration with other applications
- **Database Storage**: Persistent SQLite storage with SQLAlchemy ORM
- **Modern Frontend**: Beautiful, responsive interface with animations and particles
- **Critical Path Analysis**: Identifies the critical path through your project tasks
- **Virtual Environment**: Isolated Python environment with automated setup scripts
- **Secure Configuration**: Safe API key management with environment variables

## 🔐 Security & API Keys

**IMPORTANT**: Never share your API keys or commit them to version control!

1. **Copy the example environment file**:
   ```bash
   cp .env.example .env
   ```

2. **Add your API keys to `.env`**:
   - Get OpenAI key: https://platform.openai.com/account/api-keys
   - Get Anthropic key: https://console.anthropic.com/
   - Get Gemini key: https://aistudio.google.com/app/apikey

3. **Your `.env` file is automatically ignored by git** - never commit it!

4. **Mock responses available** - Works without API keys for testing

## 🏗️ Architecture

### Backend (FastAPI + Python)
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: Database ORM for task and plan management
- **Pydantic**: Data validation and serialization
- **LLM Integration**: Support for OpenAI GPT and Anthropic Claude models

### Database (SQLite)
- **TaskPlan**: Stores goal information and plan metadata
- **Task**: Individual tasks with dependencies, priorities, and timelines

### Frontend (HTML/CSS/JavaScript)
- Clean, responsive web interface
- Real-time plan generation and visualization
- Task dependency visualization

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenAI API key (optional, falls back to mock responses)
- Anthropic API key (optional)

### Installation

#### Option 1: Automated Setup (Recommended)

**Windows:**
```batch
# Run the setup script
setup.bat
```

**Unix/Linux/macOS:**
```bash
# Make script executable and run
chmod +x setup.sh
./setup.sh
```

#### Option 2: Manual Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd smart-task-planner
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Activate virtual environment
   # Windows:
   venv\Scripts\activate
   # Unix/Linux/macOS:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your API keys:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

6. **Access the application**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Frontend: Open `frontend/index.html` in your browser

## 📖 API Usage

### Create a Task Plan

```bash
curl -X POST "http://localhost:8000/plan" \
     -H "Content-Type: application/json" \
     -d '{"goal": "Launch a product in 2 weeks"}'
```

### Get a Task Plan

```bash
curl "http://localhost:8000/plans/1"
```

### List All Plans

```bash
curl "http://localhost:8000/plans"
```

### Update Task Status

```bash
curl -X PUT "http://localhost:8000/tasks/1/status?status=completed"
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for GPT models | None |
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude models | None |
| `GEMINI_API_KEY` | Google Gemini API key | None |
| `DEFAULT_LLM_PROVIDER` | Which LLM to use (`openai`, `anthropic`, or `gemini`) | `openai` |
| `DATABASE_URL` | Database connection string | `sqlite:///./tasks.db` |
| `API_HOST` | API server host | `localhost` |
| `API_PORT` | API server port | `8000` |

### LLM Models

- **OpenAI**: `gpt-3.5-turbo`, `gpt-4`, `gpt-4-turbo`
- **Anthropic**: `claude-3-haiku-20240307`, `claude-3-sonnet-20240229`
- **Google Gemini**: `gemini-pro`, `gemini-pro-vision`

## 📊 Example Output

For the goal "Launch a simple blog website in 2 weeks", the AI might generate:

```json
{
  "title": "Blog Website Launch Plan",
  "description": "Complete plan to design, develop, and launch a blog website",
  "estimated_duration_days": 14,
  "tasks": [
    {
      "title": "Planning and Research",
      "description": "Research target audience, competitors, and define blog structure",
      "estimated_hours": 8.0,
      "priority": "high",
      "dependencies": [],
      "deadline_days_from_start": 2
    },
    {
      "title": "Design and Wireframing",
      "description": "Create visual design and wireframes for the blog",
      "estimated_hours": 12.0,
      "priority": "high",
      "dependencies": [0],
      "deadline_days_from_start": 5
    }
  ]
}
```

## 🧪 Testing

Run the test suite:

```bash
# Install test dependencies
pip install -e ".[dev]"

# Run tests  
pytest tests/ -v
```

## 🔄 Development

### Code Quality

```bash
# Format code
black .
isort .

# Lint code
flake8 .

# Type checking
mypy .
```

### Adding New LLM Providers

1. Extend the `LLMService` class in `app/services/llm_service.py`
2. Add provider-specific configuration
3. Implement the generation method
4. Update environment variable documentation

## 📋 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| POST | `/plan` | Create new task plan |
| GET | `/plans/{id}` | Get specific task plan |
| GET | `/plans` | List all task plans |
| PUT | `/tasks/{id}/status` | Update task status |

## 🎨 Frontend Features

- **Modern Design**: Beautiful gradient backgrounds with animated particles
- **Enhanced UI**: Improved typography, animations, and visual hierarchy
- **Goal Input**: Large text area with example suggestions
- **Real-time Generation**: Animated loading states with progress indicators
- **Visual Task Cards**: Color-coded priority indicators with hover effects
- **Dependency Display**: Clear visualization of task relationships with icons
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- **Interactive Elements**: Smooth animations and transitions throughout

## 🔍 Troubleshooting

### Common Issues

1. **No LLM API Keys**: The application will fall back to mock responses
2. **Database Issues**: Delete `tasks.db` to reset the database
3. **CORS Errors**: Update CORS settings in `main.py` for production
4. **Import Errors**: Ensure virtual environment is activated and dependencies installed
5. **Port Already in Use**: Change `API_PORT` in `.env` or stop other services on port 8000
6. **Virtual Environment Issues**: Delete `venv` folder and run setup script again

### Virtual Environment Commands

```bash
# Activate virtual environment
# Windows:
venv\Scripts\activate
# Unix/Linux/macOS:
source venv/bin/activate

# Deactivate virtual environment
deactivate

# Install new dependencies
pip install package_name
pip freeze > requirements.txt  # Update requirements file
```

### Debugging

Enable debug mode by setting `DEBUG=True` in your `.env` file.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License. See LICENSE file for details.

## 🚀 Deployment

### Docker (Optional)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . .

RUN pip install -e .

EXPOSE 8000

CMD ["python", "main.py"]
```

### Production Considerations

- Use a production database (PostgreSQL, MySQL)
- Set up proper CORS policies
- Use environment-specific configuration
- Implement proper logging and monitoring
- Set up HTTPS/SSL certificates
- Use a production WSGI server (Gunicorn, uWSGI)

## 🔮 Future Enhancements

- [ ] User authentication and multi-tenancy
- [ ] Real-time collaboration features
- [ ] Advanced project templates
- [ ] Integration with popular project management tools
- [ ] Mobile app development
- [ ] Advanced analytics and reporting
- [ ] Team management features
- [ ] Calendar integration
- [ ] File attachments and documentation
- [ ] Advanced dependency management (Gantt charts)

## 📞 Support

For support, please open an issue on GitHub or contact the development team.

---

Built with ❤️ using FastAPI, SQLAlchemy, and modern AI models.