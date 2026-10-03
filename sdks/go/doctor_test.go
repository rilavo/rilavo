package rilavo

import (
	"os"
	"testing"
)

func TestDoctor(t *testing.T) {
	// Test offline
	result := RunDoctor(false)
	if !result.OK {
		t.Errorf("Expected OK=true, got false")
	}
	for _, c := range result.Checks {
		if !c.OK {
			t.Errorf("Check %s failed: %s", c.Name, c.Message)
		}
	}

	// Test online (no Redis configured)
	os.Unsetenv("RILAVO_REDIS_URL")
	result = RunDoctor(true)
	if !result.OK {
		t.Errorf("Expected OK=true for online with no Redis, got false")
	}

	// Check Redis check was added
	found := false
	for _, c := range result.Checks {
		if c.Name == "Redis nonce cache" {
			found = true
			if !c.OK {
				t.Errorf("Redis check should be OK when not configured: %s", c.Message)
			}
			break
		}
	}
	if !found {
		t.Errorf("Redis nonce cache check not found in online checks")
	}
}
