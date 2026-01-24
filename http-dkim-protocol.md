# The HTTP-DKIM Protocol

This document outlines a protocol used to deploy a file to the server.
The core idea is to leverage the DKIM protocol, originally invented in the context of email, on HTTP. Thi works because a HTTP header is identical to an email header.

## HTTP Request

The deployment is done via an HTTP POST request to the server.

### HTTP Headers

The following headers are required:

- `From`: The signing address (e.g., `user@example.com`). This is used to identify the sender.
The signing address (e.g., `user@example.com`). This is used to identify the sender and determine which DNS TXT record to query for the public key. The DNS record follows the format `<username>._domainkey.<domain>` (e.g., for `user@example.com`, the record would be `user._domainkey.example.com`).
The signing address (e.g., `user@example.com`). This is used to identify the sender and determine which DNS TXT record to query for the public key used to verify the DKIM signature.
- `DKIM-Signature`: The DKIM signature of the request body. The signature is calculated using the private key and the domain specified in the signing address.
- `Content-Type`: Must be `application/data`.
- `Content-Disposition`: Must be `attachment; filename="<file_name>"`, where `<file_name>` is the name of the file being deployed.

### Body

The body of the request must be the raw content of the file being deployed.

## HTTP Response

### Success

A successful deployment is indicated by an HTTP status code of `200 OK`.

### Failure

Any HTTP status code greater than or equal to `400` indicates a failed deployment. The response body may contain an error message.
