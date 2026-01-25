#!/usr/bin/env python3
"""Load testing script for AI-IMUTIS backend using Locust."""
from locust import HttpUser, task, between, events
import random
from datetime import datetime, timedelta

CITIES = ["douala", "yaounde", "buea"]
ATTRACTIONS = {
    "douala": ["douala-waterfront", "douala-bonanjo", "douala-maritime-museum"],
    "yaounde": ["yaounde-mfoundi-market", "yaounde-national-museum", "yaounde-mount-febe-viewpoint"],
    "buea": ["buea-botanical-garden", "buea-mount-cameroon", "buea-colonial-architecture-tour"],
}


class TravelUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Initialize user session."""
        self.user_token = "demo-token-" + str(random.randint(10000, 99999))
        self.headers = {"Authorization": f"Bearer {self.user_token}"}
    
    @task(3)
    def list_travels(self):
        """List all travel routes."""
        self.client.get("/api/travels", headers=self.headers)
    
    @task(2)
    def search_travels(self):
        """Search for travel routes."""
        origin = random.choice(CITIES)
        destination = random.choice([c for c in CITIES if c != origin])
        self.client.post(
            "/api/travels/search",
            headers=self.headers,
            json={
                "origin": origin,
                "destination": destination,
                "departure_date": (datetime.utcnow() + timedelta(days=random.randint(1, 7))).isoformat(),
                "passengers": random.randint(1, 4),
            },
        )
    
    @task(1)
    def estimate_departure(self):
        """Estimate optimal departure window."""
        self.client.post(
            "/api/ai/estimate-departure",
            headers=self.headers,
            json={
                "route_id": "route-yaounde-douala-morning",
                "current_time": datetime.utcnow().isoformat(),
                "user_preferences": {"comfort": "high"},
            },
        )
    
    @task(2)
    def list_cities(self):
        """List all cities."""
        self.client.get("/api/cities", headers=self.headers)
    
    @task(2)
    def list_attractions(self):
        """List attractions in a city."""
        city = random.choice(CITIES)
        self.client.get(f"/api/cities/{city}/attractions", headers=self.headers)
    
    @task(1)
    def recommend_attractions(self):
        """Get attraction recommendations."""
        city = random.choice(CITIES)
        self.client.post(
            "/api/ai/recommend-attractions",
            headers=self.headers,
            json={
                "city_id": city,
                "interests": random.sample(["nature", "culture", "history"], k=random.randint(1, 2)),
                "max_results": 5,
            },
        )
    
    @task(1)
    def traffic_prediction(self):
        """Get traffic prediction for a route."""
        self.client.get(
            "/api/ai/traffic-prediction/route-yaounde-douala-morning",
            headers=self.headers,
        )
    
    @task(1)
    def tourism_suggestions(self):
        """Get tourism suggestions for a city."""
        city = random.choice(CITIES)
        self.client.get(f"/api/ai/tourism-suggestions/{city}", headers=self.headers)


class AdminUser(HttpUser):
    """Simulates admin operations."""
    wait_time = between(2, 5)
    
    def on_start(self):
        """Initialize with admin token."""
        self.user_token = "admin-token-" + str(random.randint(10000, 99999)) + "-admin"
        self.headers = {"Authorization": f"Bearer {self.user_token}"}
    
    @task(1)
    def get_profile(self):
        """Retrieve user profile."""
        self.client.get("/api/users/profile", headers=self.headers)
    
    @task(1)
    def list_sessions(self):
        """List device sessions."""
        self.client.get("/api/users/sessions", headers=self.headers)
    
    @task(1)
    def list_notifications(self):
        """List notifications."""
        self.client.get("/api/notifications", headers=self.headers)


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("\n=== Load Test Started ===")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("\n=== Load Test Finished ===")
    print(f"Total requests: {environment.stats.total.num_requests}")
    print(f"Total failures: {environment.stats.total.num_failures}")
    print(f"Average response time: {environment.stats.total.avg_response_time:.0f}ms")
    print(f"95th percentile: {environment.stats.total.get_response_time_percentile(0.95):.0f}ms")
    print(f"99th percentile: {environment.stats.total.get_response_time_percentile(0.99):.0f}ms")
