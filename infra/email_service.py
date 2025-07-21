"""Email service for sending OCCP constraint notifications."""

import os
import smtplib
from typing import List
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from core.base import EmailSender
from core.errors import ExternalServiceError

class EmailService(EmailSender):
    """Service for sending emails with attachments."""
    
    def __init__(self, smtp_gateway: str, smtp_port: int, email_from: str, email_password: str):
        """
        Initialize the email service.
        
        Args:
            smtp_gateway: SMTP server address
            smtp_port: SMTP server port
            email_from: Sender email address
            email_password: Sender email password
        """
        self.smtp_gateway = smtp_gateway
        self.smtp_port = smtp_port
        self.email_from = email_from
        self.email_password = email_password
    
    def send(self, subject: str, body: str, recipients: List[str], 
             attachment_bytes: bytes, filename: str) -> None:
        """
        Send email with attachment.
        
        Args:
            subject: Email subject
            body: Email body (HTML format)
            recipients: List of recipient email addresses
            attachment_bytes: Attachment file as bytes
            filename: Name of the attachment file
            
        Raises:
            ExternalServiceError: If email sending fails
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg["Subject"] = subject
            msg["From"] = self.email_from
            msg["To"] = ", ".join(recipients)
            
            # Add HTML body
            part = MIMEText(body, "html")
            msg.attach(part)
            
            # Add attachment
            attachment = MIMEBase(
                "application",
                "vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            attachment.set_payload(attachment_bytes)
            encoders.encode_base64(attachment)
            attachment.add_header(
                "Content-Disposition",
                "attachment",
                filename=filename,
            )
            msg.attach(attachment)
            
            # Send email
            mailserver = smtplib.SMTP(host=self.smtp_gateway, port=self.smtp_port)
            mailserver.starttls()
            mailserver.ehlo()
            mailserver.login(user=self.email_from, password=self.email_password)
            mailserver.sendmail(self.email_from, recipients, msg.as_string())
            mailserver.close()
            
        except Exception as e:
            raise ExternalServiceError(f"Failed to send email: {e}")
    
    def format_email_subject(self, country: str, brands: List[str]) -> str:
        """
        Format email subject based on country and brands.
        
        Args:
            country: Country name
            brands: List of brand names
            
        Returns:
            Formatted email subject
        """
        if len(brands) == 1:
            return f"Business Constraints Submission for Review | {country}, {brands[0]}"
        else:
            brands_str = ", ".join(brands)
            return f"Business Constraints Submission for Review | {country} | {brands_str}"
    
    def format_email_body(self, country: str, brands: List[str], 
                         sales_line: str, cycle_name: str) -> str:
        """
        Format email body with OCCP constraint details.
        
        Args:
            country: Country name
            brands: List of brand names
            sales_line: Sales line name
            cycle_name: Cycle name
            
        Returns:
            Formatted HTML email body
        """
        if len(brands) == 1:
            brand_info = f"<li>Brand : <b>{brands[0]}</b> </li>"
        else:
            brands_str = ", ".join(brands)
            brand_info = f"<li>Brands : <b>{brands_str}</b> </li>"
        
        return f"""<html>
            <head></head>
            <body>
            <h5><span lang=EN style='font-family:"Noto Sans",sans-serif;mso-fareast-font-family:"Times New Roman";color:#000000;mso-ansi-language:EN;font-weight:normal'>
            Hi,<br><br>
            We would like to inform you that a user has submitted the business constraints for the following details:
            <ul>
            <li>Country : <b>{country}</b> </li> 
            {brand_info}
            <li>Sales Line : <b>{sales_line}</b> </li>
            <li>Cycle Name : <b>{cycle_name}</b> </li>
            </ul>
            <br>
            Please find the attached Excel file containing the detailed constraints submitted through the OCCP Business Constraints Tool for your review.
            <br><br>
            Thank you for your attention to this matter.
            <br><br>
            Regards,
            <br>
            OCCP Business Constraints Tool
            <o:p></o:p></span></h5></body></html>""" 