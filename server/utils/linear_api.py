import requests
from .linear import get_linear_api_key, get_linear_api_url
import json

class LinearAPI:
    def __init__(self):
        self.api_key = get_linear_api_key()
        self.api_url = get_linear_api_url()
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def create_ticket(self, team_id, title, description, assignee_id=None, label_ids=None):
        print(f"[Linear] Creating ticket: team_id={team_id}, title={title}, assignee_id={assignee_id}, label_ids={label_ids}")
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
              labels { nodes { id name } }
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
        if label_ids:
            print(f"[Linear] label_ids type: {type(label_ids)}, value: {label_ids}")
            if isinstance(label_ids, str):
                label_ids = [label_ids]
            elif isinstance(label_ids, list):
                label_ids = [str(lid) for lid in label_ids]
            variables["input"]["labelIds"] = label_ids
        print(f"[Linear] Final variables for mutation: {variables}")
        print(f"[Linear] Payload: {json.dumps({'query': mutation, 'variables': variables}, indent=2)}")
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

    def get_team_members(self, team_id):
        """
        Fetches all members for a given team ID.
        """
        print(f"[Linear] Fetching members for team_id='{team_id}'")
        query = """
        query TeamMembers($id: String!) {
            team(id: $id) {
                members {
                    nodes {
                        id
                        name
                        email
                    }
                }
            }
        }
        """
        response = self.__raw_query(query, {"id": team_id})
        print(f"[Linear] get_team_members response: {response}")
        return response.get("data", {}).get("team", {}).get("members", {}).get("nodes", [])

    def get_labels(self):
        print(f"[Linear] Fetching all labels")
        query = """
        query {
          issueLabels {
            nodes {
              id
              name
              color
            }
          }
        }
        """
        response = self.__raw_query(query)
        print(f"[Linear] get_labels response: {response}")
        return response.get("data", {}).get("issueLabels", {}).get("nodes", [])

    def __raw_query(self, query, variables=None):
        print(f"[Linear] __raw_query: query={query}, variables={variables}")
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        response = requests.post(
            self.api_url,
            headers=self.headers,
            json=payload,
        )
        print(f"[Linear] __raw_query response: {response.text[:500]}")
        try:
            return response.json()
        except Exception:
            return {"error": response.text} 