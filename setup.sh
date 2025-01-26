#!/bin/bash

# GitHub repo details
GITHUB_USER="juniorsir"  # Replace with your GitHub username
GITHUB_REPO="TSecureD"      # Replace with your repository name
LOCAL_VERSION="1.0.0"        # Current version of the tool

# Function to fetch the latest version from version.json
function fetch_latest_version() {
    echo "Checking for updates..."
    latest_version=$(curl -s "https://raw.githubusercontent.com/$GITHUB_USER/$GITHUB_REPO/main/version.json" | grep -Po '"version": "\K.*?(?=")')

    if [[ -z "$latest_version" ]]; then
        echo "Unable to fetch the latest version. Please ensure you have internet connectivity."
        return 1
    fi

    echo "Local Version: $LOCAL_VERSION"
    echo "Latest Version: $latest_version"

    if [[ "$latest_version" != "$LOCAL_VERSION" ]]; then
        echo "An update is available! Do you want to update now? (y/n)"
        read -p "Choice: " choice
        if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
            update_tool
        else
            echo "Skipping update. You are running an older version."
        fi
    else
        echo "You are already using the latest version."
    fi
}

# Function to update the tool
function update_tool() {
    echo "Updating the tool..."
    git clone --depth 1 "https://github.com/$GITHUB_USER/$GITHUB_REPO" /tmp/$GITHUB_REPO
    cp -r /tmp/$GITHUB_REPO/* .
    rm -rf /tmp/$GITHUB_REPO
    echo "Tool updated to the latest version!"
    echo "Restart the tool to apply the update."
    exit 0
}

# Main script functionality
function start_shell() {
    echo "Welcome to the Advanced Termux Shell!"
    echo "Choose an option:"
    echo "1. Client Device (Configure Telegram Bot)"
    echo "2. Control Voice (Enter Unique ID)"
    read -p "Enter your choice (1 or 2): " choice

    if [[ "$choice" == "1" ]]; then
        configure_bot
    elif [[ "$choice" == "2" ]]; then
        control_bot
    else
        echo "Invalid option. Exiting..."
    fi
}

# Configure Telegram bot
function configure_bot() {
    read -p "Enter the Telegram Bot Token: " bot_token

    if [[ ${#bot_token} -ge 40 ]]; then
        unique_id=$(uuidgen)
        echo "Bot token configured successfully!"
        echo "Your Unique ID: $unique_id"
        echo "Enter this Unique ID in your Telegram bot to verify the connection."

        # Save configuration
        echo "$bot_token" > bot_token.txt
        echo "$unique_id" > unique_id.txt
        echo "You can now start the Python bot script to interact with Telegram."
    else
        echo "Invalid bot token. Please try again."
        exit 1
    fi
}

# Control bot features
function control_bot() {
    read -p "Enter your Unique ID: " entered_id

    if [[ -f "unique_id.txt" ]] && [[ "$(cat unique_id.txt)" == "$entered_id" ]]; then
        echo "Verification successful!"
        echo "Run the Python bot script to control features through Telegram."
    else
        echo "Invalid Unique ID. Access denied."
        exit 1
    fi
}

# Check for updates before starting the main functionality
fetch_latest_version

# Start the tool
start_shell
