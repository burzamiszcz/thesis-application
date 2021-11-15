<?php
require_once '_db.php';

$json = file_get_contents('php://input');
$params = json_decode($json);

$stmt = $db->prepare("UPDATE events SET event_start = :start, event_end = :end WHERE id = :id");
$stmt->bindParam(':id', $params->e->id);
$stmt->bindParam(':start', $params->newStart);
$stmt->bindParam(':end', $params->newEnd);
$stmt->execute();

class Result {}

$response = new Result();
$response->result = 'OK';
$response->message = 'Update successful';

echo json_encode($response);

