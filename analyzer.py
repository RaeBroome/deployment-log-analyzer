import anthropic
import os
import sys
import json
from datetime import datetime

def read_log_file(filepath):
    """Read a log file and return its contents."""
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Log file not found at {filepath}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading log file: {e}")
        sys.exit(1)

def analyze_log(log_content):
    """Send log content to Claude for structured analysis."""
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    prompt = f"""You are a senior DevOps engineer analyzing a deployment log.

Analyze the following deployment log and respond ONLY with a valid JSON object. 
No preamble, no explanation, no markdown code blocks. Just the raw JSON object.

The JSON must follow this exact structure:
{{
    "deployment_status": "FAILED or SUCCESS",
    "summary": "one sentence summary of what happened",
    "failures": [
        {{
            "timestamp": "timestamp from log",
            "component": "which component failed",
            "error": "exact error message",
            "root_cause": "most likely root cause explanation",
            "recommended_action": "specific steps to resolve"
        }}
    ],
    "warnings": [
        {{
            "timestamp": "timestamp from log",
            "component": "which component warned",
            "message": "warning message",
            "recommendation": "what to do about it"
        }}
    ],
    "successes": [
        "brief description of what completed successfully"
    ],
    "safe_to_retry": true or false,
    "retry_instructions": "what must be done before retrying deployment"
}}

DEPLOYMENT LOG:
{log_content}"""

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return message.content[0].text

def save_report(analysis_json, log_path):
    """Save the analysis report to a timestamped file."""
    # Create reports directory if it doesn't exist
    os.makedirs("reports", exist_ok=True)

    # Build report filename from log name and timestamp
    log_name = os.path.splitext(os.path.basename(log_path))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"reports/{log_name}_{timestamp}.json"

    with open(report_path, 'w') as f:
        json.dump(analysis_json, f, indent=2)

    return report_path

def print_summary(analysis_json):
    """Print a clean human-readable summary to the console."""
    status = analysis_json.get("deployment_status", "UNKNOWN")
    summary = analysis_json.get("summary", "")
    failures = analysis_json.get("failures", [])
    warnings = analysis_json.get("warnings", [])
    safe = analysis_json.get("safe_to_retry", False)

    # One-line verdict
    failure_count = len(failures)
    warning_count = len(warnings)
    print(f"\n{'='*60}")
    print(f"STATUS: {status} — {failure_count} failure(s), {warning_count} warning(s)")
    print(f"{summary}")
    print(f"{'='*60}\n")

    # Failures
    if failures:
        print("FAILURES:")
        for f in failures:
            print(f"  [{f.get('timestamp', 'N/A')}] {f.get('component', 'Unknown')}")
            print(f"  Error: {f.get('error', '')}")
            print(f"  Root Cause: {f.get('root_cause', '')}")
            print(f"  Fix: {f.get('recommended_action', '')}")
            print()

    # Warnings
    if warnings:
        print("WARNINGS:")
        for w in warnings:
            print(f"  [{w.get('timestamp', 'N/A')}] {w.get('component', 'Unknown')}")
            print(f"  {w.get('message', '')}")
            print(f"  Recommendation: {w.get('recommendation', '')}")
            print()

    # Successes
    successes = analysis_json.get("successes", [])
    if successes:
        print("SUCCEEDED:")
        for s in successes:
            print(f"  ✓ {s}")
        print()

    # Retry guidance
    print(f"SAFE TO RETRY: {'YES' if safe else 'NO'}")
    if not safe:
        print(f"BEFORE RETRYING: {analysis_json.get('retry_instructions', '')}")
    print(f"{'='*60}\n")

def main():
    # Default to sample log if no argument provided
    if len(sys.argv) > 1:
        log_path = sys.argv[1]
    else:
        log_path = "samples/sample_deployment.log"

    print(f"Analyzing log: {log_path}")

    # Read and analyze
    log_content = read_log_file(log_path)
    raw_analysis = analyze_log(log_content)

    # Parse JSON response
    try:
            # Strip markdown code blocks if Claude wrapped the response
        cleaned = raw_analysis.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]  # Remove first line (```json)
            cleaned = cleaned.rsplit("```", 1)[0]  # Remove trailing ```
        analysis_json = json.loads(cleaned.strip())
    except json.JSONDecodeError:
        print("Error: Claude did not return valid JSON. Raw response:")
        print(raw_analysis)
        sys.exit(1)

    # Print human-readable summary
    print_summary(analysis_json)

    # Save full report
    report_path = save_report(analysis_json, log_path)
    print(f"Full report saved to: {report_path}")

if __name__ == "__main__":
    main()