# :one: Milestone 1

## ToolShare :iphone: :hammer:
> Version 0.0.1

### Product Description

ToolShare is a community-driven platform that lets you rent tools like drills, lawn mowers, and more from your neighbors. Why buy expensive equipment when you can borrow it locally? Easily browse available tools, rent what you need, and save money while fostering a sense of community. Share your own tools, earn extra cash, and help reduce waste by making resources accessible to everyone around you.   

With ToolShare, renting and sharing tools is simple:

- **Rent out**: List your tool with a picture, brand, age, skill level required, and set a price per day.
- **Rent**: Browse available tools, select what you need, specify how long you want it, and share your experience level.
- **What if things break?**: We recommend signing up for our insurance. If a tool breaks, we’ll replace it and ensure the owner gets a new one.

**Easy!!!**

### Why use the Cloud?

Running ToolShare in the cloud is ideal because it allows easy scaling as the platform grows and ensures availability during high demand. The cloud also provides built-in security and backup options, making it easier to manage without the need for extra infrastructure. This flexibility is important for a student project with limited resources.



---

## Repository Setup Guide

### 1. Repository Creation
1. Navigate to [GitHub](https://github.com/) and log in.
2. Click on the **+** icon in the top-right corner and select **New repository**.
3. Fill in the details:
   - **Repository name**: (e.g., `toolshare-repo`)
   - **Description**: A brief description of the repository.
   - Select **Public** or **Private** according to your preference.
   - Check the box to initialize the repository with a **README** file.

### 2. SSH Key Setup

To securely interact with GitHub using SSH, follow these steps:

1. **Generate a new SSH key**:
    ```bash
    ssh-keygen -t ed25519 -C "your_email@example.com"
    ```
    - Follow the prompts to save the key in the default location.
    - Optionally, set a passphrase.

2. **Add SSH key to the ssh-agent**:
    ```bash
    eval "$(ssh-agent -s)"
    ssh-add ~/.ssh/id_ed25519
    ```

3. **Add SSH key to GitHub**:
    - Copy the SSH public key to your clipboard:
      ```bash
      cat ~/.ssh/id_ed25519.pub
      ```
    - Go to your GitHub profile → **Settings** → **SSH and GPG keys** → **New SSH Key**.
    - Paste your public key and give it a title, then click **Add SSH key**.

4. **Clone the repository using SSH**:
    ```bash
    git clone git@github.com:your-username/toolshare-repo.git
    ```

### 3. Setting up a License

1. Navigate to your repository on GitHub.
2. Click the **Add file** dropdown and select **Create new file**.
3. Name the file `LICENSE`.
4. In the editor, GitHub offers an option to choose a template for the license. Select a license that best suits your project (e.g., MIT License).
5. Click **Commit new file**.

### 4. Committing and Pushing Changes

1. Make changes to your local repository.
2. To stage changes:
    ```bash
    git add .
    ```
3. To commit changes:
    ```bash
    git commit -m "Initial commit"
    ```
4. To push changes:
    ```bash
    git push origin main
    ```


