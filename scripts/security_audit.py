import os
import re

def scan_files(directory):
    print(f"Scanning directory: {directory}")
    
    # Patterns to look for
    print_pattern = re.compile(r'print\(')
    secret_patterns = [
        re.compile(r'(sk_[a-zA-Z0-9]{20,})'), # generic secret key
        re.compile(r'(gsk_[a-zA-Z0-9]{20,})'), # groq
        # Add more logic to ignore .env or config files if needed
    ]
    
    vulnerabilities = []
    
    for root, _, files in os.walk(directory):
        for file in files:
            if not file.endswith(".py"):
                continue
                
            filepath = os.path.join(root, file)
            
            # Skip verify_db.py and scripts/ as they are tools not app code
            if "verify_db.py" in filepath or "scripts/" in filepath:
                continue

            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                    lines = content.splitlines()
                    
                    for i, line in enumerate(lines):
                        # Check for print()
                        if print_pattern.search(line) and not line.strip().startswith("#"):
                             vulnerabilities.append({
                                 "type": "Code Quality",
                                 "description": "Usage of print() detected (fails log redaction)",
                                 "file": filepath,
                                 "line": i + 1,
                                 "content": line.strip()
                             })
                        
                        # Check for Secrets (simple heuristic)
                        for pattern in secret_patterns:
                            if pattern.search(line) and "API_KEY" not in line and "os.getenv" not in line and "settings." not in line:
                                vulnerabilities.append({
                                     "type": "Security Risk",
                                     "description": "Potential hardcoded secret detected",
                                     "file": filepath,
                                     "line": i + 1,
                                     "content": "REDACTED"
                                 })
                                 
            except Exception as e:
                print(f"Could not scan {filepath}: {e}")

    return vulnerabilities

if __name__ == "__main__":
    vulnerabilities = scan_files("app")
    
    report = "# Automated Security Audit Report\n\n"
    if not vulnerabilities:
        report += "**Status**: passed ✅\n\nNo vulnerabilities found."
    else:
        report += "**Status**: failed ❌\n\nFound the following issues:\n"
        for v in vulnerabilities:
            report += f"- **{v['type']}**: {v['description']}\n"
            report += f"  - Location: `{v['file']}:{v['line']}`\n"
            if v['content'] != "REDACTED":
                report += f"  - Code: `{v['content']}`\n"
    
    # Write to artifact
    with open("AUDIT_REPORT.md", "w") as f:
        f.write(report)
        
    print("Audit Complete. Report generated at AUDIT_REPORT.md")
