# User Story 50: Browse IDPs as Authenticated Non Customer

## BCE Diagram

```mermaid
flowchart LR
    N0["Actor<br/>Authenticated Non Customer User"]
    N1["boundary<br/>BrowseIDPBoundary<br/><br/>+submit()<br/>+request()"]
    N2["control<br/>BrowseIDPController<br/><br/>+search()<br/>+view()"]
    N3["entity<br/>IDP<br/><br/>+search_available_projects(keyword)<br/>+get_available_project(project_id)"]
    N0 -->|"search(keyword) or request(project_id)"| N1
    N1 -->|"search(keyword) or view(project_id)"| N2
    N2 -->|"search_available_projects(keyword) or get_available_project(project_id)"| N3
    N3 -->|"available projects or project details"| N2
    N2 -->|"read only result"| N1
```

## Sequence Diagram

```mermaid
sequenceDiagram
    actor P0 as Authenticated Non Customer User
    participant P1 as BrowseIDPBoundary
    participant P2 as BrowseIDPController
    participant P3 as IDP
    P0-->>P1: search(keyword) or request(project_id)
    P1-->>P2: search(keyword) or view(project_id)
    P2-->>P3: search_available_projects(keyword) or get_available_project(project_id)
    P3-->>P2: available projects or project details
    P2-->>P1: read only result
    P1->>P0: display projects without favourite actions
```
