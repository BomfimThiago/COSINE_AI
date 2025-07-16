from github import Github, GithubException
import os

class GitHubAPI:
    def __init__(self):
        token = os.environ.get("GITHUB_TOKEN")
        repo_name = os.environ.get("GITHUB_REPO") # e.g., "your_username/your_repo"

        if not token or not repo_name:
            raise ValueError("GITHUB_TOKEN and GITHUB_REPO environment variables must be set.")
            
        self.gh = Github(token)
        self.repo = self.gh.get_repo(repo_name)

    def create_pr(self, ticket_id, ticket_title, file_path, file_content, base_branch="main"):
        try:
            # 1. Create a new branch from the base branch
            branch_name = f"feature/{ticket_id}-{ticket_title.lower().replace(' ', '-')[:20]}"
            print(f"[GitHub] Creating branch: {branch_name}")
            
            source = self.repo.get_branch(base_branch)
            self.repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=source.commit.sha)

            # 2. Create or update the file in the new branch
            commit_message = f"feat({ticket_id}): {ticket_title}"
            print(f"[GitHub] Creating file '{file_path}' in branch '{branch_name}'")
            
            try:
                # Check if file exists to update it
                contents = self.repo.get_contents(file_path, ref=branch_name)
                self.repo.update_file(contents.path, commit_message, file_content, contents.sha, branch=branch_name)
                print(f"[GitHub] Updated existing file: {file_path}")
            except GithubException as e:
                if e.status == 404:
                    # File does not exist, create it
                    self.repo.create_file(file_path, commit_message, file_content, branch=branch_name)
                    print(f"[GitHub] Created new file: {file_path}")
                else:
                    raise
            
            # 3. Create the pull request
            pr_title = f"feat({ticket_id}): {ticket_title}"
            pr_body = f"### Ticket: {ticket_id}\n\nThis PR implements the solution for the ticket: **{ticket_title}**."
            print(f"[GitHub] Creating Pull Request: '{pr_title}'")
            
            pr = self.repo.create_pull(
                title=pr_title,
                body=pr_body,
                head=branch_name,
                base=base_branch
            )
            
            print(f"[GitHub] Successfully created PR: {pr.html_url}")
            return {"success": True, "pr_url": pr.html_url}

        except GithubException as e:
            error_message = f"GitHub API error: {e.data.get('message', str(e))}"
            print(f"[GitHub] {error_message}")
            return {"success": False, "error": error_message}
        except Exception as e:
            print(f"[GitHub] An unexpected error occurred: {str(e)}")
            return {"success": False, "error": str(e)}

