# User Story 12: User Admin Logout

## BCE Diagram

```mermaid
flowchart LR
    N0["Actor<br/>User Admin"]
    N1["boundary<br/>UserAdminLogoutBoundary<br/><br/>+submit()"]
    N2["control<br/>UserAdminLogoutController<br/><br/>+logout()"]
    N3["entity<br/>Session<br/><br/>+invalidate_session(session_id)"]
    N0 -->|"submit(session_context)"| N1
    N1 -->|"logout(session_context)"| N2
    N2 -->|"invalidate_session(session_id)"| N3
    N3 -->|"invalidated"| N2
    N2 -->|"result"| N1
```

## Sequence Diagram

```mermaid
sequenceDiagram
    actor P0 as User Admin
    participant P1 as UserAdminLogoutBoundary
    participant P2 as UserAdminLogoutController
    participant P3 as Session
    P0->>P1: submit(session_context)
    P1->>P2: logout(session_context)
    P2-->>P3: invalidate_session(session_id)
    P3->>P2: invalidated
    P2-->>P1: result
    P1->>P0: return to login page
```
