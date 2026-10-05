# ADR-003: Use Docker Compose

## Status

Accepted

## Context

The project consists of multiple services:

* FastAPI application
* Redis

These services need to run together and communicate with each other.

Running and configuring each container manually would make development and testing more complicated.

## Decision

We will use **Docker Compose** to define and manage the project services.

Docker Compose will be responsible for:

* Building the FastAPI application image.
* Starting the FastAPI container.
* Starting the Redis container.
* Creating the network between the services.
* Managing the service configuration.

## Why?

We chose Docker Compose because:

* Multiple services can be defined in a single `compose.yaml` file.
* Services can communicate using their Compose service names.
* The entire application can be started with a single command.
* The development environment becomes easier to reproduce.
* Container configuration is kept in version control.

For example:

```bash
docker compose up -d
```

starts the application and Redis in the background.

## Consequences

### Positive

* Simple multi-container management.
* Consistent development environment.
* Easy service-to-service communication.
* Easy project startup and shutdown.
* Configuration is stored in `compose.yaml`.

### Negative

* Docker is required to run the project.
* Developers need basic knowledge of Docker and Docker Compose.
* Additional configuration is required compared with running the application directly.

## Example

The project defines two services:

```text
FastAPI application
        │
        │
        ▼
      Redis
```

The FastAPI application connects to Redis using the Compose service name:

```text
redis
```

rather than `localhost`.
