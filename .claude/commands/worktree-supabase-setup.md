# Worktree Supabase Setup

Configure and start a Supabase instance for the current Git worktree with unique project ID and ports to enable multiple worktrees to run simultaneously without port conflicts.

## Task

1. **Check Running Instances**
   - Run `docker ps --filter "name=supabase_db_" --format "{{.Names}} {{.Ports}}"` to see all running Supabase instances
   - Parse the output to find which ports are already in use
   - Identify the highest port numbers currently in use

2. **Determine New Ports**
   - Base Supabase ports (55001-55008):
     - API: 55001
     - DB: 55002
     - Shadow: 55003
     - Pooler: 55004
     - Studio: 55005
     - Inbucket: 55006
     - Analytics: 55007
     - Edge Inspector: 55008
   - Base Application ports:
     - Backend API: 7100
     - Frontend: 7200
     - Redis: 7300 (shared, no increment needed)
   - For each additional worktree, increment ALL ports by 10:
     - Worktree 1: Supabase 55001-55008, Backend 7100, Frontend 7200
     - Worktree 2: Supabase 55011-55018, Backend 7110, Frontend 7210
     - Worktree 3: Supabase 55021-55028, Backend 7120, Frontend 7220
   - Find the next available port set based on what's running
   - Check both `lsof -i :7100` and `docker ps` to determine which increment to use
   - **CRITICAL:** ALL service ports must be incremented, even if services are disabled, because Kong gateway still tries to bind to them

3. **Update project_id**
   - Get the current Git branch name
   - Convert to valid format (lowercase, replace special chars with hyphens)
   - Update `project_id` in `supabase/config.toml` to `algorise-{branch-name}`

4. **Update ALL Ports in config.toml**
   - Update `[api].port` to the new API port (e.g., 55011)
   - Update `[db].port` to the new DB port (e.g., 55012)
   - Update `[db].shadow_port` to the new shadow port (e.g., 55013)
   - Update `[db.pooler].port` to the new pooler port (e.g., 55014)
   - Update `[studio].port` to the new Studio port (e.g., 55015)
   - Update `[inbucket].port` to the new inbucket port (e.g., 55016)
   - Update `[analytics].port` to the new analytics port (e.g., 55017)
   - Update `[edge_runtime].inspector_port` to the new edge inspector port (e.g., 55018)
   - **Do NOT skip any ports, even if the service is disabled - Kong needs all ports to be available**

5. **Start Supabase**
   - Run `supabase start` to start the Supabase instance with the new configuration
   - Capture the output which contains the JWT keys (anon key and service_role key)

6. **Update Backend .env File**
   - Update `POSTGRES_PORT` to match the new DB port (e.g., 55012)
   - Update `SUPABASE_URL` to match the new API URL (e.g., `http://127.0.0.1:55011`)
   - Update `SUPABASE_ANON_KEY` with the anon key from `supabase start` output (usually default local key)
   - Update `SUPABASE_SERVICE_KEY` with the service_role key from `supabase start` output (usually default local key)
   - Update `API_BASE_URL` to match the new backend port (e.g., `http://localhost:7110`)
   - Update `CLERK_AUTHORIZED_PARTIES` to match new ports (e.g., `http://localhost:7210,http://localhost:7110`)
   - If .env doesn't exist, check for .env.example and create .env from it

7. **Update Backend API Port in main.py**
   - Update the uvicorn port in `algorise/api/main.py` to match the new backend port
   - Change `port=7100` to `port=7110` (or appropriate increment)

8. **Update Supabase Auth Config**
   - Update `site_url` in `supabase/config.toml` under `[auth]` to match new frontend port (e.g., `http://127.0.0.1:7210`)
   - Update `additional_redirect_urls` to match new frontend port (e.g., `["https://127.0.0.1:7210"]`)

9. **Update Frontend Configuration**
   - Update `frontend/.env.local`:
     - Change `NEXT_PUBLIC_API_BASE_URL` to match new backend URL (e.g., `http://localhost:7110/api/v1`)
   - Update `frontend/package.json`:
     - Change `"dev": "next dev -p 7200"` to use new frontend port (e.g., `"next dev -p 7210"`)
     - Change `"start": "next start -p 7200"` to use new frontend port (e.g., `"next start -p 7210"`)

10. **Show Summary**
   - Display what was changed:
     - Old project_id → New project_id
     - Old Supabase ports → New Supabase ports
     - Old Backend/Frontend ports → New Backend/Frontend ports
   - Show all connection URLs:
     - Database connection string
     - Supabase Studio UI URL: `http://localhost:{studio_port}`
     - Backend API URL: `http://localhost:{backend_port}`
     - Frontend URL: `http://localhost:{frontend_port}`
   - Confirm that Supabase is running successfully and all files have been updated

## Port Assignment Logic

