#!/bin/bash

# Step 0: Delete skill.zip if it already exists
echo "Checking if skill.zip already exists..."
if [ -f skill.zip ]; then
  echo "Found existing skill.zip. Deleting it..."
  rm skill.zip || { echo "Failed to delete existing skill.zip"; exit 1; }
else
  echo "No existing skill.zip found."
fi

# Step 1: Change to the directory containing site-packages
echo "Changing directory to .venv/Lib/site-packages/"
cd .venv/Lib/site-packages/ || { echo "Failed to cd into .venv/Lib/site-packages/"; exit 1; }

# Step 2: Zip the contents of the directory into skill.zip
echo "Zipping the contents of site-packages into skill.zip..."
zip -r ../../../skill.zip . || { echo "Failed to zip site-packages. See zip_output.log for details."; exit 1; }

# Step 3: Change back to the root directory
echo "Changing back to the root directory..."
cd ../../../lambda/ || { echo "Failed to cd back to the root directory"; exit 1; }

# Step 4: Add the lambda_function.py to the zip file
echo "Adding lambda_function.py to skill.zip..."
zip ../skill.zip lambda_function.py || { echo "Failed to add lambda_function.py"; exit 1; }
echo "Script completed successfully. The skill.zip is ready."