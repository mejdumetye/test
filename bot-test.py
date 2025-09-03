import time
import os

def workflow_runs_for_repo_with_token(token: str, owner: str, repo: str, workflow_id: Optional[str]) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    # cache runs per repo+workflow+token briefly (short TTL) to avoid repeated calls during one /run_all
    cache_key = f"runs::{token[:8]}::{owner}::{repo}::{workflow_id or 'any'}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached  # (data, err)
    if workflow_id:
        url = f"{GITHUB_API}/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
    else:
        url = f"{GITHUB_API}/repos/{owner}/{repo}/actions/runs"
    status, data = safe_github_request("GET", url, token=token)
    if status == 200:
        cache.set(cache_key, (data, None), ttl=max(10, CACHE_TTL//10))
        return data, None
    if status == 404:
        cache.set(cache_key, (None, "not found"), ttl=max(10, CACHE_TTL//10))
        return None, "not found"
    if status == 0:
        cache.set(cache_key, (None, f"network: {data.get('error')}"), ttl=max(10, CACHE_TTL//10))
        return None, f"network: {data.get('error')}"
    cache.set(cache_key, (None, f"{status}: {data}"), ttl=max(10, CACHE_TTL//10))
    return None, f"{status}: {data}"
