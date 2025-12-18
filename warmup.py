#!/usr/bin/env python3
"""
Email Warm-up Service
Gradually increases email sending volume to improve deliverability
"""

import os
import sys
import argparse
import json
import smtplib
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List
from dotenv import load_dotenv
import schedule

load_dotenv()

class EmailWarmupService:
    def __init__(self):
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        
        self.warmup_duration = int(os.getenv('WARMUP_DURATION_DAYS', 30))
        self.initial_volume = int(os.getenv('INITIAL_VOLUME', 5))
        self.target_volume = int(os.getenv('TARGET_VOLUME', 100))
        
        self.state_file = 'warmup_state.json'
        self.state = self.load_state()
    
    def load_state(self) -> Dict:
        """Load warm-up state from file"""
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {
            'started': False,
            'start_date': None,
            'current_day': 0,
            'emails_sent_today': 0,
            'total_emails_sent': 0,
            'paused': False
        }
    
    def save_state(self):
        """Save warm-up state to file"""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def calculate_daily_volume(self, day: int) -> int:
        """Calculate target emails for a specific day"""
        if day <= 0:
            return 0
        
        # Gradual increase curve
        progress = min(1.0, day / self.warmup_duration)
        
        # Exponential curve for gradual warm-up
        volume = self.initial_volume + (self.target_volume - self.initial_volume) * (progress ** 1.5)
        
        return int(volume)
    
    def get_warmup_recipients(self) -> List[str]:
        """Get list of warm-up email addresses"""
        # In production, these would be real warm-up service addresses
        # For now, return example addresses
        recipients_file = 'recipients.txt'
        if os.path.exists(recipients_file):
            with open(recipients_file, 'r') as f:
                return [line.strip() for line in f if line.strip() and '@' in line]
        
        # Default: return empty (user should add recipients)
        return []
    
    def send_warmup_email(self, recipient: str) -> bool:
        """Send a warm-up email"""
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.smtp_user
            msg['To'] = recipient
            msg['Subject'] = f"Warm-up email {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # Create email body
            text = f"""
            This is an automated warm-up email.
            
            Sent at: {datetime.now().isoformat()}
            Warm-up day: {self.state['current_day']}
            """
            
            html = f"""
            <html>
              <body>
                <p>This is an automated warm-up email.</p>
                <p><strong>Sent at:</strong> {datetime.now().isoformat()}</p>
                <p><strong>Warm-up day:</strong> {self.state['current_day']}</p>
              </body>
            </html>
            """
            
            part1 = MIMEText(text, 'plain')
            part2 = MIMEText(html, 'html')
            
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            return True
        except Exception as e:
            print(f"❌ Error sending email to {recipient}: {e}")
            return False
    
    def run_daily_warmup(self):
        """Run daily warm-up routine"""
        if self.state['paused']:
            return
        
        if not self.state['started']:
            print("⚠️  Warm-up not started. Use --start to begin.")
            return
        
        # Calculate current day
        if self.state['start_date']:
            start_date = datetime.fromisoformat(self.state['start_date'])
            current_day = (datetime.now() - start_date).days + 1
            self.state['current_day'] = current_day
        else:
            current_day = self.state['current_day']
        
        # Check if warm-up period is complete
        if current_day > self.warmup_duration:
            print(f"✅ Warm-up complete! Reached {self.warmup_duration} days.")
            self.state['paused'] = True
            self.save_state()
            return
        
        # Calculate target volume for today
        target_volume = self.calculate_daily_volume(current_day)
        emails_sent_today = self.state.get('emails_sent_today', 0)
        
        # Reset daily counter if new day
        last_reset = self.state.get('last_reset_date')
        today = datetime.now().date().isoformat()
        if last_reset != today:
            emails_sent_today = 0
            self.state['last_reset_date'] = today
        
        # Send emails if needed
        remaining = target_volume - emails_sent_today
        if remaining > 0:
            recipients = self.get_warmup_recipients()
            if not recipients:
                print("⚠️  No recipients configured. Add email addresses to recipients.txt")
                return
            
            print(f"📧 Sending {min(remaining, len(recipients))} warm-up emails (Day {current_day}/{self.warmup_duration})...")
            
            sent_count = 0
            for recipient in recipients[:remaining]:
                if self.send_warmup_email(recipient):
                    sent_count += 1
                    time.sleep(2)  # Rate limiting
            
            self.state['emails_sent_today'] = emails_sent_today + sent_count
            self.state['total_emails_sent'] = self.state.get('total_emails_sent', 0) + sent_count
            self.save_state()
            
            print(f"✅ Sent {sent_count} emails. Total today: {self.state['emails_sent_today']}/{target_volume}")
        else:
            print(f"✓ Daily quota reached ({target_volume} emails)")
    
    def start(self):
        """Start warm-up process"""
        if self.state['started']:
            print("⚠️  Warm-up already started")
            return
        
        self.state['started'] = True
        self.state['start_date'] = datetime.now().isoformat()
        self.state['current_day'] = 1
        self.state['paused'] = False
        self.save_state()
        
        print("🚀 Email warm-up started!")
        print(f"   Duration: {self.warmup_duration} days")
        print(f"   Initial volume: {self.initial_volume} emails/day")
        print(f"   Target volume: {self.target_volume} emails/day")
        
        # Run initial warm-up
        self.run_daily_warmup()
    
    def pause(self):
        """Pause warm-up"""
        self.state['paused'] = True
        self.save_state()
        print("⏸️  Warm-up paused")
    
    def resume(self):
        """Resume warm-up"""
        if not self.state['started']:
            print("⚠️  Warm-up not started. Use --start to begin.")
            return
        
        self.state['paused'] = False
        self.save_state()
        print("▶️  Warm-up resumed")
    
    def status(self):
        """Show warm-up status"""
        if not self.state['started']:
            print("⚠️  Warm-up not started")
            return
        
        current_day = self.state['current_day']
        target_volume = self.calculate_daily_volume(current_day)
        emails_sent_today = self.state.get('emails_sent_today', 0)
        total_sent = self.state.get('total_emails_sent', 0)
        progress = (current_day / self.warmup_duration) * 100
        
        print("="*60)
        print("EMAIL WARM-UP STATUS")
        print("="*60)
        print(f"Status: {'⏸️  Paused' if self.state['paused'] else '▶️  Active'}")
        print(f"Day: {current_day}/{self.warmup_duration} ({progress:.1f}%)")
        print(f"Emails sent today: {emails_sent_today}/{target_volume}")
        print(f"Total emails sent: {total_sent}")
        print(f"Target volume today: {target_volume} emails")
        
        if self.state['start_date']:
            start_date = datetime.fromisoformat(self.state['start_date'])
            days_elapsed = (datetime.now() - start_date).days
            print(f"Started: {start_date.strftime('%Y-%m-%d')} ({days_elapsed} days ago)")
    
    def run_continuous(self):
        """Run warm-up continuously with scheduled checks"""
        print("🚀 Starting continuous warm-up service...")
        
        # Schedule daily warm-up
        schedule.every().day.at("09:00").do(self.run_daily_warmup)
        
        # Also run immediately
        self.run_daily_warmup()
        
        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(60)


def main():
    parser = argparse.ArgumentParser(description='Email Warm-up Service')
    parser.add_argument('--start', action='store_true', help='Start warm-up')
    parser.add_argument('--pause', action='store_true', help='Pause warm-up')
    parser.add_argument('--resume', action='store_true', help='Resume warm-up')
    parser.add_argument('--status', action='store_true', help='Show status')
    parser.add_argument('--run', action='store_true', help='Run warm-up once')
    parser.add_argument('--continuous', action='store_true', help='Run continuously')
    
    args = parser.parse_args()
    
    if not os.getenv('SMTP_USER') or not os.getenv('SMTP_PASSWORD'):
        print("❌ SMTP_USER and SMTP_PASSWORD must be set in .env file")
        sys.exit(1)
    
    service = EmailWarmupService()
    
    if args.start:
        service.start()
    elif args.pause:
        service.pause()
    elif args.resume:
        service.resume()
    elif args.status:
        service.status()
    elif args.run:
        service.run_daily_warmup()
    elif args.continuous:
        service.run_continuous()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()


