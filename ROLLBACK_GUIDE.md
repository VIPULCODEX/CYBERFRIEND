# Rollback Guide (QuantX)

This guide keeps recovery simple when a change causes issues.

## 1. Safe Workflow Before Any New Change
1. Create a checkpoint commit.
2. Make one logical change block.
3. Test quickly.
4. Commit again.

### Checkpoint Command
```powershell
git add -A
git commit -m "checkpoint: stable before <feature-name>"
```

## 2. Quick Undo Options

### Undo last commit but keep files changed
```powershell
git reset --soft HEAD~1
```

### Undo last commit and unstage files (keep edits in working tree)
```powershell
git reset --mixed HEAD~1
```

### Restore a single file to last commit state
```powershell
git restore --source=HEAD -- cybersecurity_friend/app.py
```

### Restore specific file from an older commit
```powershell
git restore --source <commit-hash> -- cybersecurity_friend/rag_pipeline.py
```

### Revert a commit safely (best for shared branch)
```powershell
git revert <commit-hash>
```

## 3. Rollback by Feature Block

### Revert Hybrid RAG changes only
```powershell
git restore --source=HEAD -- \
  cybersecurity_friend/rag_pipeline.py \
  cybersecurity_friend/data_ingestion/fetch_hot_index_data.py \
  cybersecurity_friend/data_ingestion/fetch_warm_index_data.py \
  cybersecurity_friend/data_ingestion/rebuild_hybrid_index.py \
  cybersecurity_friend/config.py \
  cybersecurity_friend/assistant.py \
  README.md
```

### Revert UI sidebar compatibility changes only
```powershell
git restore --source=HEAD -- cybersecurity_friend/app.py
```

### Revert local Ollama provider integration only
```powershell
git restore --source=HEAD -- \
  cybersecurity_friend/config.py \
  cybersecurity_friend/assistant.py \
  cybersecurity_friend/api.py \
  cybersecurity_friend/main.py \
  cybersecurity_friend/requirements.txt \
  README.md
```

## 4. Emergency Snapshot Patch (No Commit Needed)
Use this when `git` is unavailable but you still want rollback safety.

```powershell
New-Item -ItemType Directory -Force .\backups | Out-Null
Copy-Item .\cybersecurity_friend\app.py .\backups\app.py.bak -Force
Copy-Item .\cybersecurity_friend\assistant.py .\backups\assistant.py.bak -Force
Copy-Item .\cybersecurity_friend\rag_pipeline.py .\backups\rag_pipeline.py.bak -Force
```

Restore later:
```powershell
Copy-Item .\backups\app.py.bak .\cybersecurity_friend\app.py -Force
Copy-Item .\backups\assistant.py.bak .\cybersecurity_friend\assistant.py -Force
Copy-Item .\backups\rag_pipeline.py.bak .\cybersecurity_friend\rag_pipeline.py -Force
```

## 5. Pre-Change Checklist
1. `PROJECT_LOG.txt` updated with current state.
2. Checkpoint created.
3. New edits scoped to one module.
4. Rollback command decided before edit.

## 6. Current Constraint
If shell shows `git`/`python` not found, install and add to PATH first.  
Without that, use backup-copy method from section 4.
