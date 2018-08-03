<?php

  require 'vendor/autoload.php';

  $sendgrid_username = 'sendgrid username';
  $sendgrid_password = 'sendgrid email address';
 
  $sendgrid = new SendGrid($sendgrid_username, $sendgrid_password, array("turn_off_ssl_verification" => true));
  $email    = new SendGrid\Email();

  $_email   = '';
  $_message = '';

  if($_POST) {
    $GLOBALS['_email']   = $_POST['email'];
    $GLOBALS['_message'] = $_POST['message'];
  }
  if($_GET) {
    $GLOBALS['_email']   = $_GET['email'];
    $GLOBALS['_message'] = $_GET['message'];
  }

  $email->addTo($_email)
    ->setFrom('ImageCapturePy')
    ->setSubject("Location Captured!")
    ->setText($_message);

  $sendgrid->send($email);
?>
