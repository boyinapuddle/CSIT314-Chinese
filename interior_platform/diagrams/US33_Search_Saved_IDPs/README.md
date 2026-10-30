# User Story 33: Search Saved IDPs

## BCE Diagram

```mermaid
flowchart LR
    N0["Actor<br/>Customer"]
    N1["&lt;&lt;boundary&gt;&gt;<br/>SearchSavedIDPBoundary<br/><br/>+submit()"]
    N2["&lt;&lt;control&gt;&gt;<br/>SearchSavedIDPController<br/><br/>+search()"]
    N3["&lt;&lt;entity&gt;&gt;<br/>Favourite<br/><br/>+search_saved_projects(customer_id, keyword)"]
    N0 -->|"submit(session, keyword)"| N1
    N1 -->|"search(session, keyword)"| N2
    N2 -->|"search_saved_projects(customer_id, keyword)"| N3
    N3 -->|"matching saved projects"| N2
    N2 -->|"results"| N1
```

## Sequence Diagram

```mermaid
sequenceDiagram
    actor P0 as Customer
    participant P1 as SearchSavedIDPBoundary
    participant P2 as SearchSavedIDPController
    participant P3 as Favourite
    P0->>P1: submit(session, keyword)
    P1->>P2: search(session, keyword)
    P2->>P2: read customer_id from trusted session
    P2->>P3: search_saved_projects(customer_id, keyword)
    P3-->>P2: matching saved projects
    P2-->>P1: results
    P1-->>P0: display results
```
