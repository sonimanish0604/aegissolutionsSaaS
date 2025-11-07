#!/usr/bin/env bash
set -euo pipefail

# Optional: pick a profile if you have multiple (aws configure list-profiles)
PROFILE="${AWS_PROFILE:-default}"  # change if needed

echo "Using AWS CLI profile: $PROFILE"
aws sts get-caller-identity --profile "$PROFILE"