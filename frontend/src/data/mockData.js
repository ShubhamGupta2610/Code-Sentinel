export const vulnerabilityData = [
  { name: "SQL Injection", value: 35 },
  { name: "XSS", value: 25 },
  { name: "Authentication", value: 20 },
  { name: "SSRF", value: 10 },
  { name: "Others", value: 10 }
];

export const healthData = [
  {
    metric: "Security",
    score: 92
  },
  {
    metric: "Code Quality",
    score: 88
  },
  {
    metric: "Maintainability",
    score: 85
  },
  {
    metric: "Documentation",
    score: 76
  }
];

export const findingsData = [
  {
    file: "auth.py",
    issue: "SQL Injection",
    severity: "Critical",
    confidence: 96,
    reason: "User input is directly concatenated into SQL query.",
    risk: "Attackers can access or modify database records.",
    fix: "Use parameterized queries."
  },
  {
    file: "login.py",
    issue: "Cross Site Scripting",
    severity: "High",
    confidence: 91,
    reason: "Unsanitized user content rendered in HTML.",
    risk: "Malicious JavaScript execution.",
    fix: "Escape and sanitize user input."
  },
  {
    file: "admin.py",
    issue: "Broken Authentication",
    severity: "Medium",
    confidence: 87
  },
  {
    file: "payment.py",
    issue: "Hardcoded Secret",
    severity: "High",
    confidence: 94
  }
  
];

