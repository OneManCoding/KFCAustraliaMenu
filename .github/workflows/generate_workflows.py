import os

# Define the template for the GitHub Actions workflow
workflow_template = """name: Run main.py script for {store_numbers}

on:
  workflow_dispatch:

jobs:
  run-script:
    runs-on: ubuntu-latest-m

    steps:
    - name: Checkout code
      uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install aiofiles asyncio aiohttp requests logging jq
        RANDOM_SLEEP_TIME=$((RANDOM % 46 + 15))
        echo "Sleeping for $RANDOM_SLEEP_TIME seconds..."
        sleep $RANDOM_SLEEP_TIME

    - name: Run the store_info.py script
      run: |
        python store_info.py
        RANDOM_SLEEP_TIME=$((RANDOM % 46 + 15))
        echo "Sleeping for $RANDOM_SLEEP_TIME seconds..."
        sleep $RANDOM_SLEEP_TIME

    - name: Run the main.py script
      run: |
        python main.py {store_numbers}
        RANDOM_SLEEP_TIME=$((RANDOM % 46 + 15))
        echo "Sleeping for $RANDOM_SLEEP_TIME seconds..."
        sleep $RANDOM_SLEEP_TIME

    - name: Try to pull latest changes and stash
      id: git_pull
      continue-on-error: true
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git pull origin main
        RANDOM_SLEEP_TIME=$((RANDOM % 46 + 15))
        echo "Sleeping for $RANDOM_SLEEP_TIME seconds..."
        sleep $RANDOM_SLEEP_TIME

    - name: Wait for lock to be released
      run: |
        while [ -f .gitlock ]; do
          echo "Waiting for lock to be released..."
          git pull
          RANDOM_SLEEP_TIME=$((RANDOM % 46 + 15))
          echo "Sleeping for $RANDOM_SLEEP_TIME seconds..."
          sleep $RANDOM_SLEEP_TIME
        done

    - name: Acquire lock
      run: |
        echo "Acquiring lock..."
        git pull
        echo "Locked by $GITHUB_RUN_ID" > .gitlock
        git add .gitlock
        git commit -m "Acquiring lock by run $GITHUB_RUN_ID"
        git pull
        RANDOM_SLEEP_TIME=$((RANDOM % 46 + 15))
        echo "Sleeping for $RANDOM_SLEEP_TIME seconds..."
        sleep $RANDOM_SLEEP_TIME
        git push origin main

    - name: Commit and push changes
      run: |
        git pull
        git add .
        git commit -m "Updated store menu for {store_numbers} as of $(date -u +'%Y-%m-%d %H:%M:%S UTC')"
        git push origin main
        RANDOM_SLEEP_TIME=$((RANDOM % 46 + 15))
        echo "Sleeping for $RANDOM_SLEEP_TIME seconds..."
        sleep $RANDOM_SLEEP_TIME

    - name: Release lock
      run: |
        echo "Releasing lock..."
        git pull
        RANDOM_SLEEP_TIME=$((RANDOM % 46 + 15))
        echo "Sleeping for $RANDOM_SLEEP_TIME seconds..."
        sleep $RANDOM_SLEEP_TIME
        git pull
        git rm .gitlock
        git commit -m "Releasing lock by run $GITHUB_RUN_ID"
        git push origin main

  periodic-check:
    runs-on: ubuntu-latest
    steps:
    - name: Periodically check and trigger the next workflow
      run: |
        while true; do
          # Check the number of running workflows
          sleep 120
          RUNNING_WORKFLOWS=$(curl -s -H "Authorization: token ${{ secrets.GITHUB_TOKEN }}" \\
                                  "https://api.github.com/repos/${{ github.repository }}/actions/runs?status=in_progress" \\
                                  | jq '.workflow_runs | length')
          echo "Number of running workflows: $RUNNING_WORKFLOWS"

          if [ "$RUNNING_WORKFLOWS" -lt 20 ]; then
            # Trigger the next workflow
            echo "Triggering next workflow..."
            curl -X POST \\
            -H "Authorization: token ${{ secrets.GITHUB_TOKEN }}" \\
            -H "Accept: application/vnd.github.v3+json" \\
            https://api.github.com/repos/${{ github.repository }}/actions/workflows/{next_workflow}.yml/dispatches \\
            -d '{{"ref":"main"}}'
            break
          else
            echo "Waiting for available workflow slots..."
            sleep 60  # Check every 60 seconds
          fi
        done
"""

def generate_workflows(store_numbers_file, first_workflow_name="workflow_2_to_3"):
    # Read the store numbers from the file
    with open(store_numbers_file, 'r') as f:
        store_numbers = [line.strip() for line in f.readlines()]

    # Split the store numbers into batches of 2
    total_store_numbers = len(store_numbers)
    for i in range(0, total_store_numbers, 2):
        batch = store_numbers[i:i+2]
        first_number = batch[0]
        last_number = batch[-1]
        store_numbers_str = ' '.join(batch)

        # Determine the next workflow's first and last numbers
        if i + 2 < total_store_numbers:
            next_first_number = store_numbers[i+2]
            next_last_number = store_numbers[min(i+4-1, total_store_numbers-1)]
            next_workflow = f"workflow_{next_first_number}_to_{next_last_number}"
        else:
            # Point back to the first workflow if this is the last batch
            next_workflow = first_workflow_name

        # Generate the content for the workflow file
        workflow_content = workflow_template.format(
            store_numbers=store_numbers_str,
            next_workflow=next_workflow
        )

        # Post-process to correctly format GitHub Actions expressions
        workflow_content = workflow_content.replace("\\${{", "${{").replace("${ secrets.GITHUB_TOKEN }", "${{ secrets.GITHUB_TOKEN }}").replace("${ github.repository }", "${{ github.repository }}")

        # Define the workflow file name
        workflow_filename = f"workflow_{first_number}_to_{last_number}.yml"

        # Save the workflow file
        with open(workflow_filename, 'w') as f:
            f.write(workflow_content)

        print(f"Generated workflow: {workflow_filename}")

if __name__ == "__main__":
    # Specify the path to the store numbers file
    store_numbers_file = 'kfc_stores.txt'  # Replace with your actual file path
    generate_workflows(store_numbers_file)