# LogiTrack Pro — Entity Relationship Diagram

```mermaid
erDiagram
    USER ||--o{ SHIPMENT : "creates"
    USER ||--o| DRIVER : "linked to (optional)"
    USER }o--|| ROLE : "has"
    ROLE }o--o{ PERMISSION : "grants"

    WAREHOUSE ||--o{ INVENTORY_ITEM : "stores"
    WAREHOUSE ||--o{ SHIPMENT : "handles"
    WAREHOUSE }o--|| USER : "managed by"

    VEHICLE ||--o{ MAINTENANCE_RECORD : "has"
    VEHICLE ||--o{ DRIVER : "assigned to"
    VEHICLE ||--o{ SHIPMENT : "carries"
    VEHICLE ||--o{ GPS_LOG : "reports"
    VEHICLE ||--o{ IOT_READING : "reports"
    VEHICLE ||--o{ INCIDENT : "involved in"

    DRIVER ||--o{ SHIPMENT : "delivers"

    ROUTE ||--o{ SHIPMENT : "used by"

    SHIPMENT ||--o{ SHIPMENT_ATTACHMENT : "has"
    SHIPMENT ||--o{ SHIPMENT_STATUS_HISTORY : "logs"
    SHIPMENT ||--o{ INCIDENT : "may cause"

    USER ||--o{ NOTIFICATION : "receives"
    USER ||--o{ AUDIT_LOG : "performs action"

    USER {
        uuid id PK
        string email
        string first_name
        string last_name
        fk role
        bool is_verified
    }
    ROLE {
        int id PK
        string name
    }
    PERMISSION {
        int id PK
        string codename
    }
    SHIPMENT {
        uuid id PK
        string tracking_number
        string customer_name
        string status
        string priority
        fk vehicle
        fk driver
        fk route
        fk warehouse
        fk created_by
    }
    VEHICLE {
        uuid id PK
        string vehicle_number
        string truck_type
        string status
    }
    DRIVER {
        uuid id PK
        string full_name
        string license_number
        fk assigned_vehicle
        fk user
    }
    WAREHOUSE {
        uuid id PK
        string name
        string city
        fk manager
    }
    INVENTORY_ITEM {
        uuid id PK
        string product_name
        int quantity
        fk warehouse
    }
    ROUTE {
        uuid id PK
        string name
        decimal distance_km
    }
    GPS_LOG {
        uuid id PK
        fk vehicle
        decimal latitude
        decimal longitude
        datetime recorded_at
    }
    IOT_READING {
        uuid id PK
        fk vehicle
        decimal temperature_c
        bool is_alert
    }
    INCIDENT {
        uuid id PK
        string incident_type
        fk vehicle
        fk shipment
        string status
    }
    NOTIFICATION {
        uuid id PK
        fk recipient
        string title
        bool is_read
    }
    AUDIT_LOG {
        uuid id PK
        fk user
        string action
        string model_name
        string object_id
    }
```

> Render this on GitHub directly (Mermaid renders natively in `.md` files), or paste into
> [mermaid.live](https://mermaid.live) for an exportable PNG/SVG.
