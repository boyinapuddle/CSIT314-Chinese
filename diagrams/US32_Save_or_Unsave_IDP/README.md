# User Story 32: Save or Unsave IDP

## BCE Diagram

```mermaid
flowchart LR
    N0["Actor<br/>Customer"]
    N1["boundary<br/>SaveIDPBoundary<br/><br/>+submit()<br/>+unsave()<br/>+check_saved()"]
    N2["control<br/>SaveIDPController<br/><br/>+save_idp()<br/>+unsave_idp()<br/>+check_saved()"]
    N3["entity<br/>Favourite<br/><br/>+save_idp(customer_id, project_id)<br/>+unsave_idp(customer_id, project_id)<br/>+check_saved(customer_id, project_id)"]
    N4["entity<br/>IDP<br/><br/>+view_available_idp(project_id)"]
    N0 -->|"save, unsave, or check project"| N1
    N1 -->|"save / unsave / check_saved(session, project_id)"| N2
    N2 -->|"save_idp / unsave_idp / check_saved"| N3
    N3 -->|"view_available_idp(project_id) when saving"| N4
    N4 -->|"available or unavailable"| N3
    N3 -->|"saved state result"| N2
    N2 -->|"result"| N1
```

## Sequence Diagram

```mermaid
sequenceDiagram
    actor P0 as Customer
    participant P1 as SaveIDPBoundary
    participant P2 as SaveIDPController
    participant P3 as Favourite
    participant P4 as IDP
    P0->>P1: save, unsave, or check project
    P1-->>P2: save / unsave / check_saved(session, project_id)
    P2->>P2: read customer_id from trusted session
    P2->>P3: save_idp / unsave_idp / check_saved
    P3-->>P4: view_available_idp(project_id) when saving
    P4->>P3: available or unavailable
    P3-->>P2: saved state result
    P2-->>P1: result
    P1->>P0: display Save or Saved state
```
