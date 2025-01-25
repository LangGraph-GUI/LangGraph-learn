# SubGraph

## Overview
```
graph LR
    subgraph "Region C: Lottery System"
        subgraph "Region A: Buy Lottery"
            A[Buy] --> B[Check]
        end
        subgraph "Region B: Buy Reward"
            C[Buy] --> D[Reward]
        end
        A -- include --> C
        B -- include --> C
        C -- include --> C
        D -- include --> C
    end
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#ccf,stroke:#333,stroke-width:2px
    style C fill:#cfc,stroke:#333,stroke-width:2px
    style D fill:#fcc,stroke:#333,stroke-width:2px
    style "Region A: Buy Lottery" fill:#eee,stroke:#ddd,stroke-width:2px
    style "Region B: Buy Reward" fill:#eee,stroke:#ddd,stroke-width:2px
    style "Region C: Lottery System" fill:#fff,stroke:#aaa,stroke-width:2px
```
