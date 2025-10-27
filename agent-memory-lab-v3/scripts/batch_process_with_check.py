#!/usr/bin/env python3
import sys
import json
import pathlib
import subprocess
import hashlib


import shutil

def run_q1_for_session(project_root: pathlib.Path, session_path: pathlib.Path, source_md_path: pathlib.Path) -> bool:
    """Run Q1 batch analysis, with self-healing for incompatible sessions."""
    summary_path = project_root / "data" / "2_runs" / session_path.name / "summary.json"
    if summary_path.exists():
        print(f"   ✅ [SKIPPING] Analysis already complete: {summary_path}")
        return True

    print(f"   ▶️  [ANALYZING] Running Q1 analysis for session: '{session_path.name}'")
    cmd = [
        sys.executable,
        "-m",
        "tools.run_q1_batch",
        str(session_path.resolve())
    ]
    try:
        result = subprocess.run(
            cmd,
            cwd=project_root,
            check=True,
            text=True,
            capture_output=True
        )
        print(f"   ✅ [SUCCESS] Q1 analysis completed for '{session_path.name}'.")
        return True
    except subprocess.CalledProcessError as e:
        # Self-healing logic for incompatible session structure
        if "goal.json not found" in e.stderr:
            print(f"   ⚠️  [AUTO-FIX] Incompatible session structure detected for '{session_path.name}'.")
            print(f"      - Deleting old session and re-processing from '{source_md_path.name}'...")
            shutil.rmtree(session_path)
            
            # Re-run preprocessing
            preprocess_cmd = [
                sys.executable, "-m", "tools.process_long_conversation", str(source_md_path.resolve())
            ]
            try:
                subprocess.run(preprocess_cmd, cwd=project_root, check=True, text=True, capture_output=True)
                print("      - ✅ Preprocessing complete. Now attempting analysis again...")
                
                # Find the new session path (most recently created)
                sessions_dir = project_root / "data" / "1_sessions"
                all_sessions = sorted(sessions_dir.iterdir(), key=lambda p: p.stat().st_ctime)
                if all_sessions:
                    new_session_path = all_sessions[-1]
                    return run_q1_for_session(project_root, new_session_path, source_md_path) # Recursive call
                else:
                    print("      - ❌ [ERROR] Could not find new session path after re-processing.")
                    return False
            except subprocess.CalledProcessError as e2:
                print(f"      - ❌ [ERROR] Re-processing failed for '{source_md_path.name}'.")
                print("         - Stderr:", e2.stderr)
                return False
        else:
            print(f"   ❌ [ERROR] Q1 analysis failed for '{session_path.name}'.")
            print("      - Stderr:", e.stderr)
            return False

def get_file_hash(path: pathlib.Path) -> str:
    """Calculates the MD5 hash of a file."""
    hasher = hashlib.md5()
    with open(path, "rb") as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def find_processed_sessions(sessions_dir: pathlib.Path) -> dict:
    """Finds all processed sessions and maps their original content hash to the session path."""
    processed_map = {}
    if not sessions_dir.exists():
        return processed_map

    for session_path in sessions_dir.iterdir():
        if not session_path.is_dir():
            continue
        
        raw_md_path = session_path / "raw" / "full_conversation.md"
        if raw_md_path.exists():
            file_hash = get_file_hash(raw_md_path)
            processed_map[file_hash] = session_path
            
    return processed_map

def main():
    """Main script to process markdown files in spot-test directory incrementally."""
    project_root = pathlib.Path(__file__).parent.parent
    spot_test_dir = project_root / "spot-test"
    sessions_dir = project_root / "data" / "1_sessions"

    print("🚀 Starting incremental processing of spot-test files...")
    print("-" * 60)

    # 1. Build a map of already processed files by their content hash
    processed_sessions = find_processed_sessions(sessions_dir)
    print(f"🔎 Found {len(processed_sessions)} existing processed sessions.")

    # 2. Get all markdown files to be processed
    md_files_to_process = sorted(spot_test_dir.glob("*.md"))
    if not md_files_to_process:
        print("🤷 No markdown files found in spot-test directory. Nothing to do.")
        return
        
    print(f"📂 Found {len(md_files_to_process)} markdown files to check in '{spot_test_dir.name}'.")
    print("-" * 60)

    # 3. Loop through and process
    for md_path in md_files_to_process:
        print(f"Checking '{md_path.name}'...")
        current_hash = get_file_hash(md_path)

        if current_hash in processed_sessions:
            session_path = processed_sessions[current_hash]
            print(f"⚠️  [SKIPPING] File content is identical to an existing session: '{session_path.name}'")
            # Pass the original md_path for potential self-healing
            run_q1_for_session(project_root, session_path, md_path)
        else:
            print(f"✨ [PROCESSING] Found new or modified file: '{md_path.name}'")
            cmd = [
                sys.executable,
                "-m",
                "tools.process_long_conversation",
                str(md_path.resolve())
            ]
            try:
                # We run from the project root to ensure all module paths are correct
                subprocess.run(
                    cmd,
                    cwd=project_root,
                    check=True,
                    text=True,
                    capture_output=True
                )
                print(f"✅ [SUCCESS] Finished processing '{md_path.name}'.")

                # Map the just-processed file to its session by hash, then run Q1
                # Refresh processed_sessions to include the new session
                processed_sessions = find_processed_sessions(sessions_dir)
                new_session_path = processed_sessions.get(current_hash)
                if new_session_path:
                    # Pass the original md_path for potential self-healing
                    run_q1_for_session(project_root, new_session_path, md_path)
                else:
                    print("   ⚠️  [WARN] Could not locate new session by hash; skip Q1.")
            except subprocess.CalledProcessError as e:
                print(f"❌ [ERROR] Failed to process '{md_path.name}'.")
                print("   - Stderr:", e.stderr)
                print("   - Stdout:", e.stdout)
        print("-" * 60)

    print("🎉 All files checked. Incremental processing complete.")

if __name__ == "__main__":
    main()
