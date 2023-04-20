<?php
// Get the form data
$name = $_POST['name'];
$email = $_POST['email'];
$phone = $_POST['phone'];
$subject = $_POST['subject'];
$message = $_POST['message'];

// Compose the email message
$to = 'duohealth5@gmail.com';
$subject = 'New message from ' . $name;
$body = "Name: $name\nEmail: $email\nPhone: $phone\n\n$message";

// Send the email
$headers = 'From: ' . $email . "\r\n" .
            'Reply-To: ' . $email . "\r\n" .
            'X-Mailer: PHP/' . phpversion();
mail($to, $subject, $body, $headers);

// Redirect back to the contact page
header('Location: index.html#contact');
exit;
?>