"""
Comprehensive tests for the Mergington High School Activities API.
Tests are organized using the AAA pattern (Arrange-Act-Assert).
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """
        ARRANGE: Client ready
        ACT: GET /activities
        ASSERT: Returns 200 with all 9 activities
        """
        # ACT
        response = client.get("/activities")
        
        # ASSERT
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == 9
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities
    
    def test_get_activities_correct_structure(self, client):
        """
        ARRANGE: Client ready
        ACT: GET /activities
        ASSERT: Each activity has correct schema
        """
        # ACT
        response = client.get("/activities")
        activities = response.json()
        
        # ASSERT
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)
    
    def test_get_activities_participants_list(self, client):
        """
        ARRANGE: Client ready
        ACT: GET /activities
        ASSERT: Participants list is correctly populated
        """
        # ACT
        response = client.get("/activities")
        activities = response.json()
        
        # ASSERT
        chess_club = activities["Chess Club"]
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client):
        """
        ARRANGE: Valid activity, new email not yet signed up
        ACT: POST signup with email
        ASSERT: 200 response, participant added
        """
        # ARRANGE
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # ASSERT
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        
        # Verify participant was added
        final_response = client.get("/activities")
        final_count = len(final_response.json()[activity_name]["participants"])
        assert final_count == initial_count + 1
        assert email in final_response.json()[activity_name]["participants"]
    
    def test_signup_duplicate_email_same_activity(self, client):
        """
        ARRANGE: Email already signed up for activity
        ACT: Try to signup with same email
        ASSERT: 400 error, detail says "already signed up"
        """
        # ARRANGE
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already a participant
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # ASSERT
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_invalid_activity(self, client):
        """
        ARRANGE: Non-existent activity name
        ACT: Try to signup for invalid activity
        ASSERT: 404 error, detail says "Activity not found"
        """
        # ARRANGE
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # ASSERT
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_different_email_same_activity_allowed(self, client):
        """
        ARRANGE: Activity already has a participant
        ACT: Signup with different email
        ASSERT: 200, both emails now in participants
        """
        # ARRANGE
        activity_name = "Programming Class"
        email1 = "emma@mergington.edu"  # Existing
        email2 = "newemail@mergington.edu"  # New
        
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[activity_name]["participants"]
        assert email1 in initial_participants
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup?email={email2}"
        )
        
        # ASSERT
        assert response.status_code == 200
        final_response = client.get("/activities")
        final_participants = final_response.json()[activity_name]["participants"]
        assert email1 in final_participants
        assert email2 in final_participants
        assert len(final_participants) == len(initial_participants) + 1
    
    def test_signup_case_sensitive_email(self, client):
        """
        ARRANGE: Signup with different case variant of existing email
        ACT: Signup with UPPERCASE variant
        ASSERT: Treated as new email (case-sensitive comparison)
        """
        # ARRANGE
        activity_name = "Debate Club"
        email_lowercase = "lucas@mergington.edu"  # Existing
        email_uppercase = "LUCAS@MERGINGTON.EDU"  # Different case
        
        # ACT - first attempt with uppercase should succeed (treated as new)
        response = client.post(
            f"/activities/{activity_name}/signup?email={email_uppercase}"
        )
        
        # ASSERT - succeeds because email comparison is case-sensitive
        assert response.status_code == 200
        final_response = client.get("/activities")
        participants = final_response.json()[activity_name]["participants"]
        assert email_lowercase in participants
        assert email_uppercase in participants


class TestDeleteParticipant:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint"""
    
    def test_delete_participant_success(self, client):
        """
        ARRANGE: Activity with known participant
        ACT: DELETE participant
        ASSERT: 200, participant removed from list
        """
        # ARRANGE
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Known participant
        
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])
        assert email in initial_response.json()[activity_name]["participants"]
        
        # ACT
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # ASSERT
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]
        
        # Verify participant was removed
        final_response = client.get("/activities")
        final_count = len(final_response.json()[activity_name]["participants"])
        assert final_count == initial_count - 1
        assert email not in final_response.json()[activity_name]["participants"]
    
    def test_delete_participant_not_found(self, client):
        """
        ARRANGE: Email not in activity participants
        ACT: Try to delete non-existent participant
        ASSERT: 404 error, detail says "Participant not found"
        """
        # ARRANGE
        activity_name = "Chess Club"
        email = "nonexistent@mergington.edu"
        
        # ACT
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # ASSERT
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]
    
    def test_delete_from_invalid_activity(self, client):
        """
        ARRANGE: Non-existent activity name
        ACT: Try to delete from invalid activity
        ASSERT: 404 error, detail says "Activity not found"
        """
        # ARRANGE
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # ACT
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # ASSERT
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_delete_last_participant(self, client):
        """
        ARRANGE: Activity with only one participant
        ACT: Delete that participant
        ASSERT: 200, participant removed, list now empty
        """
        # ARRANGE
        activity_name = "Music Band"
        # Music Band has only "mia@mergington.edu"
        email = "mia@mergington.edu"
        
        initial_response = client.get("/activities")
        assert len(initial_response.json()[activity_name]["participants"]) == 1
        
        # ACT
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # ASSERT
        assert response.status_code == 200
        final_response = client.get("/activities")
        assert len(final_response.json()[activity_name]["participants"]) == 0
    

