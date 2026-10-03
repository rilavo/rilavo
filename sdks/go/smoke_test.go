package rilavo

import "testing"

func TestRunSmoke(t *testing.T) {
	result := RunSmoke()
	if !result.OK {
		t.Fatalf("RunSmoke() OK = false, want true")
	}
	if len(result.Steps) < 4 {
		t.Fatalf("RunSmoke() steps = %d, want at least 4", len(result.Steps))
	}
	// Check for expected step patterns
	stepStr := ""
	for _, s := range result.Steps {
		if len(stepStr) > 0 {
			stepStr += " "
		}
		stepStr += s
	}
	expectedPatterns := []string{
		"issue: OK",
		"verify accept",
		"scope mismatch rejected",
		"wrong audience rejected",
	}
	for _, pattern := range expectedPatterns {
		found := false
		for _, step := range result.Steps {
			if contains(step, pattern) {
				found = true
				break
			}
		}
		if !found {
			t.Errorf("RunSmoke() missing expected step pattern: %s", pattern)
		}
	}
}

func TestRunSmokeReturnsStructuredResult(t *testing.T) {
	result := RunSmoke()
	if !result.OK {
		t.Fatal("OK should be true")
	}
	if len(result.Steps) == 0 {
		t.Fatal("Steps should not be empty")
	}
	for _, step := range result.Steps {
		if step == "" {
			t.Fatal("Step should not be empty string")
		}
	}
}

func contains(s, substr string) bool {
	for i := 0; i <= len(s)-len(substr); i++ {
		if s[i:i+len(substr)] == substr {
			return true
		}
	}
	return false
}