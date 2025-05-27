#!/bin/sh

set -e

fastapi run --proxy-headers --host 0.0.0.0 --port 8000
