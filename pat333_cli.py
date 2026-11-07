"""
Pat333 Autonomous Fleet Controller (pat333-cli)
Master command-line interface and executive synchronization bus for the 7-repo ecosystem.
Governing Authority: Governing Officer Tarwater
"""

import os
import sys
import yaml
import base64
import argparse
import requests
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

GITHUB_API_URL = "https://api.github.com"

FLEET_REPOSITORIES = [
    "Pat333-ux/autonomous-governance-core",
    "Pat333-ux/autonomous-agent-swarm",
    "Pat333-ux/autonomous-sandbox-runner",
    "Pat333-ux/autonomous-memory-vault",
    "Pat333-ux/autonomous-command-center",
    "Pat333-ux/autonomous-dependency-warden",
    "Pat333-ux/autonomous-release-orchestrator"
]


def get_github_headers() -> dict:
    token = os.getenv("GH_PAT") or os.getenv("GITHUB_TOKEN")
    if not token:
        raise EnvironmentError("Missing GH_PAT or GITHUB_TOKEN environment variable.")
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }


def cmd_status() -> None:
    """Queries live health and open PR counts across all 7 repositories in the fleet."""
    headers = get_github_headers()
    logging.info("==================================================")
    logging.info(" 🛡️ PAT333 FLEET STATUS REPORT (Officer Tarwater)  ")
    logging.info("==================================================")

    for repo in FLEET_REPOSITORIES:
        url = f"{GITHUB_API_URL}/repos/{repo}"
        resp = requests.get(url, headers=headers, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            pr_resp = requests.get(f"{GITHUB_API_URL}/repos/{repo}/pulls", headers=headers, timeout=10)
            open_prs = len(pr_resp.json()) if pr_resp.status_code == 200 else 0
            
            stars = data.get("stargazers_count", 0)
            logging.info(f"🟢 [ONLINE] {repo} | Open PRs: {open_prs} | Stars: {stars}")
        else:
            logging.error(f"🔴 [OFFLINE/ERROR] {repo} (Status code: {resp.status_code})")
    
    logging.info("==================================================")


def cmd_patrol() -> None:
    """Triggers workflow dispatches across all repositories to force an immediate synchronized audit."""
    headers = get_github_headers()
    logging.info("Initiating synchronized fleet-wide patrol...")

    for repo in FLEET_REPOSITORIES:
        # Trigger workflow dispatch if a standard workflow exists
        url = f"{GITHUB_API_URL}/repos/{repo}/actions/workflows"
        resp = requests.get(url, headers=headers, timeout=10)
        
        if resp.status_code == 200:
            workflows = resp.json().get("workflows", [])
            if workflows:
                wf_id = workflows[0]["id"]
                dispatch_url = f"{GITHUB_API_URL}/repos/{repo}/actions/workflows/{wf_id}/dispatches"
                d_resp = requests.post(dispatch_url, headers=headers, json={"ref": "main"}, timeout=10)
                if d_resp.status_code == 204:
                    logging.info(f"Dispatched patrol workflow for {repo}")
                else:
                    logging.warning(f"Could not dispatch workflow for {repo}: {d_resp.status_code}")


def cmd_freeze(reason: str) -> None:
    """
    Instantly propagates the global emergency kill-switch to governance_config.yaml
    across all seven repositories, locking down the ecosystem simultaneously.
    """
    headers = get_github_headers()
    logging.critical(f"🚨 EMERGENCY FREEZE INITIATED BY TARWATER: {reason}")

    for repo in FLEET_REPOSITORIES:
        url = f"{GITHUB_API_URL}/repos/{repo}/contents/governance_config.yaml"
        resp = requests.get(url, headers=headers, timeout=10)
        
        if resp.status_code != 200:
            logging.warning(f"Skipping {repo} (governance_config.yaml not found).")
            continue

        file_data = resp.json()
        file_sha = file_data.get("sha")
        decoded_yaml = base64.b64decode(file_data["content"]).decode("utf-8")
        
        config = yaml.safe_load(decoded_yaml)
        if "communication_and_oversight" not in config:
            config["communication_and_oversight"] = {}
        if "emergency_override" not in config["communication_and_oversight"]:
            config["communication_and_oversight"]["emergency_override"] = {}

        config["communication_and_oversight"]["emergency_override"]["global_kill_switch"] = True
        config["communication_and_oversight"]["emergency_override"]["freeze_reason"] = reason

        updated_yaml = yaml.dump(config, sort_keys=False)
        
        commit_payload = {
            "message": f"[EMERGENCY-FREEZE] Master lockdown engaged: {reason}",
            "content": base64.b64encode(updated_yaml.encode("utf-8")).decode("utf-8"),
            "sha": file_sha
        }
        
        put_resp = requests.put(url, headers=headers, json=commit_payload, timeout=15)
        if put_resp.status_code in (200, 201):
            logging.info(f"LOCKED DOWN: {repo}")
        else:
            logging.error(f"Failed to lock down {repo}: {put_resp.text}")

    logging.critical("🚨 ECOSYSTEM-WIDE FREEZE COMPLETE. All autonomous operations halted.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pat333 Autonomous Fleet Controller (pat333-cli)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("status", help="Check live health across all 7 repositories")
    subparsers.add_parser("patrol", help="Trigger synchronized fleet-wide workflow audits")

    freeze_parser = subparsers.add_parser("freeze", help="Engage ecosystem-wide emergency kill switch")
    freeze_parser.add_argument("--reason", required=True, help="Reason for emergency lockdown")

    args = parser.parse_args()

    if args.command == "status":
        cmd_status()
    elif args.command == "patrol":
        cmd_patrol()
    elif args.command == "freeze":
        cmd_freeze(args.reason)
