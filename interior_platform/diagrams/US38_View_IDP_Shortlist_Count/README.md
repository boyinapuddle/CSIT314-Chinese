# User Story 38: View IDP Shortlist Count

## BCE Diagram

```mermaid
flowchart LR
    N0["Actor<br/>Interior Designer"]
    N1["boundary<br/>ViewIDPShortlistsBoundary<br/><br/>+request()"]
    N2["control<br/>ViewIDPShortlistsController<br/><br/>+view()"]
    N3["entity<br/>ShortlistMetric<br/><br/>+for_designer(designer_id)"]
    N4["entity<br/>IDP<br/><br/>+get_designer_projects_with_metrics(designer_id)"]
    N0 -->|"request(session)"| N1
    N1 -->|"view(session)"| N2
    N2 -->|"for_designer(designer_id)"| N3
    N3 -->|"get_designer_projects_with_metrics(designer_id)"| N4
    N4 -->|"projects with shortlist totals from favourites"| N3
    N3 -->|"metrics"| N2
    N2 -->|"metrics"| N1
```

## Sequence Diagram

```mermaid
sequenceDiagram
    actor P0 as Interior Designer
    participant P1 as ViewIDPShortlistsBoundary
    participant P2 as ViewIDPShortlistsController
    participant P3 as ShortlistMetric
    participant P4 as IDP
    P0->>P1: request(session)
    P1->>P2: view(session)
    P2->>P2: read designer_id from trusted session
    P2->>P3: for_designer(designer_id)
    P3-->>P4: get_designer_projects_with_metrics(designer_id)
    P4->>P3: projects with shortlist totals from favourites
    P3-->>P2: metrics
    P2-->>P1: metrics
    P1->>P0: display shortlist counts
```
