# User Story 6: Create User Account

## BCE Diagram

```mermaid
flowchart LR
    N0["Actor<br/>User Admin"]
    N1["&lt;&lt;boundary&gt;&gt;<br/>CreateUserAccountBoundary<br/><br/>+submit()<br/>+profiles()"]
    N2["&lt;&lt;control&gt;&gt;<br/>CreateUserAccountController<br/><br/>+create()<br/>+profiles()"]
    N3["&lt;&lt;entity&gt;&gt;<br/>UserProfile<br/><br/>+search_profiles("")"]
    N4["&lt;&lt;entity&gt;&gt;<br/>UserAccount<br/><br/>+create_account(username, password, profile_id, display_name, email)"]
    N0 -->|"request available profiles"| N1
    N1 -->|"profiles()"| N2
    N2 -->|"search_profiles(&quot;&quot;)"| N3
    N3 -->|"profiles with role and status"| N2
    N2 -->|"create_account(...)"| N4
    N4 -->|"account_id or duplicate username error"| N2
    N2 -->|"result"| N1
```

## Sequence Diagram

```mermaid
sequenceDiagram
    actor P0 as User Admin
    participant P1 as CreateUserAccountBoundary
    participant P2 as CreateUserAccountController
    participant P3 as UserProfile
    participant P4 as UserAccount
    P0->>P1: request available profiles
    P1->>P2: profiles()
    P2->>P3: search_profiles("")
    P3->>P2: profiles with role and status
    P0->>P1: submit account form
    P1->>P2: create(...)
    P2->>P4: create_account(...)
    P4->>P2: account_id or duplicate username error
    P2-->>P1: result
    P1-->>P0: display result
```
