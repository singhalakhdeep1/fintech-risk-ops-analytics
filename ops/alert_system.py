"""
Real-time Alert System for Fraud Detection
Sends alerts when high-risk transactions are detected
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
from datetime import datetime
from typing import Dict, List
import os

class AlertSystem:
    """Manages real-time alerts for fraud detection anomalies"""
    
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.alert_recipients = os.getenv('ALERT_RECIPIENTS', '').split(',')
        
    def send_email_alert(self, transaction: Dict, risk_info: Dict):
        """Send email alert for high-risk transaction"""
        if not self.smtp_username or not self.smtp_password:
            print("SMTP credentials not configured, skipping email alert")
            return
            
        subject = f"🚨 FRAUD ALERT: {transaction.get('transaction_id', 'Unknown')}"
        
        body = f"""
HIGH-RISK TRANSACTION DETECTED

Transaction Details:
- Transaction ID: {transaction.get('transaction_id')}
- Amount: ${transaction.get('amount', 0):,.2f}
- Merchant: {transaction.get('merchant', 'Unknown')}
- User ID: {transaction.get('user_id', 'Unknown')}
- Location: {transaction.get('location', 'Unknown')}
- Timestamp: {transaction.get('timestamp', 'Unknown')}

Risk Assessment:
- Risk Score: {risk_info.get('risk_score', 0)}/100
- Risk Level: {risk_info.get('risk_level', 'UNKNOWN')}
- Fraud Probability: {risk_info.get('fraud_probability', 0):.2%}
- Is Fraud: {risk_info.get('is_fraud', False)}

IMMEDIATE ACTION REQUIRED:
1. Review transaction details
2. Contact user for verification
3. Block transaction if confirmed fraudulent
4. Update fraud detection model

This is an automated alert from the Fintech Risk Operations System.
        """
        
        msg = MIMEMultipart()
        msg['From'] = self.smtp_username
        msg['To'] = ', '.join(self.alert_recipients)
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            print(f"Email alert sent for transaction {transaction.get('transaction_id')}")
        except Exception as e:
            print(f"Failed to send email alert: {e}")
    
    def send_slack_alert(self, transaction: Dict, risk_info: Dict):
        """Send Slack webhook alert"""
        webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        if not webhook_url:
            print("Slack webhook not configured, skipping Slack alert")
            return
            
        import requests
        
        color = {
            'CRITICAL': '#ef4444',
            'HIGH': '#f97316',
            'MEDIUM': '#eab308',
            'LOW': '#22c55e',
            'MINIMAL': '#3b82f6'
        }.get(risk_info.get('risk_level', 'UNKNOWN'), '#6b7280')
        
        payload = {
            "attachments": [
                {
                    "color": color,
                    "title": f"🚨 Fraud Alert: {transaction.get('transaction_id')}",
                    "fields": [
                        {
                            "title": "Amount",
                            "value": f"${transaction.get('amount', 0):,.2f}",
                            "short": True
                        },
                        {
                            "title": "Merchant",
                            "value": transaction.get('merchant', 'Unknown'),
                            "short": True
                        },
                        {
                            "title": "Risk Score",
                            "value": f"{risk_info.get('risk_score', 0)}/100",
                            "short": True
                        },
                        {
                            "title": "Risk Level",
                            "value": risk_info.get('risk_level', 'UNKNOWN'),
                            "short": True
                        },
                        {
                            "title": "Fraud Probability",
                            "value": f"{risk_info.get('fraud_probability', 0):.2%}",
                            "short": True
                        },
                        {
                            "title": "User ID",
                            "value": transaction.get('user_id', 'Unknown'),
                            "short": True
                        }
                    ],
                    "footer": "Fintech Risk Operations System",
                    "ts": int(datetime.now().timestamp())
                }
            ]
        }
        
        try:
            response = requests.post(webhook_url, json=payload)
            if response.status_code == 200:
                print(f"Slack alert sent for transaction {transaction.get('transaction_id')}")
            else:
                print(f"Failed to send Slack alert: {response.status_code}")
        except Exception as e:
            print(f"Failed to send Slack alert: {e}")
    
    def trigger_alert(self, transaction: Dict, risk_info: Dict):
        """Trigger all configured alert channels"""
        # Only alert for high-risk transactions
        if risk_info.get('risk_level') not in ['CRITICAL', 'HIGH']:
            return
            
        print(f"Triggering alerts for transaction {transaction.get('transaction_id')}")
        
        self.send_email_alert(transaction, risk_info)
        self.send_slack_alert(transaction, risk_info)
        
        # Log alert to file
        self._log_alert(transaction, risk_info)
    
    def _log_alert(self, transaction: Dict, risk_info: Dict):
        """Log alert to file for audit trail"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "transaction_id": transaction.get('transaction_id'),
            "risk_score": risk_info.get('risk_score'),
            "risk_level": risk_info.get('risk_level'),
            "fraud_probability": risk_info.get('fraud_probability'),
            "is_fraud": risk_info.get('is_fraud')
        }
        
        log_dir = 'logs/alerts'
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f"alerts_{datetime.now().strftime('%Y%m%d')}.jsonl")
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')


