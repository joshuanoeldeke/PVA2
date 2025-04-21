import os
import json
import subprocess
from pathlib import Path
import shutil
import argparse


def prepare_migration_suites(dataset_path, output_root, clone_root):
    dataset_path = Path(dataset_path)
    output_root = Path(output_root)
    clone_root = Path(clone_root)
    clone_root.mkdir(parents=True, exist_ok=True)
    output_root.mkdir(parents=True, exist_ok=True)

    for project_dir in dataset_path.iterdir():
        if not project_dir.is_dir():
            continue
        for mig_dir in sorted(project_dir.iterdir()):
            diff_dir = mig_dir / 'diff'
            info_file = mig_dir / 'output.info'
            if not diff_dir.exists() or not info_file.exists():
                continue
            # parse migration info by manually constructing a JSON object
            try:
                raw = info_file.read_text()
                lines = []
                for ln in raw.splitlines():
                    ln = ln.strip().rstrip(',')
                    if not ln or ':' not in ln:
                        continue
                    key, val = ln.split(':', 1)
                    key = key.strip()
                    val = val.strip()
                    # treat empty/missing values as null
                    if not val:
                        val = 'null'
                    lines.append(f"{key}: {val}")
                json_str = '{' + ','.join(lines) + '}'
                info = json.loads(json_str)
            except Exception as e:
                print(f"Warning: could not parse output.info in {mig_dir}, skipping: {e}")
                print(f"Raw content:\n{raw}")
                continue
            commit_hash = info['commit_hash']
            commit_link = info['commit_link']
            project_name = project_dir.name
            mig_id = mig_dir.name
            suite_name_before = f"{project_name}_{mig_id}_before"
            suite_name_after = f"{project_name}_{mig_id}_after"
            out_before = output_root / suite_name_before
            out_after = output_root / suite_name_after
            # clone repo shallowly and fetch only the target commit
            repo_url = commit_link.split('/commit/')[0] + '.git'
            local_repo = clone_root / project_name
            if not local_repo.exists():
                print(f"Shallow cloning {repo_url} without full history...")
                try:
                    # clone with no checkout and minimal history
                    subprocess.run([
                        "git", "clone", "--depth", "1", "--no-checkout",
                        repo_url, str(local_repo)
                    ], check=True)
                    # fetch the specific migration commit
                    subprocess.run([
                        "git", "-C", str(local_repo), "fetch",
                        "--depth", "1", "origin", commit_hash
                    ], check=True)
                    # check out the commit
                    subprocess.run([
                        "git", "-C", str(local_repo), "checkout", commit_hash
                    ], check=True)
                except subprocess.CalledProcessError:
                    print(f"Warning: failed to shallow clone {project_name}, skipping this project.")
                    continue
            # export before state (parent commit)
            parent_hash = commit_hash + '^'
            for state, out_dir, label in [
                (parent_hash, out_before, 'unittest'),
                (commit_hash, out_after, 'pytest')
            ]:
                print(f"Exporting {project_name}@{state} to {out_dir}...")
                if out_dir.exists():
                    shutil.rmtree(out_dir)
                out_dir.mkdir()
                subprocess.run([
                    "git", "-C", str(local_repo), "archive", state
                ], stdout=subprocess.PIPE, check=True)
                # extract archive stream
                proc = subprocess.Popen([
                    "tar", "-x", "-C", str(out_dir)
                ], stdin=subprocess.PIPE)
                proc.stdin.write(subprocess.run([
                    "git", "-C", str(local_repo), "archive", state
                ], stdout=subprocess.PIPE).stdout)
                proc.stdin.close()
                proc.wait()
                # copy test file from diff and rename
                suffix = 'before' if label == 'unittest' else 'after'
                diff_pattern = f"*-{suffix}-*.py"
                files = list(diff_dir.glob(diff_pattern))
                if files:
                    test_src = files[0]
                    test_dest = out_dir / f"test_{suite_name_before if label=='unittest' else suite_name_after}_{label}.py"
                    shutil.copy(test_src, test_dest)
    print("Preparation complete.")


def main():
    parser = argparse.ArgumentParser(description="Prepare migration suite directories from TestMigrationsInPy")
    parser.add_argument("--dataset-path", default="datasets/TestMigrationsInPy-main/projects/", help="Path to TestMigrationsInPy projects folder")
    parser.add_argument("--output-dir", default="migration_suites", help="Where to output prepared suite folders")
    parser.add_argument("--clone-dir", default=".repos", help="Where to clone repositories")
    args = parser.parse_args()
    prepare_migration_suites(args.dataset_path, args.output_dir, args.clone_dir)

if __name__ == "__main__":
    main()