```
Supabase Ports:
Base ports (Worktree 1):     55001, 55002, 55003, 55004, 55005, 55006, 55007, 55008
Next ports (Worktree 2):     55011, 55012, 55013, 55014, 55015, 55016, 55017, 55018
Next ports (Worktree 3):     55021, 55022, 55023, 55024, 55025, 55026, 55027, 55028

Application Ports:
Base ports (Worktree 1):     Backend: 7100, Frontend: 7200
Next ports (Worktree 2):     Backend: 7110, Frontend: 7210
Next ports (Worktree 3):     Backend: 7120, Frontend: 7220

Pattern: increment ALL ports by 10 for each worktree
Supabase Services: API, DB, Shadow, Pooler, Studio, Inbucket, Analytics, Edge Inspector
Application Services: Backend API, Frontend Dev Server
```

## Expected Format

Example for Worktree 2 (increment by 10):

```toml
project_id = "algorise-{branch-name}"

[api]
port = 55011  # Incremented by 10

[db]
port = 55012  # Incremented by 10
shadow_port = 55013  # Incremented by 10

[db.pooler]
port = 55014  # Incremented by 10

[studio]
port = 55015  # Incremented by 10

[inbucket]
port = 55016  # Incremented by 10

[analytics]
port = 55017  # Incremented by 10

[edge_runtime]
inspector_port = 55018  # Incremented by 10
```

## Important Notes

### Supabase Configuration
- Always preserve the `algorise-` prefix for project_id
- **CRITICAL:** ALL 8 Supabase service ports must be incremented (API, DB, Shadow, Pooler, Studio, Inbucket, Analytics, Edge Inspector)
- Even if a service is disabled in config.toml, its port must still be incremented because Kong gateway tries to bind to all ports
- Forgetting to update even one port will cause `supabase start` to fail with "port is already allocated" error
- Ports must not conflict with any running Supabase instances
- Check both Docker containers (`docker ps`) AND port usage (`lsof -i :7100`) to determine which increment to use
- **Minimal Setup:** Only Auth service needs to be enabled in config.toml - API and Storage can remain disabled

### Files to Update
1. **supabase/config.toml**:
   - `project_id` - branch-specific name
   - All 8 service ports (API, DB, Shadow, Pooler, Studio, Inbucket, Analytics, Edge Inspector)
   - `[auth].site_url` - frontend URL
   - `[auth].additional_redirect_urls` - frontend URL

2. **Backend .env**:
   - `POSTGRES_PORT` - database port (e.g., 55012)
   - `SUPABASE_URL` - API URL (e.g., `http://127.0.0.1:55011`)
   - `API_BASE_URL` - backend URL (e.g., `http://localhost:7110`)
   - `CLERK_AUTHORIZED_PARTIES` - both backend and frontend URLs
   - `SUPABASE_ANON_KEY` and `SUPABASE_SERVICE_KEY` - usually default local keys

3. **algorise/api/main.py**:
   - uvicorn `port` parameter (e.g., 7110)

4. **frontend/.env.local**:
   - `NEXT_PUBLIC_API_BASE_URL` - backend API URL (e.g., `http://localhost:7110/api/v1`)

5. **frontend/package.json**:
   - `"dev"` script port flag (e.g., `-p 7210`)
   - `"start"` script port flag (e.g., `-p 7210`)

### Summary to Show User
- Display ALL connection URLs:
  - Supabase Studio: `http://localhost:{studio_port}`
  - Database: `postgresql://postgres:postgres@127.0.0.1:{db_port}/postgres`
  - Backend API: `http://localhost:{backend_port}`
  - Frontend: `http://localhost:{frontend_port}`
- Show a table of old vs new ports for both Supabase and Application services
- Confirm all files have been updated successfully

## Quick Reference: Complete File Update Checklist

For Worktree 2 (increment by 10), update these exact locations:

1. `supabase/config.toml`:
   - Line 5: `project_id = "algorise-{branch-name}"`
   - Line 10: `port = 55011`
   - Line 26: `port = 55012`
   - Line 28: `shadow_port = 55013`
   - Line 36: `port = 55014`
   - Line 72: `port = 55015`
   - Line 83: `port = 55016`
   - Line 302: `port = 55017`
   - Line 293: `inspector_port = 55018`
   - Line 110: `site_url = "http://127.0.0.1:7210"`
   - Line 112: `additional_redirect_urls = ["https://127.0.0.1:7210"]`

2. `.env`:
   - `POSTGRES_PORT=55012`
   - `SUPABASE_URL=http://127.0.0.1:55011`
   - `API_BASE_URL=http://localhost:7110`
   - `CLERK_AUTHORIZED_PARTIES=http://localhost:7210,http://localhost:7110`

3. `algorise/api/main.py`:
   - Line ~277: `port=7110,`

4. `frontend/.env.local`:
   - `NEXT_PUBLIC_API_BASE_URL=http://localhost:7110/api/v1`

5. `frontend/package.json`:
   - Line 6: `"dev": "next dev -p 7210",`
   - Line 8: `"start": "next start -p 7210",`
