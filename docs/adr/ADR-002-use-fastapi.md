# ADR-002: Use FastAPI

## Status

Accepted

## Context

The project requires a web framework for building a REST API that can handle HTTP requests and integrate with Redis.

The API also needs to support asynchronous operations because Redis operations are performed asynchronously.

## Decision

We will use **FastAPI** as the web framework for the project.

## Why?

We chose FastAPI because:

* It has built-in support for asynchronous endpoints.
* It provides automatic API documentation through Swagger UI.
* It uses Python type hints for request validation.
* It integrates well with Pydantic.
* It is lightweight and suitable for building REST APIs.
* It provides good performance for I/O-bound applications.

## Consequences

### Positive

* Automatic interactive API documentation.
* Clear request and response validation.
* Native support for `async` and `await`.
* Simple and readable API development.
* Easy integration with asynchronous Redis operations.

### Negative

* The project depends on the FastAPI ecosystem.
* Developers need to understand asynchronous programming when working with async endpoints.

## Example

The API is exposed through FastAPI endpoints such as:

```text
POST /api/submit
```

The endpoint uses asynchronous Redis operations to implement the rate-limiting logic.
