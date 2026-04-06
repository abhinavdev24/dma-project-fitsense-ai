# FitSense AI Dashboard

A production-ready Streamlit-based data analysis dashboard for the FitSense AI MySQL database.

## Features

- **7 Dashboard Pages**: Overview, Workouts, Nutrition, Sleep, Weight, Users, and SQL Explorer
- **Interactive Visualizations**: Plotly-based charts with dark theme
- **SQL Query Console**: Execute custom queries with syntax highlighting
- **Authentication**: Google OAuth integration with demo mode
- **Performance Optimized**: Caching, connection pooling, and lazy loading
- **Mobile Responsive**: Works on desktop and tablet devices

## Architecture

The FitSense AI Dashboard follows a three-tier architecture pattern:

```mermaid
graph TB
    subgraph Presentation["Layer 1 - Presentation"]
        Browser[Browser Client]
        Streamlit[Streamlit Server]
        Pages[Dashboard Pages]
        Sidebar[Sidebar Navigation]
        Charts[Plotly Charts]
        SQLConsole[SQL Console]
    end

    subgraph Business["Layer 2 - Business Logic"]
        Queries[queries.py]
        ChartLib[charts.py]
        SQLConsoleLib[sql_console.py]
        Auth[auth.py]
        Cache[cache.py]
    end

    subgraph Data["Layer 3 - Data Access"]
        DBPool[Connection Pool]
        MySQL[(MySQL Database)]
    end

    Browser -->|HTTP| Streamlit
    Streamlit --> Pages
    Pages --> Sidebar
    Pages --> Charts
    Pages --> SQLConsole
    Pages --> Queries
    Queries --> ChartLib
    ChartLib --> SQLConsoleLib
    Queries --> DBPool
    DBPool --> MySQL
```

## Database Schema

The MySQL database contains 25 tables organized into 9 domains:

