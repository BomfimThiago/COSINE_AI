from __future__ import annotations

import requests
from .linear import get_linear_api_key, get_linear_api_url
import json
from typing import Any
from .logging_utils import network_guard, log_error

class LinearAPI:
    def __init__(self):
        self.api_key = get_linear_api_key()
        self.api_url = get_linear_api_url()
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
    @network_guard(max_retries=3, backoff_factor=0.75)
    def _safe_post(self, *args, **kwargs):
        return requests.post(*args, **kwargs)

    def add_comment(self, ticket_id: str, body: str) -> dict:
        """
        Adds a comment to the specified Linear ticket (issue).
        Returns the API response dict.
        """
        print(f"[Linear] Adding comment to ticket {ticket_id}: {body[:120]}...")
        mutation = """
        mutation IssueCommentCreate($input: CommentCreateInput!) {
          commentCreate(input: $input) {
            success
            comment {
              id
              body
              createdAt
            }
          }
        }
        """
        variables = {
            "input": {
                "issueId": ticket_id,
                "body": body
            }
        }
        try:
            response = self._safe_post(
                self.api_url,
                headers=self.headers,
                json={"query": mutation, "variables": variables},
            )
            print(f"[Linear] add_comment response: {response.text[:500]}")
            return response.json().get("data", {}).get("commentCreate", {})
        except Exception as e:
            log_error(
                f"Failed to add comment to Linear ticket {ticket_id}: {e}",
                extra={"ticket_id": ticket_id, "body": body[:100]},
                alert=True
            )
            return {"success": False, "error": str(e)}

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
              description
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
        try:
            response = self._safe_post(
                self.api_url,
                headers=self.headers,
                json={"query": mutation, "variables": variables},
            )
            print(f"[Linear] Response: {response.text[:500]}")
            data = response.json()
            return data["data"]["issueCreate"]
        except Exception as e:
            log_error(
                f"Failed to create Linear ticket: {e}",
                extra={"team_id": team_id, "title": title, "assignee_id": assignee_id, "label_ids": label_ids},
                alert=True
            )
            return {"success": False, "error": str(e)}

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
        try:
            response = self._safe_post(
                self.api_url,
                headers=self.headers,
                json={"query": query},
            )
            print(f"[Linear] Response: {response.text[:500]}")
            data = response.json()
            teams = data["data"]["teams"]["nodes"]
            for team in teams:
                if team["key"] == team_key:
                    return team
            return None
        except Exception as e:
            log_error(
                f"Failed to get Linear team by key: {e}",
                extra={"team_key": team_key},
                alert=True
            )
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
        try:
            response = self._safe_post(
                self.api_url,
                headers=self.headers,
                json={"query": query, "variables": variables},
            )
            print(f"[Linear] Response: {response.text[:500]}")
            data = response.json()
            nodes = data["data"]["users"]["nodes"]
            return nodes[0] if nodes else None
        except Exception as e:
            log_error(
                f"Failed to get Linear user by email: {e}",
                extra={"email": email},
                alert=True
            )
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
        try:
            response = self.__raw_query(query, {"id": team_id})
            print(f"[Linear] get_team_members response: {response}")
            return response.get("data", {}).get("team", {}).get("members", {}).get("nodes", [])
        except Exception as e:
            log_error(
                f"Failed to fetch Linear team members: {e}",
                extra={"team_id": team_id},
                alert=True
            )
            return []

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
        try:
            response = self.__raw_query(query)
            print(f"[Linear] get_labels response: {response}")
            return response.get("data", {}).get("issueLabels", {}).get("nodes", [])
        except Exception as e:
            log_error(
                f"Failed to fetch Linear labels: {e}",
                alert=True
            )
            return []

    def get_ticket(self, ticket_id: str) -> dict | None:
        """
        Fetches a single ticket (issue) by its Linear ID.
        Returns the issue data dict, or None if not found/error.
        """
        print(f"[Linear] Fetching ticket by id: {ticket_id}")
        query = """
        query IssueById($id: String!) {
          issue(id: $id) {
            id
            identifier
            title
            description
            url
            labels { nodes { id name } }
            assignee { id name email }
            state { id name type }
            team { id name key }
            createdAt
            updatedAt
            priority
            comments { nodes { id body createdAt } }
          }
        }
        """
        variables = {"id": ticket_id}
        try:
            response = self.__raw_query(query, variables)
            print(f"[Linear] get_ticket response: {response}")
            return response.get("data", {}).get("issue", None)
        except Exception as e:
            log_error(
                f"Failed to fetch Linear ticket: {e}",
                extra={"ticket_id": ticket_id},
                alert=True
            )
            return None

    def __raw_query(self, query, variables=None):
        print(f"[Linear] __raw_query: query={query}, variables={variables}")
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        try:
            response = self._safe_post(
                self.api_url,
                headers=self.headers,
                json=payload,
            )
            print(f"[Linear] __raw_query response: {response.text[:500]}")
            return response.json()
        except Exception as e:
            log_error(
                f"Failed raw_query to Linear: {e}",
                extra={"query": query, "variables": variables},
                alert=True
            )
            return {"error": str(e)} 