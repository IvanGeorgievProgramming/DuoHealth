<?php

require 'path/to/PHPMailer/src/PHPMailer.php';
require 'path/to/PHPMailer/src/SMTP.php';
require 'path/to/PHPMailer/src/Exception.php';

// Get the form data
echo "Hello from PHP!";
$name = $_POST['name'];
$email = $_POST['email'];
$password = $_POST['password'];
$subject = $_POST['subject'];
$message = $_POST['message'];

// Compose the email message
$to = 'duohealth5@gmail.com';
$subject = 'New message from ' . $name;
$body = "Name: $name\nEmail: $email\n\n$message";

// Send the email
$headers = 'From: ' . $email . "\r\n" .
            'Reply-To: ' . $email . "\r\n" .
            'X-Mailer: PHP/' . phpversion();

$mail = new PHPMailer;

// Enable SMTP debugging
// 0 = off, 1 = client messages, 2 = client and server messages
$mail->SMTPDebug = 0;

// Set the hostname of the mail server
$mail->Host = 'smtp.gmail.com';

// Use SMTP authentication
$mail->SMTPAuth = true;

// Set the SMTP port number - 587 for authenticated TLS, a.k.a. RFC4409 SMTP submission
$mail->Port = 587;

// Set the encryption system to use - ssl (deprecated) or tls
$mail->SMTPSecure = 'tls';

// Set the username and password to authenticate
$mail->Username = $email;
$mail->Password = $password;

// Set the "from" email address and name
$mail->setFrom($email, $name);

// Set the email subject and body
$mail->Subject = $subject;
$mail->Body = $message;

// Add recipients
$mail->addAddress('duohealth5@gmail.com');

// Send the email
if(!$mail->send()) {
    echo 'Message could not be sent.';
    echo 'Mailer Error: ' . $mail->ErrorInfo;
} else {
    echo 'Message has been sent';
}

// Redirect back to the contact page
header('Location: ../html/homePage.html');
exit;
?>
