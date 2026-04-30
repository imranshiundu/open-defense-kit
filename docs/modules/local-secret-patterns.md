# Local Secret Pattern Review

## Purpose

This module scans local files you own for common secret-like patterns.

It is defensive and local-only. It does not send file contents to any external service.

## Risk level

Low.

## Network activity

None.

## Safe use

Use this on:

- your own project folder
- your own `.env.example` files
- your own documentation
- local test repositories

## Unsafe use

Do not use this to search other people's files, private machines, shared drives, or systems where you do not have permission.

## Command

```bash
odkit scan-secrets ./my-project
```

## Notes

This module uses pattern matching only. It can produce false positives and false negatives. Every finding must be manually reviewed.

The output redacts long lines to reduce accidental exposure in terminal logs.
