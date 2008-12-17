<?php
$page = isset($_GET['page']) ? $_GET['page'] : '';
$select_page = preg_match('/^\\w+$/', $page) ? ":select $page" : '';

header('X-Powered-By: Lisp');
header('Content-Type: text/html; charset=UTF-8');
system("clisp -E UTF-8 -ansi -modern Web.lisp $select_page", $exit_status);

if ($exit_status <> 0) {
    include 'index.html';
}
?>