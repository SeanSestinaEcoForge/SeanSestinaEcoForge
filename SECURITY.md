# Security Policy

Thank you for helping keep EcoForge and the broader community safe.

We take security seriously and appreciate responsible disclosure of vulnerabilities. This document outlines how to report security issues in this project and what to expect.

## Supported Versions

We actively maintain and provide security updates for the following versions:

| Version   | Supported          | Security Fixes Until |
|-----------|--------------------|----------------------|
| main      | Yes (latest)       | Ongoing              |
| v1.x      | Yes                | TBD                  |

Older versions or forks may not receive security updates. Please upgrade to the latest release or main branch.

## Reporting a Vulnerability

**Please do NOT report security vulnerabilities through public GitHub issues, pull requests, or discussions.**

Instead, use one of the following private channels:

1. **Preferred: GitHub Private Vulnerability Reporting** (enabled)  
   - Go to the [Security tab](https://github.com/SeanSestinaEcoForge/SeanSestinaEcoForge/security) of this repository.  
   - Click **Report a vulnerability** → GitHub's built-in private reporting tool.  
   - This creates a private security advisory visible only to repo maintainers.  
   - Recommended for most reports (fast, secure, tracked).

2. **Fallback if the Security tab form is unavailable:**  
   - No security email is published yet. Send a short DM to @SeanSestina on X asking for a private channel (no exploit details in the first message).  
   - Then share:  
     - Description of the vulnerability  
     - Steps to reproduce  
     - Potential impact  
     - Suggested fix (if you have one)  
     - Any proof-of-concept code or screenshots (please avoid sending exploits directly)

We will acknowledge receipt of your report within **48 hours** and strive to provide an initial assessment or update within **7 days**.

## What to Expect

- **Acknowledgment**: We will confirm receipt and thank you for your report.
- **Triage**: We will assess severity, reproduce the issue (if needed), and determine scope.
- **Fix & Disclosure**: We aim to fix valid issues as quickly as possible.  
  - Critical/high severity: immediate attention and coordinated disclosure.  
  - Moderate/low: included in next release or patch.
- **Credit**: With your permission, we will publicly credit you in the release notes, SECURITY.md, or a blog post when the issue is fixed and disclosed.
- **Safe Harbor**: We will not pursue legal action against anyone who reports in good faith following this policy.

## Security-Related Best Practices for Contributors

- Never commit secrets, keys, passwords, or sensitive data.
- Use `.gitignore` and secret scanning tools.
- Enable Dependabot alerts and review dependency vulnerabilities.
- Use pull requests (not direct pushes) to main.
- Report any suspicious activity immediately.

## In Scope

- Vulnerabilities in code owned by EcoForgeProject/EcoForge
- Issues in dependencies used directly by this project
- Security misconfigurations in provided documentation or examples

## Out of Scope

- Vulnerabilities in third-party dependencies not controlled by us
- Social engineering, phishing, or physical attacks
- Denial-of-service (DoS) or rate-limiting issues
- Issues requiring physical access to hardware
- Previously known public vulnerabilities

Thank you for helping make EcoForge safer for everyone building toward Earth abundance and Mars readiness.

Last updated: November 2026