class TestIntegration:
    """Integration tests for signup and delete operations"""
    
    def test_signup_updates_participant_count(self, client):
        """
        ARRANGE: Activity with N participants
        ACT: Signup new participant, fetch activities
        ASSERT: Participant count increases by 1, availability decreases
        """
        # ARRANGE
        activity_name = "Tennis Club"
        email = "newemail@mergington.edu"
        
        initial_response = client.get("/activities")
        initial_participants = len(initial_response.json()[activity_name]["participants"])
        initial_spots = initial_response.json()[activity_name]["max_participants"] - initial_participants
        
        # ACT
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # ASSERT
        final_response = client.get("/activities")
        final_participants = len(final_response.json()[activity_name]["participants"])
        final_spots = final_response.json()[activity_name]["max_participants"] - final_participants
        
        assert final_participants == initial_participants + 1
        assert final_spots == initial_spots - 1
    
    def test_delete_frees_spot(self, client):
        """
        ARRANGE: Activity with participant
        ACT: Delete participant
        ASSERT: Spots available increases
        """
        # ARRANGE
        activity_name = "Basketball Team"
        email = "alex@mergington.edu"
        
        initial_response = client.get("/activities")
        initial_participants = len(initial_response.json()[activity_name]["participants"])
        initial_spots = initial_response.json()[activity_name]["max_participants"] - initial_participants
        
        # ACT
        client.delete(f"/activities/{activity_name}/participants/{email}")
        
        # ASSERT
        final_response = client.get("/activities")
        final_participants = len(final_response.json()[activity_name]["participants"])
        final_spots = final_response.json()[activity_name]["max_participants"] - final_participants
        
        assert final_participants == initial_participants - 1
        assert final_spots == initial_spots + 1
    
    def test_signup_delete_signup_sequence(self, client):
        """
        ARRANGE: Activity with participants
        ACT: Signup email → Delete email → Signup different email
        ASSERT: Final state correct, all operations succeeded
        """
        # ARRANGE
        activity_name = "Art Studio"
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])
        
        # ACT & ASSERT - Signup email1
        response1 = client.post(f"/activities/{activity_name}/signup?email={email1}")
        assert response1.status_code == 200
        
        check1 = client.get("/activities")
        assert email1 in check1.json()[activity_name]["participants"]
        assert len(check1.json()[activity_name]["participants"]) == initial_count + 1
        
        # ACT & ASSERT - Delete email1
        response2 = client.delete(
            f"/activities/{activity_name}/participants/{email1}"
        )
        assert response2.status_code == 200
        
        check2 = client.get("/activities")
        assert email1 not in check2.json()[activity_name]["participants"]
        assert len(check2.json()[activity_name]["participants"]) == initial_count
        
        # ACT & ASSERT - Signup email2
        response3 = client.post(f"/activities/{activity_name}/signup?email={email2}")
        assert response3.status_code == 200
        
        check3 = client.get("/activities")
        assert email2 in check3.json()[activity_name]["participants"]
        assert email1 not in check3.json()[activity_name]["participants"]
        assert len(check3.json()[activity_name]["participants"]) == initial_count + 1
    
    def test_multiple_signups_multiple_deletes(self, client):
        """
        ARRANGE: Activity with some participants
        ACT: Signup 3 emails, delete 2, signup 1 more
        ASSERT: Final list has original + 2 new
        """
        # ARRANGE
        activity_name = "Gym Class"
        emails_to_add = ["add1@test.edu", "add2@test.edu", "add3@test.edu"]
        emails_to_remove = ["add1@test.edu", "add2@test.edu"]
        email_final = "add4@test.edu"
        
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[activity_name]["participants"].copy()
        
        # ACT - Signup 3
        for email in emails_to_add:
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == 200
        
        # ACT - Delete 2
        for email in emails_to_remove:
            response = client.delete(f"/activities/{activity_name}/participants/{email}")
            assert response.status_code == 200
        
        # ACT - Signup 1 more
        response = client.post(f"/activities/{activity_name}/signup?email={email_final}")
        assert response.status_code == 200
        
        # ASSERT
        final_response = client.get("/activities")
        final_participants = final_response.json()[activity_name]["participants"]
        
        # Should have original + add3 + add4 (add1 and add2 removed)
        expected_new = ["add3@test.edu", "add4@test.edu"]
        for email in initial_participants:
            assert email in final_participants
        for email in expected_new:
            assert email in final_participants
        
        # add1 and add2 should not be there
        assert "add1@test.edu" not in final_participants
        assert "add2@test.edu" not in final_participants