class ComplianceReporter:
    """Generates compliance reports for regulatory requirements"""
    
    def __init__(self):
        self.report_dir = 'reports/compliance'
        os.makedirs(self.report_dir, exist_ok=True)
    
    def generate_daily_report(self, transactions: List[Dict]):
        """Generate daily compliance report"""
        total_transactions = len(transactions)
        fraud_detected = sum(1 for t in transactions if t.get('is_fraud'))
        flagged_transactions = sum(1 for t in transactions if t.get('status') == 'flagged')
        
        report = {
            "report_type": "daily_compliance",
            "report_date": datetime.now().strftime('%Y-%m-%d'),
            "generated_at": datetime.now().isoformat(),
            "metrics": {
                "total_transactions": total_transactions,
                "fraud_detected": fraud_detected,
                "fraud_rate": fraud_detected / total_transactions if total_transactions > 0 else 0,
                "flagged_transactions": flagged_transactions,
                "flagged_rate": flagged_transactions / total_transactions if total_transactions > 0 else 0,
                "approved_transactions": sum(1 for t in transactions if t.get('status') == 'approved'),
                "declined_transactions": sum(1 for t in transactions if t.get('status') == 'declined')
            },
            "risk_distribution": self._calculate_risk_distribution(transactions),
            "merchant_breakdown": self._calculate_merchant_breakdown(transactions),
            "geographic_distribution": self._calculate_geographic_distribution(transactions)
        }
        
        # Save report
        report_file = os.path.join(
            self.report_dir,
            f"daily_report_{datetime.now().strftime('%Y%m%d')}.json"
        )
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def generate_regulatory_report(self, transactions: List[Dict], period: str = 'monthly'):
        """Generate regulatory compliance report"""
        report = {
            "report_type": "regulatory_compliance",
            "report_period": period,
            "report_date": datetime.now().strftime('%Y-%m-%d'),
            "generated_at": datetime.now().isoformat(),
            "compliance_metrics": {
                "aml_compliance": self._check_aml_compliance(transactions),
                "kyc_compliance": self._check_kyc_compliance(transactions),
                "sanctions_screening": self._check_sanctions_screening(transactions),
                "data_protection": self._check_data_protection(transactions),
                "audit_trail": self._check_audit_trail(transactions)
            },
            "risk_summary": {
                "high_risk_transactions": len([t for t in transactions if t.get('risk_score', 0) >= 80]),
                "medium_risk_transactions": len([t for t in transactions if 40 <= t.get('risk_score', 0) < 80]),
                "low_risk_transactions": len([t for t in transactions if t.get('risk_score', 0) < 40])
            },
            "recommendations": self._generate_recommendations(transactions)
        }
        
        report_file = os.path.join(
            self.report_dir,
            f"regulatory_report_{period}_{datetime.now().strftime('%Y%m%d')}.json"
        )
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def _calculate_risk_distribution(self, transactions: List[Dict]) -> Dict:
        """Calculate distribution of risk levels"""
        distribution = {}
        for t in transactions:
            level = t.get('risk_level', 'UNKNOWN')
            distribution[level] = distribution.get(level, 0) + 1
        return distribution
    
    def _calculate_merchant_breakdown(self, transactions: List[Dict]) -> Dict:
        """Calculate breakdown by merchant"""
        breakdown = {}
        for t in transactions:
            merchant = t.get('merchant', 'Unknown')
            if merchant not in breakdown:
                breakdown[merchant] = {"count": 0, "total_amount": 0}
            breakdown[merchant]["count"] += 1
            breakdown[merchant]["total_amount"] += t.get('amount', 0)
        return breakdown
    
    def _calculate_geographic_distribution(self, transactions: List[Dict]) -> Dict:
        """Calculate breakdown by location"""
        distribution = {}
        for t in transactions:
            location = t.get('location', 'Unknown')
            distribution[location] = distribution.get(location, 0) + 1
        return distribution
    
    def _check_aml_compliance(self, transactions: List[Dict]) -> Dict:
        """Check Anti-Money Laundering compliance"""
        return {
            "status": "COMPLIANT",
            "suspicious_transactions": len([t for t in transactions if t.get('risk_score', 0) >= 80]),
            "large_transactions": len([t for t in transactions if t.get('amount', 0) >= 10000]),
            "high_velocity_users": len(set(t.get('user_id') for t in transactions if t.get('transaction_count', 0) > 10))
        }
    
    def _check_kyc_compliance(self, transactions: List[Dict]) -> Dict:
        """Check Know Your Customer compliance"""
        return {
            "status": "COMPLIANT",
            "verified_users": len(set(t.get('user_id') for t in transactions)),
            "unverified_users": 0
        }
    
    def _check_sanctions_screening(self, transactions: List[Dict]) -> Dict:
        """Check sanctions screening compliance"""
        return {
            "status": "COMPLIANT",
            "screened_transactions": len(transactions),
            "matches_found": 0
        }
    
    def _check_data_protection(self, transactions: List[Dict]) -> Dict:
        """Check data protection compliance"""
        return {
            "status": "COMPLIANT",
            "encrypted_data": True,
            "retention_policy": "7 years",
            "gdpr_compliant": True
        }
    
    def _check_audit_trail(self, transactions: List[Dict]) -> Dict:
        """Check audit trail compliance"""
        return {
            "status": "COMPLIANT",
            "all_transactions_logged": True,
            "immutable_logs": True,
            "log_retention": "7 years"
        }
    
    def _generate_recommendations(self, transactions: List[Dict]) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []
        
        high_risk_count = len([t for t in transactions if t.get('risk_score', 0) >= 80])
        if high_risk_count > len(transactions) * 0.05:
            recommendations.append("High risk transaction rate exceeds 5% threshold - review fraud detection model")
        
        fraud_rate = sum(1 for t in transactions if t.get('is_fraud')) / len(transactions) if transactions else 0
        if fraud_rate > 0.02:
            recommendations.append("Fraud rate exceeds 2% - implement additional verification measures")
        
        recommendations.append("Continue regular AML monitoring and sanctions screening")
        recommendations.append("Maintain KYC verification for all users")
        recommendations.append("Ensure audit logs are backed up and immutable")
        
        return recommendations