```mermaid
erDiagram
    users {
        int user_id "PK"
        varchar name "username"
        varchar email "email address"
        datetime created_at "creation timestamp"
    }
    user_profiles {
        int user_id "PK, FK"
        date date_of_birth "birth date"
        varchar sex "gender"
        decimal height_cm "height in cm"
        varchar activity_level "activity level"
        datetime updated_at "last update"
    }
    user_medical_profiles {
        int medical_profile_id "PK"
        int user_id "FK"
        tinyint has_injuries "has injuries"
        text injury_details "injury details"
        text surgeries_history "surgeries history"
        text family_history "family history"
        text notes "notes"
        datetime updated_at "last update"
    }
    user_medications {
        int medication_id "PK"
        int user_id "FK"
        varchar medication_name "medication name"
        varchar dosage "dosage"
        varchar frequency "frequency"
        date start_date "start date"
        date end_date "end date"
        text notes "notes"
    }
    user_allergies {
        int allergy_id "PK"
        int user_id "FK"
        varchar allergen "allergen"
        varchar reaction "reaction"
        varchar severity "severity"
        text notes "notes"
    }
    goals {
        int goal_id "PK"
        varchar name "goal name"
        text description "goal description"
    }
    user_goals {
        int user_id "PK, FK"
        int goal_id "PK, FK"
        tinyint priority "goal priority"
    }
    conditions {
        int condition_id "PK"
        varchar name "condition name"
        text description "condition description"
    }
    user_conditions {
        int user_id "PK, FK"
        int condition_id "PK, FK"
        varchar severity "condition severity"
        text notes "notes"
    }
    equipment {
        int equipment_id "PK"
        varchar name "equipment name"
        varchar category "equipment category"
    }
    exercises {
        int exercise_id "PK"
        varchar name "exercise name"
        varchar primary_muscle "primary muscle group"
        text notes "exercise notes"
        varchar video_url "video URL"
        text thumbnail_base64 "thumbnail"
    }
    exercise_equipment {
        int exercise_id "PK, FK"
        int equipment_id "PK, FK"
    }
    workout_plans {
        int plan_id "PK"
        int user_id "FK"
        varchar name "plan name"
        boolean is_active "is active"
        datetime created_at "creation timestamp"
    }
    plan_days {
        int plan_day_id "PK"
        int plan_id "FK"
        varchar name "day name"
        tinyint day_order "day order"
        text notes "notes"
    }
    plan_exercises {
        int plan_exercise_id "PK"
        int plan_day_id "FK"
        int exercise_id "FK"
        smallint position "position"
        text notes "notes"
    }
    plan_sets {
        int plan_set_id "PK"
        int plan_exercise_id "FK"
        tinyint set_number "set number"
        tinyint target_reps "target reps"
        decimal target_weight "target weight"
        tinyint target_rir "target RIR"
        smallint rest_seconds "rest seconds"
    }
    workouts {
        int workout_id "PK"
        int user_id "FK"
        int plan_id "FK"
        int plan_day_id "FK"
        datetime started_at "start time"
        datetime ended_at "end time"
        text notes "notes"
    }
    workout_exercises {
        int workout_exercise_id "PK"
        int workout_id "FK"
        int exercise_id "FK"
        int plan_exercise_id "FK"
        smallint position "position"
        text notes "notes"
    }
    workout_sets {
        int workout_set_id "PK"
        int workout_exercise_id "FK"
        tinyint set_number "set number"
        tinyint reps "repetitions"
        decimal weight "weight used"
        tinyint rir "RIR"
        boolean is_warmup "is warmup"
        datetime completed_at "completed timestamp"
    }
    ai_interactions {
        int ai_interaction_id "PK"
        int user_id "FK"
        varchar context_type "context type"
        int context_id "context ID"
        text query_text "query text"
        text response_text "response text"
        varchar model_name "model name"
        datetime created_at "creation timestamp"
    }
    calorie_targets {
        int calorie_target_id "PK"
        int user_id "FK"
        int maintenance_calories "maintenance calories"
        varchar method "calculation method"
        date effective_from "effective from"
        date effective_to "effective to"
        text notes "notes"
        datetime created_at "creation timestamp"
    }
    calorie_intake_logs {
        int calorie_log_id "PK"
        int user_id "FK"
        date log_date "log date"
        int calories_consumed "calories consumed"
        text notes "notes"
        datetime created_at "creation timestamp"
    }
    sleep_targets {
        int sleep_target_id "PK"
        int user_id "FK"
        decimal target_sleep_hours "target sleep hours"
        date effective_from "effective from"
        date effective_to "effective to"
        text notes "notes"
        datetime created_at "creation timestamp"
    }
    sleep_duration_logs {
        int sleep_log_id "PK"
        int user_id "FK"
        date log_date "log date"
        decimal sleep_duration_hours "sleep hours"
        text notes "notes"
        datetime created_at "creation timestamp"
    }
    weight_logs {
        int weight_log_id "PK"
        int user_id "FK"
        datetime logged_at "log timestamp"
        decimal weight_kg "weight in kg"
        decimal body_fat_percentage "body fat %"
        text notes "notes"
    }

    users ||--|| user_profiles : "1:1"
    users ||--|| user_medical_profiles : "1:1"
    users ||--o{ user_medications : "1:N"
    users ||--o{ user_allergies : "1:N"
    users ||--o{ user_goals : "1:N"
    users ||--o{ user_conditions : "1:N"
    users ||--o{ workout_plans : "1:N"
    users ||--o{ workouts : "1:N"
    users ||--o{ ai_interactions : "1:N"
    users ||--o{ calorie_targets : "1:N"
    users ||--o{ calorie_intake_logs : "1:N"
    users ||--o{ sleep_targets : "1:N"
    users ||--o{ sleep_duration_logs : "1:N"
    users ||--o{ weight_logs : "1:N"
    goals ||--o{ user_goals : "1:N"
    conditions ||--o{ user_conditions : "1:N"
    exercises ||--o{ exercise_equipment : "1:N"
    equipment ||--o{ exercise_equipment : "1:N"
    workout_plans ||--o{ plan_days : "1:N"
    plan_days ||--o{ plan_exercises : "1:N"
    exercises ||--o{ plan_exercises : "1:N"
    plan_exercises ||--o{ plan_sets : "1:N"
    workouts ||--o{ workout_exercises : "1:N"
    exercises ||--o{ workout_exercises : "1:N"
    plan_exercises ||--o{ workout_exercises : "1:N"
    workout_exercises ||--o{ workout_sets : "1:N"
```

## Network Architecture

```mermaid
graph LR
    subgraph External["External Network"]
        Browser[Browser port 8501]
    end

    subgraph Docker["Docker fitsense-network"]
        subgraph Dashboard["Dashboard Container"]
            Streamlit[Streamlit Server app.py]
            Python[Python 3.11 Backend]
            Pool[Connection Pool Size 5]
        end

        subgraph Database["MySQL Container"]
            MySQL[MySQL 9.6.0 port 3306]
            Data[(Persistent Volume)]
        end
    end

    Browser -.->|HTTP| Streamlit
    Python -.->|MySQL| Pool
    Pool -.->|TCP| MySQL
    MySQL --> Data
```

### Port Mappings

| Service             | Container Port | Host Port | Protocol |
| ------------------- | -------------- | --------- | -------- |
| Streamlit Dashboard | 8501           | 8501      | HTTP     |
| MySQL Database      | 3306           | 3306      | TCP      |

## Quick Start

### Prerequisites

- Python 3.10+
- MySQL 8.0+ (or Docker)
- pip

### Installation

1. **Clone the repository**

   ```bash
   cd fitsense-ai-dashboard
   ```

2. **Create virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**

   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. **Run the dashboard**
   ```bash
   streamlit run app.py
   ```

## Docker Deployment

### Using Docker Compose (Recommended)

```bash
docker-compose up -d
```

This starts both the MySQL database and the dashboard.

