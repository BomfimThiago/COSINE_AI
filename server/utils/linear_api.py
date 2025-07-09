import requests
from .linear import get_linear_api_key, get_linear_api_url

class LinearAPI:
    def __init__(self):
        self.api_key = get_linear_api_key()
        self.api_url = get_linear_api_url()
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def create_ticket(self, team_id, title, description, assignee_id=None):
        print(f"[Linear] Creating ticket: team_id={team_id}, title={title}, assignee_id={assignee_id}")
        mutation = """
        mutation IssueCreate($input: IssueCreateInput!) {
          issueCreate(input: $input) {
            success
            issue {
              id
              identifier
              title
              assignee { id name email }
              url
            }
          }
        }
        """
        variables = {
            "input": {
                "teamId": team_id,
                "title": title,
                "description": description,
            }
        }
        if assignee_id:
            variables["input"]["assigneeId"] = assignee_id
        print(f"[Linear] Payload: {{'query': mutation, 'variables': {variables}}}")
        response = requests.post(
            self.api_url,
            headers=self.headers,
            json={"query": mutation, "variables": variables},
        )
        print(f"[Linear] Response: {response.text[:500]}")
        try:
            data = response.json()
            return data["data"]["issueCreate"]
        except Exception:
            return {"success": False, "error": response.text}

    def get_team_id_by_key(self, team_key):
        print(f"[Linear] Looking up team by key: {team_key}")
        query = """
        query {
          teams {
            nodes {
              id
              name
              key
            }
          }
        }
        """
        print(f"[Linear] Payload: {{'query': query}}")
        response = requests.post(
            self.api_url,
            headers=self.headers,
            json={"query": query},
        )
        print(f"[Linear] Response: {response.text[:500]}")
        try:
            data = response.json()
            teams = data["data"]["teams"]["nodes"]
            for team in teams:
                if team["key"] == team_key:
                    return team
            return None
        except Exception:
            return None

    def get_user_id_by_email(self, email):
        print(f"[Linear] Looking up user by email: {email}")
        query = """
        query UserByEmail($email: String!) {
          users(filter: {email: {eq: $email}}) {
            nodes {
              id
              name
              email
            }
          }
        }
        """
        variables = {"email": email}
        print(f"[Linear] Payload: {{'query': query, 'variables': {variables}}}")
        response = requests.post(
            self.api_url,
            headers=self.headers,
            json={"query": query, "variables": variables},
        )
        print(f"[Linear] Response: {response.text[:500]}")
        try:
            data = response.json()
            nodes = data["data"]["users"]["nodes"]
            return nodes[0] if nodes else None
        except Exception:
            return None 