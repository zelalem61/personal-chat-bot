# Worktree Supabase Teardown

Stop and remove the Supabase containers for the current Git worktree to free up RAM and disk space.

## Task

1. **Get Current Project ID**
   - Read `project_id` from `supabase/config.toml`
   - Confirm this is the correct project to tear down

2. **Check Running Containers**
   - Run `docker ps --filter "name=supabase_" --format "{{.Names}}"` to see all running Supabase containers
   - Filter containers that match the current project_id
   - Display which containers will be stopped and removed

3. **Stop Supabase**
   - Run `supabase stop` to gracefully stop all Supabase services
   - This preserves data volumes by default

4. **Remove Containers (Optional)**
   - Ask user if they want to completely remove containers and volumes
   - If yes, run `supabase stop --no-backup` to remove everything including data
   - If no, just leave containers stopped (they can be restarted later)

5. **Verify Cleanup**
   - Run `docker ps --filter "name=supabase_{project_id}"` to verify containers are stopped
   - If volumes were removed, confirm with `docker volume ls`
   - Show memory/disk space freed

6. **Show Summary**
   - Display what was stopped/removed:
     - Project ID
     - Container names
     - Ports freed
   - Provide command to restart: `supabase start` (if data was preserved)
   - Or provide command to setup fresh instance: `/worktree-supabase-setup` (if data was removed)

## Important Notes

- `supabase stop` - Stops containers but preserves data (can restart later)
- `supabase stop --no-backup` - Removes everything including data (complete cleanup)
- Always confirm the project_id before tearing down to avoid deleting the wrong instance
- If you plan to return to this worktree later, use `supabase stop` without `--no-backup`
- If you're done with this worktree permanently, use `--no-backup` to free all resources
