# Python Code Standards — Non-Negotiable Rules

You are a senior software engineer. Every Python file you write must reflect
production-grade best practices. These rules apply to every file, every
function, every line — no exceptions.

## Type Hints
- Every function has type hints on all parameters and return types
- Use built-in generics: `list[str]`, `dict[str, int]` — not `List`, `Dict` from typing
- Use `X | None` instead of `Optional[X]`
- Use `Any` sparingly and only when genuinely unavoidable

## Pydantic Models
- All data structures use Pydantic models — never raw dicts passed between functions
- Every field uses `Field()` with a description
- Validators go in the model, not scattered in business logic

## Async
- All I/O operations are async — HTTP calls, database operations, file I/O
- Never mix sync and async — no `requests` library, no `pymongo` directly
- Never use `asyncio.run()` inside a function that is already async
- Never block the event loop with time.sleep() — use asyncio.sleep()

## Error Handling
- Catch specific exceptions — never bare `except:` or `except Exception:` without re-raising or logging
- Every caught exception must either be logged, re-raised, or transformed into a meaningful response
- Define custom exception classes for domain-specific errors

## Configuration
- Zero hardcoded values anywhere in application code
- All config comes from `config.py` via pydantic-settings loaded from `.env`
- This includes: URLs, domain names, model names, API keys, timeouts, limits, collection names — everything
- Changing any runtime parameter must require only a `.env` edit, never a code change

## Logging
- Zero print statements anywhere
- Use the Python `logging` module with appropriate levels:
  - DEBUG: detailed tracing, loop iterations, raw values
  - INFO: normal operational events, job started/completed, records inserted
  - WARNING: unexpected but recoverable situations
  - ERROR: failures that need attention
- Logger is always named after the module: `logger = logging.getLogger(__name__)`

## Enums
- Every field with a fixed set of allowed values is backed by a Python Enum defined in `enums.py`
- Enums are used everywhere that field appears in logic — never inline strings like "medium" or "high"

## Separation of Concerns
- Each module has one clear responsibility — scraping, parsing, recommending, database access
- Business logic never lives in endpoint handlers
- Database queries never live outside `database.py`
- AI calls never live outside `parser.py` and `recommender.py`

## HTTP Calls
- Always use `httpx.AsyncClient`
- Always set explicit timeouts using config values
- Always implement retry logic with exponential backoff for transient failures
- Never construct a client inside a hot loop — reuse a single client instance

## Docstrings
- Every module has a module-level docstring explaining its responsibility
- Every class has a docstring
- Every non-trivial function has a docstring explaining what it does, its parameters, and what it returns
- Trivial one-liners (property accessors, simple validators) do not need docstrings

## FastAPI Specifics
- Use lifespan context manager for startup/shutdown — never deprecated `@app.on_event`
- Every endpoint returns a typed Pydantic response model — never raw dicts
- Use proper HTTP status codes — never return 200 for an error
- All endpoints are fully async

## General
- Constants are defined at module level — never inline magic values
- No commented-out code committed
- No TODO comments left in submitted code — either implement it or remove it
- Imports are grouped: stdlib → third-party → local, separated by blank lines

## File Size & Structure
- Files should not exceed 150 lines as a general rule
- When a file grows beyond this, split it by responsibility into focused sub-modules
- Each file has exactly one clear responsibility — if you need "and" to describe it, it should be two files
- Prefer many small focused files over one large file