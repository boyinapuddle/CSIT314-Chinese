# Centralised login BCE and sequence diagrams

## BCE diagram

```mermaid
flowchart LR
    Actor[User] --> Boundary[LoginBoundary]
    Boundary --> Control[AuthenticationController]
    Control --> Account[UserAccount]
    Control --> Profile[UserProfile]
    Control --> RoleControl[Role specific LoginController]
    RoleControl --> Session[UserSession]
```

The role specific Controller is one of UserAdminLoginController, InteriorDesignerLoginController, CustomerLoginController or PlatformManagerLoginController. AuthenticationController chooses it only after UserProfile returns the stored profile name.

## Sequence diagram

```mermaid
sequenceDiagram
    actor User
    participant B as LoginBoundary
    participant A as AuthenticationController
    participant UA as UserAccount
    participant UP as UserProfile
    participant RC as Role specific LoginController
    participant S as UserSession

    User->>B: submit username and password
    B->>A: login username and password
    A->>UA: find_by_username username
    UA-->>A: account
    A->>UA: verify_password account and password
    UA-->>A: valid or invalid
    A->>UP: get_profile profile_id
    UP-->>A: profile
    A->>A: validate active account and profile
    A->>A: determine role from profile name
    A->>RC: complete_login account and profile
    RC->>S: create_session account_id and role
    S-->>RC: session_id
    RC-->>A: account and session_id
    A-->>B: account and session_id
    B-->>User: authenticated result
```

## Failure flow

Invalid credentials, a suspended account, a suspended profile, or an unsupported profile name returns a failed result. No UserSession is created.
