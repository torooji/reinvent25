# Documentation Check Reminder

When working on this project, always check relevant documentation before making changes or answering questions.

## Documentation Locations

### Project Documentation
- **README.md**: Main project documentation with setup, API endpoints, and usage examples
- **backend/docs/**: Generated API documentation (pdoc HTML files)
  - Open `backend/docs/index.html` in a browser for interactive docs

### Code Documentation
- Check inline comments and docstrings in Python files
- Review Pydantic models for data schemas
- Check CDK stack definitions for infrastructure details

## When to Check Documentation

1. **Before answering questions** about API endpoints, schemas, or usage
2. **Before making changes** to ensure consistency with existing patterns
3. **When debugging** to understand current implementation
4. **When adding features** to maintain consistency with existing code

## Quick Reference

- API Base URL: Check README.md for current endpoint
- Event Schema: Defined in `backend/main.py` (Event and EventUpdate models)
- Infrastructure: See `infrastructure/stacks/backend_stack.py`
- Deployment: Follow instructions in README.md
