<?php

  require 'vendor/autoload.php';

  if($_POST) {
    $email   = new SendGrid\Email(null, $_POST['email']);
    $message = new SendGrid\Content("text/plain", $_POST['message']);
  }
  if($_GET) {
    $email   = new SendGrid\Email(null, $_POST['email']);
    $message = new SendGrid\Content("text/plain", $_POST['message']);
  }
  $mail   = new SendGrid\Mail('imagecapture', "Location data captured", $email, $message);
  $apiKey = getenv('SENDGRID_API_KEY');
  $sg = new \SendGrid($apiKey);

  $sg->client->mail()->send()->post($mail);
?>
