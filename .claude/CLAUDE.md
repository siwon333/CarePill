# CarePill Project - Claude Configuration

## Project Overview
**Project Name**: CarePill
**Type**: Django-based Medicine Analysis System
**Branch**: develop-voice
**Purpose**: AI-powered medicine identification and analysis platform

## Technology Stack
- **Backend**: Django 4.2.7
- **AI/ML**: OpenAI API (GPT integration)
- **Image Processing**: OpenCV, Pillow
- **Database**: Django ORM (SQLite/PostgreSQL)
- **Python**: 3.x

## Project Structure
```
CarePill/
├── medicine_analyzer/     # Main Django app for medicine analysis
│   ├── models.py         # Database models
│   ├── views.py          # API endpoints and business logic
│   ├── urls.py           # URL routing
│   └── migrations/       # Database migrations
├── medicine_project/     # Django project settings
│   ├── settings.py       # Project configuration
│   ├── urls.py           # Root URL configuration
│   └── wsgi.py          # WSGI application
├── media/               # User-uploaded images and files
├── claudedocs/          # Claude-specific documentation and analysis
└── .claude/            # Claude configuration
```

## Development Workflow

### Git Workflow
- **Main Branch**: `master` (production-ready code)
- **Development Branch**: `develop-voice` (current feature development)
- **Feature Branches**: Create from `develop-voice` for specific features
- **Commit Pattern**: Use descriptive messages following conventional commits

### Task Management
- Use TodoWrite for multi-step tasks (>3 steps)
- Track progress in claudedocs/ directory
- Regular checkpoints every 30 minutes for complex tasks

### Code Standards
- Follow Django best practices and conventions
- Use type hints where applicable
- Maintain DRY principle
- Write tests for new features
- Document API endpoints

## SuperClaude Integration

### Mode Preferences
- **--brainstorm**: For feature planning and requirements discovery
- **--task-manage**: For complex multi-step implementations
- **--token-efficient**: For large codebase operations
- **--think**: For architectural decisions

### MCP Server Usage
- **Context7**: Django documentation, OpenAI API patterns
- **Sequential**: Complex business logic analysis
- **Playwright**: E2E testing for web interfaces

### Quality Gates
- Run tests before marking tasks complete
- Validate migrations before committing
- Check for security vulnerabilities in dependencies
- Ensure proper error handling for API calls

## Project-Specific Rules

### Medicine Analysis Domain
- **Image Processing**: Validate image formats and sizes before processing
- **API Integration**: Handle OpenAI API errors gracefully with fallbacks
- **Data Privacy**: Ensure user-uploaded images are properly secured
- **Response Format**: Standardize JSON responses for medicine analysis

### Django-Specific
- **Models**: Use appropriate field types and validators
- **Migrations**: Always create migrations for model changes
- **Static Files**: Organize in appropriate directories
- **Media Files**: Implement proper file upload handling

### Environment Variables
Required in `.env`:
- `OPENAI_API_KEY`: OpenAI API authentication
- `DEBUG`: Development/production mode
- `SECRET_KEY`: Django secret key
- `ALLOWED_HOSTS`: Permitted hosts for deployment

## Development Priorities

### Phase 1: Foundation (Current)
- ✅ Project setup and configuration
- ✅ Branch management (develop-voice)
- 🔄 Code analysis and documentation
- ⏳ Environment setup validation

### Phase 2: Feature Development
- Voice integration for medicine analysis
- Enhanced image recognition
- User management and authentication
- API endpoint optimization

### Phase 3: Quality & Testing
- Unit tests for core functionality
- Integration tests for API endpoints
- E2E tests for user workflows
- Performance optimization

### Phase 4: Deployment
- Production environment configuration
- CI/CD pipeline setup
- Monitoring and logging
- Documentation finalization

## AI-Assisted Development Guidelines

### Code Review Focus
- Django security best practices
- Efficient database queries (avoid N+1)
- Proper error handling for AI API calls
- Input validation and sanitization

### Documentation Requirements
- API endpoint documentation
- Model schema descriptions
- Business logic explanations
- Deployment instructions

### Testing Strategy
- Unit tests: Models, utilities, helpers
- Integration tests: Views, API endpoints
- E2E tests: User workflows
- Performance tests: Image processing, API calls

## Notes
- Keep dependencies updated regularly
- Monitor OpenAI API usage and costs
- Implement rate limiting for API endpoints
- Use Django Debug Toolbar in development
- Maintain detailed change logs in claudedocs/
- 이모지 쓰지 않기.
---
*Generated: 2025-10-01*
*Last Updated: 2025-10-01*
