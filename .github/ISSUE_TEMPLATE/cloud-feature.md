on:
  issues:
    types: [labeled]

jobs:
  fanout:
    if: github.event.issue.labels.* contains 'cloud'
    runs-on: ubuntu-latest
    steps:
      - name: Create subtasks
        env:
          GH_TOKEN: ${{ secrets.PROJECT_AUTOMATION_TOKEN }}
        run: |
          for cloud in AWS GCP Azure; do
            gh issue create \
              --title "${{ github.event.issue.title }} – ${cloud}" \
              --body "Subtask for ${cloud}\nParent: #${{ github.event.issue.number }}" \
              --project "sonimanish0604/aegisSolutionsSaaS/XYZ" \
              --label "cloud-subtask";
          done