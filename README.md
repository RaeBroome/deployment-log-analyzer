# Deployment Log Analyzer

An AI-powered deployment log analyzer that uses the Anthropic Claude API to identify failures, surface root causes, and provide actionable remediation steps from complex deployment logs.

> Built from real-world enterprise DevOps experience in regulated government environments.

## Why This Exists

Deployment logs can span thousands of lines across parallel threads, multiple components, and simultaneous operations. When threads execute concurrently, their log entries interleave by timestamp — a critical failure from Thread 3 can be buried between progress messages from Threads 1 and 2, easy to miss under pressure during a live deployment window.

Finding the root cause manually means mentally reconstructing the execution sequence across interleaved thread output while the clock is ticking and websites are offline.

This tool feeds the log to Claude and returns a structured analysis in seconds — pulling failures out regardless of where they appear in the thread sequence, reconstructing what happened and in what order, and telling you exactly what to fix before retrying.

## What It Does

- Detects failures and warnings with exact timestamps and component names
- Identifies root cause for each failure
- Provides specific recommended actions to resolve each issue
- Summarizes what succeeded so you know what not to re-run
- Determines whether the deployment is safe to retry
- Saves a timestamped JSON report for audit trails

## Setup

### Prerequisites
- Python 3.x
- An Anthropic API key (get one at console.anthropic.com)

### Install Dependencies

```
pip install anthropic
```

### Configure Your API Key

This tool uses an OS-level environment variable for your API key — safer than a .env file since the key never touches your project filesystem.

**Windows:**
```
setx ANTHROPIC_API_KEY "your_key_here"
```
Close and reopen your terminal after running this so the variable takes effect.

**Mac/Linux:**
```
export ANTHROPIC_API_KEY="your_key_here"
```

## Usage

**Analyze the included sample log:**
```
python analyzer.py
```

**Analyze your own log file:**
```
python analyzer.py path/to/your/deployment.log
```

## Example Output

```
============================================================
STATUS: FAILED — 1 failure(s), 3 warning(s)
Deployment failed due to missing package source for AMS-ST1-Agency 
component, only 2 of 7 items deployed successfully before halting.
============================================================

FAILURES:
  [2026-02-28 18:04:35] AMS-ST1-Agency
  Error: Package source not found: C:\Projects\ST1-Deployment\ST1_02282026\Appl-Agency
  Root Cause: Deployment package missing or incorrectly named in package directory
  Fix: Verify Agency package exists with correct naming convention before retrying

WARNINGS:
  [2026-02-28 18:02:42] AmsTasksService
  Service did not stop within timeout — process forcibly killed (PID 7842)

SAFE TO RETRY: YES
============================================================
Full report saved to: reports/sample_deployment_20260514_102344.json
```

## Output Reports

Each analysis run saves a structured JSON report to the `reports/` folder with a timestamp. The JSON contains the full structured analysis including all failures, warnings, successes, and retry instructions — suitable for integration into other tooling or audit logging.

## Sample Log

A realistic sample deployment log is included at `samples/sample_deployment.log` representing a multi-threaded Azure DevOps deployment to a state government environment. The log demonstrates parallel deployment threads, service management, Azure backup integration, and a package source failure that halts deployment before database scripts run — protecting database integrity by design.

## Background

Built to demonstrate AI-assisted DevOps workflows — specifically the pattern of taking real engineering problems that currently require manual analysis and wrapping them in an AI layer that accelerates diagnosis and decision-making.

The sample log reflects real deployment patterns from enterprise government environments including parallel threading, Azure Recovery Services integration, and safe deployment sequencing — halting before database scripts on a failed code deployment because code rollback is a file copy while database rollback is a restore.

## Planned Improvements

- Support for multiple log formats (Azure DevOps, Jenkins, GitHub Actions)
- HTML report output for sharing with stakeholders
- Slack or Teams notification integration
- Batch analysis of multiple logs
- Trend analysis across deployment history