### Using Docker Only

```bash
# Build the image
docker build -t fitsense-dashboard .

# Run with environment variables
docker run -p 8501:8501 \
  -e DB_HOST=mysql-host \
  -e DB_PORT=3306 \
  -e DB_USER=root \
  -e DB_PASSWORD=secret \
  -e DB_NAME=fitsense_ai \
  fitsense-dashboard
```

## Environment Variables

| Variable               | Description                | Default     |
| ---------------------- | -------------------------- | ----------- |
| `DB_HOST`              | MySQL host                 | localhost   |
| `DB_PORT`              | MySQL port                 | 3306        |
| `DB_USER`              | Database user              | root        |
| `DB_PASSWORD`          | Database password          | (none)      |
| `DB_NAME`              | Database name              | fitsense_ai |
| `DEMO_MODE`            | Enable demo login          | false       |
| `GOOGLE_CLIENT_ID`     | Google OAuth client ID     | (none)      |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | (none)      |
| `DEBUG`                | Enable debug mode          | false       |
| `DISABLE_CACHE`        | Disable query caching      | false       |

## Project Structure

```
fitsense-ai-dashboard/
├── app.py                 # Main entry point
├── pages/                 # Dashboard pages
│   ├── 1_Overview.py
│   ├── 2_Workouts.py
│   ├── 3_Nutrition.py
│   ├── 4_Sleep.py
│   ├── 5_Weight.py
│   ├── 6_Users.py
│   └── 7_SQL_Explorer.py
├── utils/                  # Utility modules
│   ├── db.py              # Database connection
│   ├── queries.py         # SQL queries
│   ├── charts.py          # Chart configurations
│   ├── sql_console.py     # SQL console
│   ├── auth.py            # Authentication
│   ├── cache.py           # Caching utilities
│   ├── error_handler.py   # Error handling
│   └── performance.py     # Performance utilities
├── assets/
│   └── style.css          # Custom CSS
├── tests/                 # Test suite
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Code Flow

### Request Flow

```mermaid
sequenceDiagram
    participant Browser
    participant Streamlit
    participant Page
    participant Utils
    participant DB
    participant MySQL

    Browser->>Streamlit: Page Request
    Streamlit->>Page: Render Page
    Page->>Utils: Import Utils
    Page->>DB: ensure_db_connection
    DB->>DB: test_connection
    DB->>MySQL: SELECT 1
    MySQL-->>DB: Connection OK
    DB-->>Page: db_connected = True
    Page->>Utils: Get Query
    Utils->>DB: execute_query
    DB->>MySQL: Execute SQL
    MySQL-->>DB: Results
    DB-->>Page: DataFrame
    Page->>Utils: create_chart
    Utils-->>Page: Plotly Figure
    Page->>Streamlit: Render Charts
    Streamlit-->>Browser: HTML Response
```

### Query Execution Flow

```mermaid
flowchart LR
    A[Page Load] --> B[Select Query from queries.py]
    B --> C[execute_query in utils/db.py]
    C --> D[get_connection Context Manager]
    D --> E[Get Connection from Pool]
    E --> F{Check Retries MAX_RETRIES}
    F -->|Yes| G[Execute Query]
    F -->|No| H[Raise Error]
    G --> I[Cursor execute]
    I --> J[fetchall]
    J --> K[Binary to Hex UUID Conversion]
    K --> L[DataFrame Return]
    L --> M[Chart or Table Render]
    M --> N[Display to User]
```

### Database Connection Pool Flow

```mermaid
flowchart TD
    A[Module Import] --> B[init_connection_pool in utils/db.py]
    B --> C{Create Pool}
    C --> D[Pool Config - fitsense_pool, size=5]
    D --> E[Pool Created]
    E --> F[get_connection_pool Lazy Init]
    F --> G[get_connection Context Manager]
    G --> H[Get Connection from Pool]
    H --> I[Execute Query]
    I --> J[Connection Close]
    J --> K[Return to Pool]
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_dashboard.py
```

## SQL Explorer Features

- **Predefined Queries**: Load common queries by category
- **Custom Queries**: Execute any valid SQL
- **Query History**: Track executed queries
- **Export**: Download results as CSV or JSON
- **Quick Charts**: Auto-generate visualizations

## Design System

The dashboard follows a dark-mode glassmorphism design:

- **Background**: #0F172A (dark slate)
- **Cards**: #1E293B with glass effect
- **Primary**: #3B82F6 (blue)
- **Secondary**: #F59E0B (amber)
- **Typography**: Inter/Roboto

## Deployment Options

### Streamlit Cloud

1. Push to GitHub
2. Connect to Streamlit Cloud
3. Set environment variables
4. Deploy

### Heroku

```bash
heroku create fitsense-dashboard
heroku container:push web
heroku container:release web
```

### AWS Elastic Beanstalk

```bash
eb init
eb create production
eb deploy
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues and questions, please open a GitHub issue.
